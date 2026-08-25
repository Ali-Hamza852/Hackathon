import pytest

from app.scoring.aqi_math import pm25_to_aqi


@pytest.mark.parametrize(
    "pm25",
    [12.05, 35.45, 55.45, 150.45, 250.45, 350.45, 0.05],
)
def test_no_gap_between_breakpoints_falls_through_to_worst_case(pm25):
    assert pm25_to_aqi(pm25) < 500


@pytest.mark.parametrize(
    "pm25,expected_aqi",
    [
        (0.0, 0),
        (12.0, 50),
        (12.1, 51),
        (35.4, 100),
        (35.5, 101),
        (500.4, 500),
    ],
)
def test_known_breakpoint_values(pm25, expected_aqi):
    assert pm25_to_aqi(pm25) == expected_aqi


def test_values_above_scale_clamp_to_worst_case():
    assert pm25_to_aqi(1000.0) == 500


def test_negative_values_clamp_to_zero():
    assert pm25_to_aqi(-5.0) == 0
