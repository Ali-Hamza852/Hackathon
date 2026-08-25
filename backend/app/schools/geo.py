LAHORE_MIN_LAT = 31.30
LAHORE_MAX_LAT = 31.70
LAHORE_MIN_LON = 74.10
LAHORE_MAX_LON = 74.55


def is_within_lahore(lat: float, lon: float) -> bool:
    return LAHORE_MIN_LAT <= lat <= LAHORE_MAX_LAT and LAHORE_MIN_LON <= lon <= LAHORE_MAX_LON
