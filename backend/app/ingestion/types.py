from dataclasses import dataclass
from datetime import datetime

from app.db.models import ReadingSource


@dataclass(frozen=True)
class StationReading:
    station_id: str
    lat: float
    lon: float
    aqi_value: int
    pm25: float | None
    recorded_at: datetime
    source: ReadingSource
