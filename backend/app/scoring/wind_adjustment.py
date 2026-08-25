from app.ingestion.openmeteo_client import WindForecast

LOW_WIND_THRESHOLD_KMH = 8.0
HIGH_WIND_THRESHOLD_KMH = 20.0
STAGNANT_AIR_MULTIPLIER = 1.10
DISPERSED_AIR_MULTIPLIER = 0.92

MORNING_ASSEMBLY_HOURS = range(6, 10)
AFTERNOON_DISMISSAL_HOURS = range(12, 16)
MORNING_MULTIPLIER = 1.05
AFTERNOON_MULTIPLIER = 0.95


def time_of_day_multiplier(local_hour: int) -> float:
    if local_hour in MORNING_ASSEMBLY_HOURS:
        return MORNING_MULTIPLIER
    if local_hour in AFTERNOON_DISMISSAL_HOURS:
        return AFTERNOON_MULTIPLIER
    return 1.0


def wind_multiplier(wind_forecast: WindForecast | None) -> float:
    if wind_forecast is None:
        return 1.0
    if wind_forecast.avg_wind_speed_kmh <= LOW_WIND_THRESHOLD_KMH:
        return STAGNANT_AIR_MULTIPLIER
    if wind_forecast.avg_wind_speed_kmh >= HIGH_WIND_THRESHOLD_KMH:
        return DISPERSED_AIR_MULTIPLIER
    return 1.0


def apply_adjustment(raw_aqi: float, local_hour: int, wind_forecast: WindForecast | None) -> float:
    factor = time_of_day_multiplier(local_hour) * wind_multiplier(wind_forecast)
    return round(raw_aqi * factor, 1)
