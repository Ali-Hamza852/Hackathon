from sqlalchemy.orm import Session

from app.db.models import School, Subscriber, SubscriberChannel
from app.time_utils import utc_now


class SchoolNotFoundError(Exception):
    pass


def register_subscriber(
    db: Session, channel: SubscriberChannel, contact: str, school_id: int | None = None
) -> Subscriber:
    if school_id is not None and db.get(School, school_id) is None:
        raise SchoolNotFoundError(f"no school with id {school_id}")

    existing = (
        db.query(Subscriber)
        .filter(
            Subscriber.contact == contact,
            Subscriber.channel == channel,
            Subscriber.school_id == school_id,
        )
        .first()
    )
    if existing:
        return existing

    subscriber = Subscriber(
        school_id=school_id, channel=channel, contact=contact, opted_in_at=utc_now()
    )
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return subscriber


def find_school_by_name(db: Session, name: str) -> School | None:
    return db.query(School).filter(School.name.ilike(f"%{name.strip()}%")).first()
