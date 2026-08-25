from typing import Protocol

from app.scoring.distance import haversine_km

DIRECT_MEASUREMENT_MAX_KM = 1.0
MAX_SEARCH_RADIUS_KM = 15.0
MAX_STATIONS_FOR_INTERPOLATION = 3


class HasStationLocation(Protocol):
    lat: float
    lon: float
    aqi_value: int


def nearest_readings(
    school_lat: float, school_lon: float, readings: list[HasStationLocation]
) -> list[tuple[float, HasStationLocation]]:
    scored = sorted(
        ((haversine_km(school_lat, school_lon, r.lat, r.lon), r) for r in readings),
        key=lambda pair: pair[0],
    )
    within_range = [pair for pair in scored if pair[0] <= MAX_SEARCH_RADIUS_KM]
    return within_range[:MAX_STATIONS_FOR_INTERPOLATION]


def estimate_aqi(nearby: list[tuple[float, HasStationLocation]]) -> tuple[float, float] | None:
    if not nearby:
        return None

    nearest_distance, nearest_reading = nearby[0]
    if nearest_distance <= DIRECT_MEASUREMENT_MAX_KM:
        return float(nearest_reading.aqi_value), nearest_distance

    weights = [1 / max(distance, 0.05) for distance, _ in nearby]
    total_weight = sum(weights)
    weighted_aqi = sum(w * r.aqi_value for w, (_, r) in zip(weights, nearby)) / total_weight
    return round(weighted_aqi, 1), nearest_distance
