from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.db.models import SubscriberChannel


class SubscriberCreate(BaseModel):
    school_id: int | None = None
    channel: SubscriberChannel
    contact: str

    @field_validator("contact")
    @classmethod
    def contact_must_look_like_a_phone_number(cls, value: str) -> str:
        digits = value.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 8:
            raise ValueError("contact must be a valid phone number")
        return value


class SubscriberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    school_id: int | None
    channel: SubscriberChannel
    contact: str
    opted_in_at: datetime
