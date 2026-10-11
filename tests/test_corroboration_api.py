
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app import app
from models.schemas import (
    CorroborationResult,
    CorroborationStatus,
)

client = TestClient(app)


def make_result():
    return CorroborationResult(
        claim="The RBI announced a policy update.",
        status=CorroborationStatus.UNVERIFIED,
        sources_checked=1,
        supporting_sources=0,
        contradicting_sources=0,
        sources=[
            {
                "source_name": "Example News",
                "url": "https://example.com/rbi",
                "supports_claim": None,
                "explanation": "Evidence remains inconclusive.",
                "content_available": True,
            }
        ],
        limitations=["Source independence has not been verified."],
    )


def test_corroboration_endpoint_success():
    with patch(
        "app.collect_corroboration_sources",
        new_callable=AsyncMock,
        return_value=make_result(),
    ) as mock_service:
        response = client.post(
            "/news/corroborate",
            json={
                "claim": "The RBI announced a policy update.",
                "query": "RBI policy update",
                "limit": 5,
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unverified"
    assert data["sources_checked"] == 1
    assert data["sources"][0]["source_name"] == "Example News"
    mock_service.assert_awaited_once()


def test_corroboration_endpoint_uses_default_limit():
    with patch(
        "app.collect_corroboration_sources",
        new_callable=AsyncMock,
        return_value=make_result(),
    ) as mock_service:
        response = client.post(
            "/news/corroborate",
            json={
                "claim": "The RBI announced a policy update.",
                "query": "RBI policy update",
            },
        )

    assert response.status_code == 200
    assert mock_service.await_args.kwargs["limit"] == 5


def test_corroboration_endpoint_rejects_short_claim():
    response = client.post(
        "/news/corroborate",
        json={
            "claim": "RBI",
            "query": "RBI policy update",
        },
    )

    assert response.status_code == 422


def test_corroboration_endpoint_rejects_invalid_limit():
    response = client.post(
        "/news/corroborate",
        json={
            "claim": "The RBI announced a policy update.",
            "query": "RBI policy update",
            "limit": 11,
        },
    )

    assert response.status_code == 422


def test_corroboration_endpoint_handles_value_error():
    with patch(
        "app.collect_corroboration_sources",
        new_callable=AsyncMock,
        side_effect=ValueError("Invalid claim"),
    ):
        response = client.post(
            "/news/corroborate",
            json={
                "claim": "The RBI announced a policy update.",
                "query": "RBI policy update",
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid claim"


def test_corroboration_endpoint_hides_unexpected_error_details():
    with patch(
        "app.collect_corroboration_sources",
        new_callable=AsyncMock,
        side_effect=RuntimeError("Sensitive internal detail"),
    ):
        response = client.post(
            "/news/corroborate",
            json={
                "claim": "The RBI announced a policy update.",
                "query": "RBI policy update",
            },
        )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "News corroboration failed. Please try again later."
    )
    assert "Sensitive internal detail" not in response.text
