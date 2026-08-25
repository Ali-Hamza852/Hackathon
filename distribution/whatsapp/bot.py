import hashlib
import hmac
import json
import logging
import re

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.models import BroadcastLog, BroadcastStatus, Score, Subscriber, SubscriberChannel
from app.db.session import get_db
from app.services.subscribers import find_school_by_name, register_subscriber
from app.time_utils import utc_now
from distribution.whatsapp.message_templates import build_bulletin_message

logger = logging.getLogger("saans.distribution.whatsapp")

router = APIRouter()

GRAPH_API_VERSION = "v20.0"
SEND_TIMEOUT_SECONDS = 5.0
SEND_ATTEMPTS = 2
SUBSCRIBE_PATTERN = re.compile(r"subscribe\s+(.+)", re.IGNORECASE)


@router.get("/whatsapp/webhook")
def verify_webhook(
    hub_mode: str = Query(default="", alias="hub.mode"),
    hub_verify_token: str = Query(default="", alias="hub.verify_token"),
    hub_challenge: str = Query(default="", alias="hub.challenge"),
    settings: Settings = Depends(get_settings),
) -> PlainTextResponse:
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        return PlainTextResponse(content=hub_challenge)
    raise HTTPException(status_code=403, detail="verification token mismatch")


@router.post("/whatsapp/webhook")
async def receive_webhook(
    request: Request, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)
) -> dict[str, str]:
    try:
        body = await request.body()
        if not _signature_is_valid(body, request.headers.get("x-hub-signature-256"), settings):
            logger.warning("rejected WhatsApp webhook payload with an invalid signature")
            return {"status": "ok"}
        _handle_inbound_payload(db, json.loads(body))
    except Exception:
        logger.exception("failed to process inbound WhatsApp webhook payload")
    return {"status": "ok"}


def _signature_is_valid(body: bytes, header_value: str | None, settings: Settings) -> bool:
    if not settings.whatsapp_app_secret:
        return True
    if not header_value or not header_value.startswith("sha256="):
        return False
    expected = hmac.new(settings.whatsapp_app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header_value.removeprefix("sha256="))


def _handle_inbound_payload(db: Session, payload: dict) -> None:
    sender, text = _extract_message(payload)
    if sender is None or text is None:
        return

    match = SUBSCRIBE_PATTERN.search(text.strip())
    if match is None:
        return

    school_name = match.group(1).strip()
    school = find_school_by_name(db, school_name)
    if school is None:
        logger.info("ignoring WhatsApp subscribe request for unknown school: %s", school_name)
        return

    register_subscriber(
        db,
        channel=SubscriberChannel.whatsapp,
        contact=_normalize_contact(sender),
        school_id=school.id,
    )


def _extract_message(payload: dict) -> tuple[str | None, str | None]:
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for message in change.get("value", {}).get("messages", []):
                sender = message.get("from")
                text = message.get("text", {}).get("body")
                if sender and text:
                    return sender, text
    return None, None


def _normalize_contact(raw_number: str) -> str:
    return raw_number if raw_number.startswith("+") else f"+{raw_number}"


def send_whatsapp_message(to: str, text: str, settings: Settings) -> bool:
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{settings.whatsapp_phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {settings.whatsapp_cloud_api_token}"}
    body = {
        "messaging_product": "whatsapp",
        "to": to.lstrip("+"),
        "type": "text",
        "text": {"body": text},
    }
    for attempt in range(SEND_ATTEMPTS):
        try:
            response = httpx.post(url, json=body, headers=headers, timeout=SEND_TIMEOUT_SECONDS)
            response.raise_for_status()
            return True
        except httpx.HTTPError:
            logger.warning("WhatsApp send attempt %s to %s failed", attempt + 1, to)
    return False


def on_scores_computed(db: Session, scores: list[Score], settings: Settings) -> None:
    if not scores:
        return

    scores_by_school_id = {score.school_id: score for score in scores}
    subscribers = (
        db.query(Subscriber)
        .filter(Subscriber.channel == SubscriberChannel.whatsapp, Subscriber.school_id.isnot(None))
        .all()
    )

    for subscriber in subscribers:
        try:
            _broadcast_to_subscriber(db, subscriber, scores_by_school_id, settings)
        except Exception:
            logger.exception("failed broadcasting bulletin to subscriber %s", subscriber.id)


def _broadcast_to_subscriber(
    db: Session,
    subscriber: Subscriber,
    scores_by_school_id: dict[int, Score],
    settings: Settings,
) -> None:
    score = scores_by_school_id.get(subscriber.school_id)
    if score is None:
        return

    if not settings.whatsapp_configured:
        if not _already_logged(db, subscriber.id, score.id, BroadcastStatus.skipped):
            _log_broadcast(db, subscriber, score, BroadcastStatus.skipped)
        return

    if _already_logged(db, subscriber.id, score.id, BroadcastStatus.sent):
        return

    message = build_bulletin_message(score)
    success = send_whatsapp_message(subscriber.contact, message, settings)
    _log_broadcast(db, subscriber, score, BroadcastStatus.sent if success else BroadcastStatus.failed)


def _already_logged(db: Session, subscriber_id: int, score_id: int, status: BroadcastStatus) -> bool:
    return (
        db.query(BroadcastLog)
        .filter(
            BroadcastLog.subscriber_id == subscriber_id,
            BroadcastLog.score_id == score_id,
            BroadcastLog.status == status,
        )
        .first()
        is not None
    )


def _log_broadcast(db: Session, subscriber: Subscriber, score: Score, status: BroadcastStatus) -> None:
    db.add(
        BroadcastLog(
            subscriber_id=subscriber.id,
            score_id=score.id,
            sent_at=utc_now(),
            status=status,
        )
    )
    db.commit()
