from dataclasses import dataclass

from app.config import Settings
from app.ingestion.exceptions import AQIProviderError
from app.ingestion.http_utils import get_json

FORECAST_WINDOW_HOURS = 12


@dataclass(frozen=True)
class WindForecast:
    avg_wind_speed_kmh: float
    hours_covered: int


def fetch_wind_forecast(lat: float, lon: float, settings: Settings) -> WindForecast:
    url = f"{settings.openmeteo_base_url}/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "wind_speed_10m",
        "forecast_hours": FORECAST_WINDOW_HOURS,
        "timezone": "auto",
    }
    payload = get_json("openmeteo", url, params=params)

    try:
        speeds = payload["hourly"]["wind_speed_10m"]
    except KeyError as exc:
        raise AQIProviderError("openmeteo", f"unexpected response shape: {exc}") from exc

    if not speeds:
        raise AQIProviderError("openmeteo", "empty forecast series")

    return WindForecast(avg_wind_speed_kmh=sum(speeds) / len(speeds), hours_covered=len(speeds))
