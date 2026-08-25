from app.config import get_settings
from app.db.models import Confidence, ReadingSource, Tier
from app.ingestion.types import StationReading
from app.scoring import engine
from app.time_utils import utc_now


def _reading(lat, lon, aqi_value):
    return StationReading(
        station_id=f"{lat},{lon}",
        lat=lat,
        lon=lon,
        aqi_value=aqi_value,
        pm25=None,
        recorded_at=utc_now(),
        source=ReadingSource.waqi,
    )


def test_direct_and_interpolated_paths_both_run(monkeypatch, db_session, seeded_schools):
    fake_readings = [
        _reading(31.4705, 74.4105, 150),
        _reading(31.5300, 74.4800, 100),
        _reading(31.5500, 74.5000, 220),
    ]
    monkeypatch.setattr(engine, "_gather_live_readings", lambda settings: fake_readings)
    monkeypatch.setattr(engine, "_fetch_wind_safely", lambda settings: None)
    monkeypatch.setattr(engine, "apply_adjustment", lambda raw_aqi, hour, wind: raw_aqi)

    scores = engine.run_scoring_job(db_session, get_settings())

    assert len(scores) == 2
    by_school_name = {score.school.name: score for score in scores}

    direct_score = by_school_name["Direct Hit School"]
    assert direct_score.confidence == Confidence.high
    assert direct_score.raw_aqi == 150
    assert direct_score.tier == Tier.amber

    interpolated_score = by_school_name["Far Interpolated School"]
    assert interpolated_score.confidence in (Confidence.medium, Confidence.low)
    assert 100 < interpolated_score.raw_aqi < 220


def test_no_readings_available_skips_scoring_without_crashing(monkeypatch, db_session, seeded_schools):
    monkeypatch.setattr(engine, "_gather_live_readings", lambda settings: [])
    monkeypatch.setattr(engine, "_load_cached_readings", lambda db: [])

    scores = engine.run_scoring_job(db_session, get_settings())

    assert scores == []
