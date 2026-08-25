from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.subscriber import SubscriberCreate, SubscriberOut
from app.services.subscribers import SchoolNotFoundError, register_subscriber

router = APIRouter(tags=["subscribers"])


@router.post("/subscribers", response_model=SubscriberOut, status_code=201)
def create_subscriber(payload: SubscriberCreate, db: Session = Depends(get_db)) -> SubscriberOut:
    """Register a WhatsApp or SMS subscriber, optionally scoped to one school."""
    try:
        subscriber = register_subscriber(
            db, channel=payload.channel, contact=payload.contact, school_id=payload.school_id
        )
    except SchoolNotFoundError:
        raise HTTPException(status_code=404, detail="school not found")
    return subscriber
