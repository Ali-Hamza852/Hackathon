from fastapi.testclient import TestClient

from app.db.models import ReadingSource
from app.ingestion.types import StationReading
from app.main import app
from app.scoring import engine
from app.time_utils import utc_now


def _reading(lat, lon, aqi_value):
    return StationReading(
        station_id=f"{lat},{lon}",
        lat=lat,
        lon=lon,
        aqi_value=aqi_value,
        pm25=None,
        recorded_at=utc_now(),
        source=ReadingSource.waqi,
    )


def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_schools_and_scores_round_trip(monkeypatch, seeded_schools):
    monkeypatch.setattr(
        engine, "_gather_live_readings", lambda settings: [_reading(31.4705, 74.4105, 150)]
    )
    monkeypatch.setattr(engine, "_fetch_wind_safely", lambda settings: None)

    with TestClient(app) as client:
        schools_response = client.get("/schools")
        assert schools_response.status_code == 200
        assert len(schools_response.json()) == 2

        search_response = client.get("/schools", params={"q": "Direct"})
        assert len(search_response.json()) == 1

        zone_via_q_response = client.get("/schools", params={"q": "Batapur"})
        assert len(zone_via_q_response.json()) == 1
        assert zone_via_q_response.json()[0]["name"] == "Far Interpolated School"

        recompute_response = client.post(
            "/admin/recompute", headers={"X-Admin-Secret": "test-secret"}
        )
        assert recompute_response.status_code == 200
        assert len(recompute_response.json()) == 2

        second_recompute_response = client.post(
            "/admin/recompute", headers={"X-Admin-Secret": "test-secret"}
        )
        assert {s["id"] for s in recompute_response.json()} == {
            s["id"] for s in second_recompute_response.json()
        }

        today_response = client.get("/scores/today")
        assert today_response.status_code == 200
        payload = today_response.json()
        assert len(payload) == 2
        for score in payload:
            assert score["confidence"] in ("high", "medium", "low")
            assert score["tier"] in ("green", "amber", "red")


def test_recompute_rejects_wrong_secret():
    with TestClient(app) as client:
        response = client.post("/admin/recompute", headers={"X-Admin-Secret": "wrong"})
        assert response.status_code == 403
