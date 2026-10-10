
from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_events_endpoint():
    response = client.get("/events")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_oil_news_matches_scenario():
    response = client.post(
        "/news/analyze",
        json={
            "text": (
                "OPEC announces crude oil supply disruption, "
                "pushing oil prices higher."
            )
        },
    )

    assert response.status_code == 200

    result = response.json()
    assert result["matched"] is True
    assert result["event"]["event_id"] == "event_oil_supply"


def test_unmatched_news_returns_no_event():
    response = client.post(
        "/news/analyze",
        json={
            "text": (
                "A local art exhibition announces its opening "
                "next month with several new paintings."
            )
        },
    )

    assert response.status_code == 200

    result = response.json()
    assert result["matched"] is False
    assert result["event"] is None


def test_short_news_is_rejected():
    response = client.post(
        "/news/analyze",
        json={"text": "Oil"},
    )

    assert response.status_code == 422
