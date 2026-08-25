from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.db.models import Confidence, Score, Tier


class ScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    school_id: int
    school_name: str
    zone: str
    lat: float
    lon: float
    score_date: date
    computed_at: datetime
    raw_aqi: float
    adjusted_aqi: float
    tier: Tier
    recommendation: str
    confidence: Confidence
    distance_to_station_km: float

    @classmethod
    def from_score(cls, score: Score) -> "ScoreOut":
        return cls(
            id=score.id,
            school_id=score.school_id,
            school_name=score.school.name,
            zone=score.school.zone,
            lat=score.school.lat,
            lon=score.school.lon,
            score_date=score.score_date,
            computed_at=score.computed_at,
            raw_aqi=score.raw_aqi,
            adjusted_aqi=score.adjusted_aqi,
            tier=score.tier,
            recommendation=score.recommendation,
            confidence=score.confidence,
            distance_to_station_km=score.distance_to_station_km,
        )
