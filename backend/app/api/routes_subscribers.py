from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import School, Subscriber
from app.db.session import get_db
from app.schemas.subscriber import SubscriberCreate, SubscriberOut
from app.time_utils import utc_now

router = APIRouter(tags=["subscribers"])


@router.post("/subscribers", response_model=SubscriberOut, status_code=201)
def create_subscriber(payload: SubscriberCreate, db: Session = Depends(get_db)) -> Subscriber:
    """Register a WhatsApp or SMS subscriber, optionally scoped to one school."""
    if payload.school_id is not None and db.get(School, payload.school_id) is None:
        raise HTTPException(status_code=404, detail="school not found")

    subscriber = Subscriber(
        school_id=payload.school_id,
        channel=payload.channel,
        contact=payload.contact,
        opted_in_at=utc_now(),
    )
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return subscriber
