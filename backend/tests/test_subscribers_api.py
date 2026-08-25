from fastapi.testclient import TestClient

from app.main import app


def test_whatsapp_subscription_requires_a_school(seeded_schools):
    with TestClient(app) as client:
        response = client.post(
            "/subscribers", json={"channel": "whatsapp", "contact": "+923001234567"}
        )
    assert response.status_code == 422


def test_whatsapp_subscription_with_school_succeeds(seeded_schools):
    school = seeded_schools[0]
    with TestClient(app) as client:
        response = client.post(
            "/subscribers",
            json={"school_id": school.id, "channel": "whatsapp", "contact": "+923001234567"},
        )
    assert response.status_code == 201
    body = response.json()
    assert body["school_id"] == school.id
    assert body["channel"] == "whatsapp"


def test_sms_subscription_without_school_is_allowed(seeded_schools):
    with TestClient(app) as client:
        response = client.post(
            "/subscribers", json={"channel": "sms", "contact": "+923001234567"}
        )
    assert response.status_code == 201
    assert response.json()["school_id"] is None


def test_subscription_for_unknown_school_returns_404(seeded_schools):
    with TestClient(app) as client:
        response = client.post(
            "/subscribers",
            json={"school_id": 999999, "channel": "whatsapp", "contact": "+923001234567"},
        )
    assert response.status_code == 404


def test_subscription_with_invalid_contact_is_rejected(seeded_schools):
    school = seeded_schools[0]
    with TestClient(app) as client:
        response = client.post(
            "/subscribers",
            json={"school_id": school.id, "channel": "whatsapp", "contact": "not-a-number"},
        )
    assert response.status_code == 422
