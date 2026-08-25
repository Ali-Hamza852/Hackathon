import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import Settings
from app.db.models import Score, Tier
from app.scoring.tiers import DECISION_SUPPORT_DISCLAIMER, TIER_LABELS

logger = logging.getLogger("saans.distribution.pdf")

TIER_MARKERS = {
    Tier.green: "[G]",
    Tier.amber: "[A]",
    Tier.red: "[R]",
}

TABLE_HEADERS = ["School", "Tier", "AQI", "Recommended Action"]
COLUMN_WIDTHS = (60, 45, 20, 65)


def render_bulletin_pdf_bytes(scores: list[Score], bulletin_date: str) -> bytes | None:
    try:
        return _build_pdf(scores, bulletin_date)
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
        logger.info(
            "bulletin storage isn't writable here (expected on serverless) - "
            "the dashboard renders it on demand from the API instead"
        )


def _build_pdf(scores: list[Score], bulletin_date: str) -> bytes:
    from fpdf import FPDF

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_margins(14, 14, 14)

    pdf.set_font("helvetica", "B", 20)
    pdf.cell(text="SAANS Smog Advisory Bulletin", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("helvetica", "", 10)
    pdf.cell(
        text=f"{bulletin_date} - Lahore school smog advisory, grouped by zone",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_font("helvetica", "", 9)
    legend = "   ".join(f"{TIER_MARKERS[tier]} {TIER_LABELS[tier]}" for tier in Tier)
    pdf.cell(text=legend, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    for zone, entries in _group_by_zone(scores).items():
        _render_zone(pdf, zone, entries)

    pdf.set_font("helvetica", "", 8)
    pdf.ln(4)
    pdf.multi_cell(w=0, text=DECISION_SUPPORT_DISCLAIMER)

    return bytes(pdf.output())


def _render_zone(pdf, zone: str, entries: list[dict]) -> None:
    pdf.set_font("helvetica", "B", 13)
    pdf.cell(text=zone, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    with pdf.table(col_widths=COLUMN_WIDTHS, text_align="LEFT", line_height=6) as table:
        header_row = table.row()
        for heading in TABLE_HEADERS:
            header_row.cell(heading)

        for entry in entries:
            row = table.row()
            row.cell(str(entry["school_name"]))
            row.cell(f"{entry['tier_marker']} {entry['tier_label']}")
            row.cell(str(entry["adjusted_aqi"]))
            row.cell(str(entry["recommendation"]))

    pdf.ln(4)


def _group_by_zone(scores: list[Score]) -> dict[str, list[dict[str, str | int]]]:
    zones: dict[str, list[dict[str, str | int]]] = {}
    for score in scores:
        zones.setdefault(score.school.zone, []).append(
            {
                "school_name": score.school.name,
                "tier_label": TIER_LABELS[score.tier],
                "tier_marker": TIER_MARKERS[score.tier],
                "recommendation": score.recommendation,
                "adjusted_aqi": round(score.adjusted_aqi),
            }
        )
    for entries in zones.values():
        entries.sort(key=lambda entry: str(entry["school_name"]))
    return dict(sorted(zones.items()))
