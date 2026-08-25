from dataclasses import dataclass

from app.scoring.interpolation import estimate_aqi, nearest_readings


@dataclass
class FakeReading:
    lat: float
    lon: float
    aqi_value: int


def test_direct_measurement_within_one_km():
    school_lat, school_lon = 31.4700, 74.4100
    close_station = FakeReading(lat=31.4705, lon=74.4102, aqi_value=180)
    far_station = FakeReading(lat=31.6000, lon=74.6000, aqi_value=40)

    nearby = nearest_readings(school_lat, school_lon, [close_station, far_station])
    raw_aqi, distance_km = estimate_aqi(nearby)

    assert distance_km < 1.0
    assert raw_aqi == 180


def test_interpolated_estimate_beyond_one_km():
    school_lat, school_lon = 31.4700, 74.4100
    station_a = FakeReading(lat=31.4900, lon=74.4300, aqi_value=200)
    station_b = FakeReading(lat=31.4500, lon=74.3900, aqi_value=100)

    nearby = nearest_readings(school_lat, school_lon, [station_a, station_b])
    raw_aqi, distance_km = estimate_aqi(nearby)

    assert distance_km > 1.0
    assert 100 < raw_aqi < 200


def test_no_stations_within_range_returns_none():
    nearby = nearest_readings(31.4700, 74.4100, [FakeReading(lat=10.0, lon=10.0, aqi_value=50)])
    assert estimate_aqi(nearby) is None
