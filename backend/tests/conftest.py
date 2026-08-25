import os
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_saans.db"
os.environ["ADMIN_RECOMPUTE_SECRET"] = "test-secret"

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from app.db.models import School, SchoolSource
from app.db.session import SessionLocal, engine, init_db
from app.db.models import Base


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
        School(name="Direct Hit School", zone="DHA", lat=31.4700, lon=74.4100, source=SchoolSource.manual),
        School(name="Far Interpolated School", zone="Batapur", lat=31.5400, lon=74.4900, source=SchoolSource.manual),
    ]
    db_session.add_all(schools)
    db_session.commit()
    for school in schools:
        db_session.refresh(school)
    return schools
