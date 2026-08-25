from app.db.models import Score
from app.scoring.tiers import DECISION_SUPPORT_DISCLAIMER, TIER_LABELS


def build_bulletin_message(score: Score) -> str:
    school = score.school
    tier_label = TIER_LABELS[score.tier]
    return (
        f"SAANS Smog Advisory - {school.name} ({school.zone})\n"
        f"{score.score_date.isoformat()}: {tier_label}\n"
        f"{score.recommendation}\n\n"
        f"{DECISION_SUPPORT_DISCLAIMER}"
    )
