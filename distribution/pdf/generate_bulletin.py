import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright
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


def on_scores_computed(db: Session, scores: list[Score], settings: Settings) -> None:
    if not scores:
        logger.info("no scores computed this cycle, skipping PDF bulletin generation")
        return

    bulletin_date = scores[0].score_date

    try:
        output_dir = Path(settings.bulletin_storage_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{bulletin_date.isoformat()}.pdf"
        html = _render_html(scores, bulletin_date.isoformat())
        _render_html_to_pdf(html, output_path)
    except Exception:
        logger.exception("failed to render PDF bulletin for %s", bulletin_date)
        return

    logger.info("PDF bulletin generated at %s", output_path)


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


def _render_html_to_pdf(html: str, output_path: Path) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page()
            page.set_content(html, wait_until="load")
            page.pdf(path=str(output_path), format="A4", print_background=True)
        finally:
            browser.close()
