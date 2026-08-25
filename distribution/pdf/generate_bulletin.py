import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session

from app.config import Settings
from app.db.models import Score, Tier
from app.scoring.tiers import DECISION_SUPPORT_DISCLAIMER, TIER_LABELS

logger = logging.getLogger("saans.distribution.pdf")

TEMPLATE_DIR = Path(__file__).resolve().parent
TEMPLATE_NAME = "bulletin_template.html"

TIER_SYMBOLS = {
    Tier.green: "●",
    Tier.amber: "▲",
    Tier.red: "■",
}

_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
)


def render_bulletin_pdf_bytes(scores: list[Score], bulletin_date: str) -> bytes | None:
    try:
        html = _render_html(scores, bulletin_date)
        return _render_html_to_pdf_bytes(html)
    except Exception:
        logger.exception("failed to render PDF bulletin for %s", bulletin_date)
        return None


def on_scores_computed(db: Session, scores: list[Score], settings: Settings) -> None:
    if not scores:
        logger.info("no scores computed this cycle, skipping PDF bulletin pre-render")
        return

    bulletin_date = scores[0].score_date
    pdf_bytes = render_bulletin_pdf_bytes(scores, bulletin_date.isoformat())
    if pdf_bytes is None:
        return

    try:
        output_dir = Path(settings.bulletin_storage_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / f"{bulletin_date.isoformat()}.pdf").write_bytes(pdf_bytes)
    except OSError:
        logger.info("bulletin storage isn't writable here (expected on serverless) - "
                    "the dashboard renders it on demand from the API instead")


def _render_html(scores: list[Score], bulletin_date: str) -> str:
    template = _jinja_env.get_template(TEMPLATE_NAME)
    return template.render(
        bulletin_date=bulletin_date,
        zones=_group_by_zone(scores),
        disclaimer=DECISION_SUPPORT_DISCLAIMER,
    )


def _group_by_zone(scores: list[Score]) -> dict[str, list[dict[str, str | int]]]:
    zones: dict[str, list[dict[str, str | int]]] = {}
    for score in scores:
        zones.setdefault(score.school.zone, []).append(
            {
                "school_name": score.school.name,
                "tier_label": TIER_LABELS[score.tier],
                "tier_symbol": TIER_SYMBOLS[score.tier],
                "recommendation": score.recommendation,
                "adjusted_aqi": round(score.adjusted_aqi),
            }
        )
    for entries in zones.values():
        entries.sort(key=lambda entry: str(entry["school_name"]))
    return dict(sorted(zones.items()))


def _render_html_to_pdf_bytes(html: str) -> bytes:
    from weasyprint import HTML

    return HTML(string=html, base_url=str(TEMPLATE_DIR)).write_pdf()
