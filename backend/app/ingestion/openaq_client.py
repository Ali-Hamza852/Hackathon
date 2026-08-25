from datetime import datetime, timedelta

from app.config import Settings
from app.db.models import ReadingSource
from app.ingestion.exceptions import AQIProviderError, ProviderNotConfiguredError
from app.ingestion.http_utils import get_json
from app.ingestion.types import StationReading
from app.scoring.aqi_math import pm25_to_aqi
from app.time_utils import utc_now

PROVIDER_NAME = "openaq"
LOCATIONS_URL = "https://api.openaq.org/v3/locations"
LATEST_URL_TEMPLATE = "https://api.openaq.org/v3/locations/{location_id}/latest"
PM25_PARAMETER_ID = 2
STALE_STATION_MAX_AGE_HOURS = 48


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
            reading = _reading_for_location(location, headers)
        except (AQIProviderError, KeyError, ValueError, TypeError):
            continue
        if reading is not None:
            readings.append(reading)
    return readings


def _reading_for_location(location: dict, headers: dict) -> StationReading | None:
    sensor_id = _find_pm25_sensor_id(location["sensors"])
    if sensor_id is None or _reports_too_stale(location.get("datetimeLast")):
        return None

    pm25, recorded_at = _find_latest_pm25(location["id"], sensor_id, headers)
    if pm25 is None or pm25 < 0:
        return None

    return StationReading(
        station_id=str(location["id"]),
        lat=location["coordinates"]["latitude"],
        lon=location["coordinates"]["longitude"],
        aqi_value=pm25_to_aqi(pm25),
        pm25=pm25,
        recorded_at=recorded_at,
        source=ReadingSource.openaq,
    )


def _find_pm25_sensor_id(sensors: list[dict]) -> int | None:
    for sensor in sensors:
        if sensor.get("parameter", {}).get("name") == "pm25":
            return sensor["id"]
    return None


def _reports_too_stale(datetime_last: dict | None) -> bool:
    if not datetime_last or not datetime_last.get("utc"):
        return True
    last_seen = _parse_iso(datetime_last["utc"])
    return utc_now() - last_seen > timedelta(hours=STALE_STATION_MAX_AGE_HOURS)


def _find_latest_pm25(location_id: int, sensor_id: int, headers: dict) -> tuple[float | None, datetime]:
    url = LATEST_URL_TEMPLATE.format(location_id=location_id)
    results = get_json(PROVIDER_NAME, url, headers=headers).get("results", [])
    for entry in results:
        if entry.get("sensorsId") == sensor_id:
            return float(entry["value"]), _parse_iso(entry["datetime"]["utc"])
    return None, utc_now()


def _parse_iso(raw: str) -> datetime:
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).replace(tzinfo=None)
