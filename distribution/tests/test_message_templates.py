from datetime import date

from app.db.models import Confidence, School, SchoolSource, Score, Tier
from app.scoring.tiers import DECISION_SUPPORT_DISCLAIMER, TIER_LABELS, recommendation_for
from app.time_utils import utc_now
from distribution.whatsapp.message_templates import build_bulletin_message


def _score_for(tier: Tier) -> Score:
    school = School(
        id=1, name="Test School", zone="Gulberg", lat=31.5, lon=74.3, source=SchoolSource.manual
    )
    score = Score(
        id=1,
        school_id=1,
        score_date=date(2026, 8, 25),
        computed_at=utc_now(),
        raw_aqi=150.0,
        adjusted_aqi=150.0,
        tier=tier,
        recommendation=recommendation_for(tier),
        confidence=Confidence.medium,
        distance_to_station_km=2.0,
    )
    score.school = school
    return score


def test_message_includes_disclaimer_and_tier_wording_for_every_tier():
    for tier in Tier:
        score = _score_for(tier)
        message = build_bulletin_message(score)

        assert DECISION_SUPPORT_DISCLAIMER in message
        assert TIER_LABELS[tier] in message
        assert recommendation_for(tier) in message
        assert score.school.name in message
