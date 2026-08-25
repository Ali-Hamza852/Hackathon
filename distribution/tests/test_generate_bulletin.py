from unittest.mock import patch

from app.config import Settings
from distribution.pdf import generate_bulletin
from distribution.pdf.generate_bulletin import on_scores_computed, render_bulletin_pdf_bytes


def test_render_bulletin_pdf_bytes_produces_a_real_pdf(seeded_scores):
    expected_date = seeded_scores[0].score_date.isoformat()

    pdf_bytes = render_bulletin_pdf_bytes(seeded_scores, expected_date)

    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


def test_render_bulletin_pdf_bytes_returns_none_on_render_failure(seeded_scores):
    with patch.object(
        generate_bulletin, "_build_pdf", side_effect=OSError("unexpected render failure")
    ):
        result = render_bulletin_pdf_bytes(seeded_scores, seeded_scores[0].score_date.isoformat())

    assert result is None


def test_generates_real_pdf_for_seeded_scores(db_session, seeded_scores, tmp_path):
    settings = Settings(bulletin_storage_dir=str(tmp_path))

    on_scores_computed(db_session, seeded_scores, settings)

    expected_date = seeded_scores[0].score_date.isoformat()
    output_path = tmp_path / f"{expected_date}.pdf"

    assert output_path.exists()
    assert output_path.stat().st_size > 1000
    assert output_path.read_bytes().startswith(b"%PDF")


def test_skips_cleanly_when_no_scores(db_session, tmp_path):
    settings = Settings(bulletin_storage_dir=str(tmp_path))

    on_scores_computed(db_session, [], settings)

    assert list(tmp_path.iterdir()) == []


def test_creates_storage_dir_if_missing(db_session, seeded_scores, tmp_path):
    nested_dir = tmp_path / "nested" / "bulletins"
    settings = Settings(bulletin_storage_dir=str(nested_dir))

    on_scores_computed(db_session, seeded_scores, settings)

    expected_date = seeded_scores[0].score_date.isoformat()
    assert (nested_dir / f"{expected_date}.pdf").exists()


def test_does_not_write_a_file_when_rendering_fails(db_session, seeded_scores, tmp_path):
    settings = Settings(bulletin_storage_dir=str(tmp_path))

    with patch.object(
        generate_bulletin, "_build_pdf", side_effect=OSError("unexpected render failure")
    ):
        on_scores_computed(db_session, seeded_scores, settings)

    assert list(tmp_path.iterdir()) == []


def test_does_not_crash_when_storage_directory_is_unwritable(db_session, seeded_scores, tmp_path):
    unwritable_path = tmp_path / "bulletins"
    unwritable_path.mkdir()
    unwritable_path.chmod(0o400)
    settings = Settings(bulletin_storage_dir=str(unwritable_path))

    try:
        on_scores_computed(db_session, seeded_scores, settings)
    finally:
        unwritable_path.chmod(0o700)
