from app.db.models import Tier

GREEN_MIN_AQI = 0
GREEN_MAX_AQI = 100
AMBER_MIN_AQI = 101
AMBER_MAX_AQI = 200
RED_MIN_AQI = 201

TIER_RECOMMENDATIONS = {
    Tier.green: "Outdoor activity, sports, and recess proceed as normal.",
    Tier.amber: "Move recess and sports indoors; sensitive students should avoid outdoor exposure.",
    Tier.red: "Recommend remote learning or an indoor-only day; flag to admin for a closure decision.",
}

TIER_LABELS = {
    Tier.green: "Green - Normal",
    Tier.amber: "Amber - Caution",
    Tier.red: "Red - High Risk",
}

DECISION_SUPPORT_DISCLAIMER = (
    "Decision-support estimate - not a replacement for official Punjab EPA/health "
    "authority guidance."
)


def classify_tier(adjusted_aqi: float) -> Tier:
    if adjusted_aqi <= GREEN_MAX_AQI:
        return Tier.green
    if adjusted_aqi <= AMBER_MAX_AQI:
        return Tier.amber
    return Tier.red


def recommendation_for(tier: Tier) -> str:
    return TIER_RECOMMENDATIONS[tier]
