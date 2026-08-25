from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.models import School
from app.db.session import get_db
from app.schemas.school import SchoolOut

router = APIRouter(tags=["schools"])


@router.get("/schools", response_model=list[SchoolOut])
def list_schools(
    zone: str | None = None, q: str | None = None, db: Session = Depends(get_db)
) -> list[School]:
    """List all seeded schools. `q` matches either name or zone; `zone` narrows further."""
    query = db.query(School)
    if q:
        query = query.filter(or_(School.name.ilike(f"%{q}%"), School.zone.ilike(f"%{q}%")))
    if zone:
        query = query.filter(School.zone.ilike(f"%{zone}%"))
    return query.order_by(School.name).all()


@router.get("/schools/{school_id}", response_model=SchoolOut)
def get_school(school_id: int, db: Session = Depends(get_db)) -> School:
    """Fetch a single school's registry details by id."""
    school = db.get(School, school_id)
    if school is None:
        raise HTTPException(status_code=404, detail="school not found")
    return school
