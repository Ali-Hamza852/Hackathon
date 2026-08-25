import json

from app.db.models import School, SchoolSource
from app.db.session import SessionLocal, init_db
from app.schools.registry_loader import SEED_FILE_PATH


def seed_schools() -> int:
    init_db()
    try:
        schools = json.loads(SEED_FILE_PATH.read_text())
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"{SEED_FILE_PATH} not found - run `python -m app.schools.registry_loader` first"
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{SEED_FILE_PATH} is not valid JSON: {exc}") from exc

    db = SessionLocal()
    try:
        inserted = 0
        for entry in schools:
            exists = (
                db.query(School)
                .filter(School.name == entry["name"], School.zone == entry["zone"])
                .first()
            )
            if exists:
                continue
            db.add(
                School(
                    name=entry["name"],
                    zone=entry["zone"],
                    lat=entry["lat"],
                    lon=entry["lon"],
                    source=SchoolSource(entry["source"]),
                )
            )
            inserted += 1
        db.commit()
        return inserted
    finally:
        db.close()


if __name__ == "__main__":
    count = seed_schools()
    print(f"inserted {count} new schools")
