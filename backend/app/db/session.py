from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.db.models import Base

settings = get_settings()


def _normalized_database_url(raw_url: str) -> str:
    if raw_url.startswith("postgres://"):
        return "postgresql+psycopg://" + raw_url[len("postgres://") :]
    if raw_url.startswith("postgresql://"):
        return "postgresql+psycopg://" + raw_url[len("postgresql://") :]
    return raw_url


database_url = _normalized_database_url(settings.database_url)
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
