import pytest

from app.db.models import Confidence
from app.scoring.confidence import classify_confidence


@pytest.mark.parametrize(
    "distance_km,expected_confidence",
    [
        (0.0, Confidence.high),
        (1.0, Confidence.high),
        (1.1, Confidence.medium),
        (5.0, Confidence.medium),
        (5.1, Confidence.low),
        (14.9, Confidence.low),
    ],
)
def test_confidence_thresholds(distance_km, expected_confidence):
    assert classify_confidence(distance_km) == expected_confidence
