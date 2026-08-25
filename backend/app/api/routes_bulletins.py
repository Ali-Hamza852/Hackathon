from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session, selectinload

from app.db.models import Score
from app.db.session import get_db

router = APIRouter(tags=["bulletins"])


@router.api_route("/bulletins/{bulletin_date}.pdf", methods=["GET", "HEAD"])
def get_bulletin_pdf(bulletin_date: date, db: Session = Depends(get_db)) -> Response:
    """Render that day's PDF bulletin on demand from the scores already in the database."""
    scores = (
        db.query(Score)
        .options(selectinload(Score.school))
        .filter(Score.score_date == bulletin_date)
        .all()
    )
    if not scores:
        raise HTTPException(status_code=404, detail="no bulletin for this date")

    pdf_bytes = _render_pdf(scores, bulletin_date.isoformat())
    if pdf_bytes is None:
        raise HTTPException(status_code=503, detail="PDF rendering is unavailable in this environment")

    return Response(content=pdf_bytes, media_type="application/pdf")


def _render_pdf(scores: list[Score], bulletin_date: str) -> bytes | None:
    try:
        from distribution.pdf.generate_bulletin import render_bulletin_pdf_bytes
    except ImportError:
        return None
    return render_bulletin_pdf_bytes(scores, bulletin_date)
