from app.ingestion.openmeteo_client import WindForecast
from app.scoring.wind_adjustment import apply_adjustment


def test_stagnant_air_and_morning_hours_raise_the_estimate():
    calm_wind = WindForecast(avg_wind_speed_kmh=2.0, hours_covered=12)
    adjusted = apply_adjustment(raw_aqi=150, local_hour=7, wind_forecast=calm_wind)
    assert adjusted > 150


def test_high_wind_and_afternoon_hours_lower_the_estimate():
    breezy_wind = WindForecast(avg_wind_speed_kmh=25.0, hours_covered=12)
    adjusted = apply_adjustment(raw_aqi=150, local_hour=14, wind_forecast=breezy_wind)
    assert adjusted < 150


def test_missing_wind_forecast_falls_back_to_time_of_day_only():
    adjusted = apply_adjustment(raw_aqi=100, local_hour=22, wind_forecast=None)
    assert adjusted == 100
