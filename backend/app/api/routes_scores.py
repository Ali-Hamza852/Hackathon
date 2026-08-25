from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.config import Settings, get_settings
from app.db.models import School, Score
from app.db.session import get_db
from app.jobs.scoring_cycle import run_full_scoring_cycle
from app.schemas.score import ScoreOut

router = APIRouter(tags=["scores"])

LAHORE_TIMEZONE = ZoneInfo("Asia/Karachi")


@router.get("/scores/today", response_model=list[ScoreOut])
def get_todays_scores(db: Session = Depends(get_db)) -> list[ScoreOut]:
    """Today's Smog Score for every seeded school, for the map and list views."""
    today = datetime.now(LAHORE_TIMEZONE).date()
    scores = (
        db.query(Score)
        .options(selectinload(Score.school))
        .filter(Score.score_date == today)
        .all()
    )
    return [ScoreOut.from_score(score) for score in scores]


@router.get("/schools/{school_id}/scores", response_model=list[ScoreOut])
def get_school_trend(school_id: int, days: int = 7, db: Session = Depends(get_db)) -> list[ScoreOut]:
    """A school's score history for the requested number of trailing days (default 7)."""
    school = db.get(School, school_id)
    if school is None:
        raise HTTPException(status_code=404, detail="school not found")

    cutoff = datetime.now(LAHORE_TIMEZONE).date() - timedelta(days=days)
    scores = (
        db.query(Score)
        .options(selectinload(Score.school))
        .filter(Score.school_id == school_id, Score.score_date >= cutoff)
        .order_by(Score.score_date)
        .all()
    )
    return [ScoreOut.from_score(score) for score in scores]


@router.post("/admin/recompute", response_model=list[ScoreOut])
def trigger_recompute(
    x_admin_secret: str = Header(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> list[ScoreOut]:
    """Manually re-run the scoring job on demand. Requires the X-Admin-Secret header."""
    if x_admin_secret != settings.admin_recompute_secret:
        raise HTTPException(status_code=403, detail="invalid admin secret")

    scores = run_full_scoring_cycle(db, settings)
    return [ScoreOut.from_score(score) for score in scores]
