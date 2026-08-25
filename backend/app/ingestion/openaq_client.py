from datetime import datetime

from app.config import Settings
from app.db.models import ReadingSource
from app.ingestion.exceptions import AQIProviderError, ProviderNotConfiguredError
from app.ingestion.http_utils import get_json
from app.ingestion.types import StationReading
from app.scoring.aqi_math import pm25_to_aqi

PROVIDER_NAME = "openaq"
LOCATIONS_URL = "https://api.openaq.org/v3/locations"
LATEST_URL_TEMPLATE = "https://api.openaq.org/v3/locations/{location_id}/latest"
PM25_PARAMETER_ID = 2


def fetch_locations_in_bounds(
    min_lat: float, min_lon: float, max_lat: float, max_lon: float, settings: Settings
) -> list[StationReading]:
    if not settings.openaq_configured:
        raise ProviderNotConfiguredError(PROVIDER_NAME)

    headers = {"X-API-Key": settings.openaq_api_key}
    params = {
        "bbox": f"{min_lon},{min_lat},{max_lon},{max_lat}",
        "parameters_id": PM25_PARAMETER_ID,
        "limit": 50,
    }
    locations = get_json(PROVIDER_NAME, LOCATIONS_URL, params=params, headers=headers).get("results", [])

    readings = []
    for location in locations:
        try:
            pm25, recorded_at = _find_latest_pm25(location["id"], headers)
        except AQIProviderError:
            continue
        readings.append(
            StationReading(
                station_id=str(location["id"]),
                lat=location["coordinates"]["latitude"],
                lon=location["coordinates"]["longitude"],
                aqi_value=pm25_to_aqi(pm25),
                pm25=pm25,
                recorded_at=recorded_at,
                source=ReadingSource.openaq,
            )
        )
    return readings


def _find_latest_pm25(location_id: int, headers: dict) -> tuple[float, datetime]:
    url = LATEST_URL_TEMPLATE.format(location_id=location_id)
    results = get_json(PROVIDER_NAME, url, headers=headers).get("results", [])
    for entry in results:
        if entry.get("parameter", {}).get("name") == "pm25":
            recorded_at = datetime.fromisoformat(
                entry["datetime"]["utc"].replace("Z", "+00:00")
            ).replace(tzinfo=None)
            return float(entry["value"]), recorded_at
    raise AQIProviderError(PROVIDER_NAME, "no pm25 sensor at this location")
