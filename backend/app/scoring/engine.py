from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.config import Settings
from app.db.models import AQIReading, School, Score
from app.ingestion import openaq_client, openmeteo_client, waqi_client
from app.ingestion.exceptions import AQIProviderError
from app.ingestion.types import StationReading
from app.schools.geo import LAHORE_MAX_LAT, LAHORE_MAX_LON, LAHORE_MIN_LAT, LAHORE_MIN_LON
from app.scoring.confidence import classify_confidence
from app.scoring.interpolation import estimate_aqi, nearest_readings
from app.scoring.tiers import classify_tier, recommendation_for
from app.scoring.wind_adjustment import apply_adjustment
from app.time_utils import utc_now

LAHORE_TIMEZONE = ZoneInfo("Asia/Karachi")
CACHE_FRESHNESS_HOURS = 6
LAHORE_CENTROID_LAT = 31.5497
LAHORE_CENTROID_LON = 74.3436


def run_scoring_job(db: Session, settings: Settings) -> list[Score]:
    schools = db.query(School).all()
    if not schools:
        return []

    readings = _gather_live_readings(settings)
    if readings:
        _cache_readings(db, readings)
    else:
        readings = _load_cached_readings(db)

    if not readings:
        return []

    wind_forecast = _fetch_wind_safely(settings)
    local_hour = datetime.now(LAHORE_TIMEZONE).hour
    score_date = datetime.now(LAHORE_TIMEZONE).date()

    existing_scores_by_school_id = {
        score.school_id: score
        for score in db.query(Score).filter(Score.score_date == score_date).all()
    }

    scores = []
    for school in schools:
        nearby = nearest_readings(school.lat, school.lon, readings)
        estimate = estimate_aqi(nearby)
        if estimate is None:
            continue

        raw_aqi, distance_km = estimate
        adjusted_aqi = apply_adjustment(raw_aqi, local_hour, wind_forecast)
        tier = classify_tier(adjusted_aqi)
        rounded_distance_km = round(distance_km, 2)

        score = existing_scores_by_school_id.get(school.id)
        if score is None:
            score = Score(school_id=school.id, score_date=score_date)
            db.add(score)

        score.computed_at = utc_now()
        score.raw_aqi = raw_aqi
        score.adjusted_aqi = adjusted_aqi
        score.tier = tier
        score.recommendation = recommendation_for(tier)
        score.confidence = classify_confidence(rounded_distance_km)
        score.distance_to_station_km = rounded_distance_km
        scores.append(score)

    db.commit()
    for score in scores:
        db.refresh(score)
    return scores


def _gather_live_readings(settings: Settings) -> list[StationReading]:
    bounds = (LAHORE_MIN_LAT, LAHORE_MIN_LON, LAHORE_MAX_LAT, LAHORE_MAX_LON)
    try:
        readings = waqi_client.fetch_stations_in_bounds(*bounds, settings)
        if readings:
            return readings
    except AQIProviderError:
        pass

    try:
        return openaq_client.fetch_locations_in_bounds(*bounds, settings)
    except AQIProviderError:
        return []


def _cache_readings(db: Session, readings: list[StationReading]) -> None:
    for reading in readings:
        db.add(
            AQIReading(
                station_id=reading.station_id,
                lat=reading.lat,
                lon=reading.lon,
                aqi_value=reading.aqi_value,
                pm25=reading.pm25,
                recorded_at=reading.recorded_at,
                source=reading.source,
            )
        )
    db.commit()


def _load_cached_readings(db: Session) -> list[AQIReading]:
    cutoff = utc_now() - timedelta(hours=CACHE_FRESHNESS_HOURS)
    return db.query(AQIReading).filter(AQIReading.recorded_at >= cutoff).all()


def _fetch_wind_safely(settings: Settings):
    try:
        return openmeteo_client.fetch_wind_forecast(LAHORE_CENTROID_LAT, LAHORE_CENTROID_LON, settings)
    except AQIProviderError:
        return None
