from datetime import timedelta
from unittest.mock import patch

from app.config import Settings
from app.ingestion import openaq_client
from app.time_utils import utc_now


def _settings():
    return Settings(openaq_api_key="test-key")


def _location(location_id, sensor_id, hours_since_last_seen=1):
    last_seen = utc_now() - timedelta(hours=hours_since_last_seen)
    return {
        "id": location_id,
        "coordinates": {"latitude": 31.55, "longitude": 74.34},
        "sensors": [{"id": sensor_id, "parameter": {"name": "pm25"}}],
        "datetimeLast": {"utc": last_seen.isoformat() + "Z"},
    }


def _latest_payload(sensor_id, value, minutes_ago=5):
    recorded = utc_now() - timedelta(minutes=minutes_ago)
    return {"results": [{"sensorsId": sensor_id, "value": value, "datetime": {"utc": recorded.isoformat() + "Z"}}]}


def test_fetches_a_live_station_with_a_valid_reading():
    location = _location(location_id=8664, sensor_id=25135)

    def fake_get_json(provider, url, params=None, headers=None):
        if "locations/8664/latest" in url:
            return _latest_payload(25135, 62.3)
        return {"results": [location]}

    with patch("app.ingestion.openaq_client.get_json", side_effect=fake_get_json):
        readings = openaq_client.fetch_locations_in_bounds(31.3, 74.1, 31.7, 74.5, _settings())

    assert len(readings) == 1
    assert readings[0].pm25 == 62.3
    assert readings[0].station_id == "8664"


def test_skips_a_station_with_no_recent_report():
    stale_location = _location(location_id=1, sensor_id=100, hours_since_last_seen=500)

    with patch("app.ingestion.openaq_client.get_json", return_value={"results": [stale_location]}):
        readings = openaq_client.fetch_locations_in_bounds(31.3, 74.1, 31.7, 74.5, _settings())

    assert readings == []


def test_skips_a_station_reporting_a_sentinel_negative_value():
    location = _location(location_id=2, sensor_id=200)

    def fake_get_json(provider, url, params=None, headers=None):
        if "locations/2/latest" in url:
            return _latest_payload(200, -999.0)
        return {"results": [location]}

    with patch("app.ingestion.openaq_client.get_json", side_effect=fake_get_json):
        readings = openaq_client.fetch_locations_in_bounds(31.3, 74.1, 31.7, 74.5, _settings())

    assert readings == []


def test_skips_a_location_with_no_pm25_sensor():
    location = {
        "id": 3,
        "coordinates": {"latitude": 31.55, "longitude": 74.34},
        "sensors": [{"id": 300, "parameter": {"name": "temperature"}}],
        "datetimeLast": {"utc": utc_now().isoformat() + "Z"},
    }

    with patch("app.ingestion.openaq_client.get_json", return_value={"results": [location]}):
        readings = openaq_client.fetch_locations_in_bounds(31.3, 74.1, 31.7, 74.5, _settings())

    assert readings == []
