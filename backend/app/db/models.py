import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SchoolSource(str, enum.Enum):
    overpass = "overpass"
    manual = "manual"


class ReadingSource(str, enum.Enum):
    waqi = "waqi"
    openaq = "openaq"


class Tier(str, enum.Enum):
    green = "green"
    amber = "amber"
    red = "red"


class Confidence(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class SubscriberChannel(str, enum.Enum):
    whatsapp = "whatsapp"
    sms = "sms"


class BroadcastStatus(str, enum.Enum):
    sent = "sent"
    failed = "failed"
    skipped = "skipped"


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    zone: Mapped[str] = mapped_column(String(120), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[SchoolSource] = mapped_column(Enum(SchoolSource), nullable=False)

    scores: Mapped[list["Score"]] = relationship(back_populates="school")
    subscribers: Mapped[list["Subscriber"]] = relationship(back_populates="school")


class AQIReading(Base):
    __tablename__ = "aqi_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    aqi_value: Mapped[int] = mapped_column(Integer, nullable=False)
    pm25: Mapped[float | None] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    source: Mapped[ReadingSource] = mapped_column(Enum(ReadingSource), nullable=False)


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False, index=True)
    score_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    raw_aqi: Mapped[float] = mapped_column(Float, nullable=False)
    adjusted_aqi: Mapped[float] = mapped_column(Float, nullable=False)
    tier: Mapped[Tier] = mapped_column(Enum(Tier), nullable=False)
    recommendation: Mapped[str] = mapped_column(String(500), nullable=False)
    confidence: Mapped[Confidence] = mapped_column(Enum(Confidence), nullable=False)
    distance_to_station_km: Mapped[float] = mapped_column(Float, nullable=False)

    school: Mapped["School"] = relationship(back_populates="scores")
    broadcasts: Mapped[list["BroadcastLog"]] = relationship(back_populates="score")


class Subscriber(Base):
    __tablename__ = "subscribers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    school_id: Mapped[int | None] = mapped_column(ForeignKey("schools.id"), nullable=True)
    channel: Mapped[SubscriberChannel] = mapped_column(Enum(SubscriberChannel), nullable=False)
    contact: Mapped[str] = mapped_column(String(64), nullable=False)
    opted_in_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    school: Mapped["School | None"] = relationship(back_populates="subscribers")
    broadcasts: Mapped[list["BroadcastLog"]] = relationship(back_populates="subscriber")


class BroadcastLog(Base):
    __tablename__ = "broadcast_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subscriber_id: Mapped[int] = mapped_column(ForeignKey("subscribers.id"), nullable=False)
    score_id: Mapped[int] = mapped_column(ForeignKey("scores.id"), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[BroadcastStatus] = mapped_column(Enum(BroadcastStatus), nullable=False)

    subscriber: Mapped["Subscriber"] = relationship(back_populates="broadcasts")
    score: Mapped["Score"] = relationship(back_populates="broadcasts")
