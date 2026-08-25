from app.config import Settings
from app.db.models import ReadingSource
from app.ingestion.exceptions import AQIProviderError, ProviderNotConfiguredError
from app.ingestion.http_utils import get_json
from app.ingestion.types import StationReading
from app.time_utils import utc_now

PROVIDER_NAME = "waqi"
BOUNDS_URL = "https://api.waqi.info/map/bounds/"


def fetch_stations_in_bounds(
    min_lat: float, min_lon: float, max_lat: float, max_lon: float, settings: Settings
) -> list[StationReading]:
    if not settings.waqi_configured:
        raise ProviderNotConfiguredError(PROVIDER_NAME)

    latlng = f"{min_lat},{min_lon},{max_lat},{max_lon}"
    payload = get_json(
        PROVIDER_NAME, BOUNDS_URL, params={"latlng": latlng, "token": settings.waqi_api_token}
    )

    if payload.get("status") != "ok":
        raise AQIProviderError(PROVIDER_NAME, str(payload.get("data", "unknown error")))

    readings = []
    for station in payload["data"]:
        try:
            aqi_value = int(station["aqi"])
        except (KeyError, ValueError):
            continue
        readings.append(
            StationReading(
                station_id=str(station["uid"]),
                lat=float(station["lat"]),
                lon=float(station["lon"]),
                aqi_value=aqi_value,
                pm25=None,
                recorded_at=utc_now(),
                source=ReadingSource.waqi,
            )
        )
    return readings
