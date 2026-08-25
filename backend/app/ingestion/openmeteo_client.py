from dataclasses import dataclass

import httpx

from app.config import Settings
from app.ingestion.exceptions import AQIProviderError
from app.ingestion.http_utils import REQUEST_TIMEOUT_SECONDS

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
        "forecast_days": 1,
        "timezone": "auto",
    }
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            response = httpx.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            payload = response.json()
            speeds = payload["hourly"]["wind_speed_10m"][:FORECAST_WINDOW_HOURS]
            if not speeds:
                raise AQIProviderError("openmeteo", "empty forecast series")
            return WindForecast(
                avg_wind_speed_kmh=sum(speeds) / len(speeds),
                hours_covered=len(speeds),
            )
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            last_error = exc
    raise AQIProviderError("openmeteo", str(last_error))
