import os
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
for path in (str(BACKEND_DIR), str(REPO_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_distribution.db")
os.environ.setdefault("ADMIN_RECOMPUTE_SECRET", "test-secret")
os.environ.setdefault("WHATSAPP_VERIFY_TOKEN", "test-verify-token")

import pytest

from app.db.models import Base, Confidence, School, SchoolSource, Score, Tier
from app.db.session import SessionLocal, engine, init_db
from app.scoring.tiers import recommendation_for
from app.time_utils import utc_now


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(bind=engine)
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def seeded_schools(db_session):
    schools = [
        School(
            name="Riverbend Grammar School",
            zone="Gulberg",
            lat=31.5100,
            lon=74.3500,
            source=SchoolSource.manual,
        ),
        School(
            name="Township Public School",
            zone="Township",
            lat=31.4400,
            lon=74.2800,
            source=SchoolSource.manual,
        ),
    ]
    db_session.add_all(schools)
    db_session.commit()
    for school in schools:
        db_session.refresh(school)
    return schools


@pytest.fixture
def seeded_scores(db_session, seeded_schools):
    score_date = date(2026, 8, 25)
    tier_and_aqi = [(Tier.green, 80.0), (Tier.red, 260.0)]
    scores = []
    for school, (tier, aqi) in zip(seeded_schools, tier_and_aqi):
        score = Score(
            school_id=school.id,
            score_date=score_date,
            computed_at=utc_now(),
            raw_aqi=aqi,
            adjusted_aqi=aqi,
            tier=tier,
            recommendation=recommendation_for(tier),
            confidence=Confidence.high,
            distance_to_station_km=0.8,
        )
        db_session.add(score)
        scores.append(score)
    db_session.commit()
    for score in scores:
        db_session.refresh(score)
    return scores
