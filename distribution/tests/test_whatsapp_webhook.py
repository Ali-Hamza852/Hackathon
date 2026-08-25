from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.db.models import Subscriber, SubscriberChannel
from app.db.session import get_db
from distribution.whatsapp.bot import router


def _client_for(db_session, verify_token="test-verify"):
    app = FastAPI()
    app.include_router(router)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = lambda: Settings(whatsapp_verify_token=verify_token)
    return TestClient(app)


def test_webhook_verification_echoes_challenge_on_matching_token(db_session):
    client = _client_for(db_session, verify_token="dev-verify")

    response = client.get(
        "/whatsapp/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": "dev-verify", "hub.challenge": "12345"},
    )

    assert response.status_code == 200
    assert response.text == "12345"


def test_webhook_verification_rejects_wrong_token(db_session):
    client = _client_for(db_session, verify_token="dev-verify")

    response = client.get(
        "/whatsapp/webhook",
        params={"hub.mode": "subscribe", "hub.verify_token": "wrong-token", "hub.challenge": "12345"},
    )

    assert response.status_code == 403


def test_webhook_inbound_subscribe_creates_subscriber(db_session, seeded_schools):
    client = _client_for(db_session)
    target_school = seeded_schools[0]
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "923001234567",
                                    "text": {"body": f"subscribe {target_school.name}"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

    response = client.post("/whatsapp/webhook", json=payload)

    assert response.status_code == 200
    subscriber = (
        db_session.query(Subscriber)
        .filter(Subscriber.contact == "+923001234567", Subscriber.channel == SubscriberChannel.whatsapp)
        .first()
    )
    assert subscriber is not None
    assert subscriber.school_id == target_school.id


def test_webhook_inbound_subscribe_with_unknown_school_registers_with_null_school(db_session):
    client = _client_for(db_session)
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {"from": "923005556666", "text": {"body": "SUBSCRIBE Nonexistent Academy"}}
                            ]
                        }
                    }
                ]
            }
        ]
    }

    response = client.post("/whatsapp/webhook", json=payload)

    assert response.status_code == 200
    subscriber = (
        db_session.query(Subscriber).filter(Subscriber.contact == "+923005556666").first()
    )
    assert subscriber is not None
    assert subscriber.school_id is None


def test_webhook_inbound_malformed_payload_still_returns_200(db_session):
    client = _client_for(db_session)

    response = client.post("/whatsapp/webhook", json={"unexpected": "shape"})

    assert response.status_code == 200


def test_webhook_inbound_non_subscribe_message_is_ignored(db_session):
    client = _client_for(db_session)
    payload = {
        "entry": [
            {"changes": [{"value": {"messages": [{"from": "923007778888", "text": {"body": "hello there"}}]}}]}
        ]
    }

    response = client.post("/whatsapp/webhook", json=payload)

    assert response.status_code == 200
    assert db_session.query(Subscriber).filter(Subscriber.contact == "+923007778888").first() is None
