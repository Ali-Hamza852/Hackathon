from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import School
from app.db.session import get_db
from app.schemas.school import SchoolOut

router = APIRouter(tags=["schools"])


@router.get("/schools", response_model=list[SchoolOut])
def list_schools(
    zone: str | None = None, q: str | None = None, db: Session = Depends(get_db)
) -> list[School]:
    """List all seeded schools, optionally filtered by zone or a name search term."""
    query = db.query(School)
    if zone:
        query = query.filter(School.zone.ilike(f"%{zone}%"))
    if q:
        query = query.filter(School.name.ilike(f"%{q}%"))
    return query.order_by(School.name).all()


@router.get("/schools/{school_id}", response_model=SchoolOut)
def get_school(school_id: int, db: Session = Depends(get_db)) -> School:
    """Fetch a single school's registry details by id."""
    school = db.get(School, school_id)
    if school is None:
        raise HTTPException(status_code=404, detail="school not found")
    return school
