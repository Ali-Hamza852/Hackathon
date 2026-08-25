from app.config import Settings
from distribution.pdf.generate_bulletin import on_scores_computed


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
