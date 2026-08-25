import pytest

from app.db.models import Tier
from app.scoring.tiers import classify_tier


@pytest.mark.parametrize(
    "aqi,expected_tier",
    [
        (0, Tier.green),
        (100, Tier.green),
        (101, Tier.amber),
        (200, Tier.amber),
        (201, Tier.red),
        (400, Tier.red),
    ],
)
def test_tier_boundaries(aqi, expected_tier):
    assert classify_tier(aqi) == expected_tier
