from app.db.models import Confidence

HIGH_CONFIDENCE_MAX_KM = 1.0
MEDIUM_CONFIDENCE_MAX_KM = 5.0


def classify_confidence(distance_to_station_km: float) -> Confidence:
    if distance_to_station_km <= HIGH_CONFIDENCE_MAX_KM:
        return Confidence.high
    if distance_to_station_km <= MEDIUM_CONFIDENCE_MAX_KM:
        return Confidence.medium
    return Confidence.low
