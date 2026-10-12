from datetime import date
from unittest.mock import AsyncMock

import pytest

import services.news_impact_workflow_service as workflow_service
from models.schemas import (
    EventGraph,
    EventType,
    NewsImpactWorkflowRequest,
)


@pytest.fixture
def request_data():
    return NewsImpactWorkflowRequest(
        query="RBI repo rate",
        limit=5,
    )


@pytest.fixture
def sample_article():
    return {
        "title": "RBI changes repo rate",
        "url": "https://example.com/article",
        "source": "Example News",
        "published_at": "2026-10-10",
        "fetched_at": "2026-10-10T10:00:00+00:00",
    }


@pytest.fixture
def sample_graph():
    return EventGraph(
        event_id="event-1",
        headline="RBI changes repo rate",
        event_type=EventType.CENTRAL_BANK_RATE,
        summary="The RBI announced a repo rate decision.",
        nodes=[],
        edges=[],
    )


@pytest.mark.asyncio
async def test_workflow_returns_graph_without_market_impact(
    monkeypatch, request_data, sample_article, sample_graph
):
    monkeypatch.setattr(
        workflow_service,
        "fetch_news",
        AsyncMock(return_value=[sample_article]),
    )
    monkeypatch.setattr(
        workflow_service,
        "fetch_article_content",
        AsyncMock(return_value="Article text"),
    )
    monkeypatch.setattr(
        workflow_service,
        "generate_event_graph",
        lambda **kwargs: sample_graph,
    )

    result = await workflow_service.run_news_impact_workflow(request_data)

    assert result.success is True
    assert result.article["title"] == sample_article["title"]
    assert result.content_length == len("Article text")
    assert result.event_graph.event_id == "event-1"
    assert result.market_impact is None
    assert result.limitations


@pytest.mark.asyncio
async def test_workflow_rejects_empty_news(monkeypatch, request_data):
    monkeypatch.setattr(
        workflow_service,
        "fetch_news",
        AsyncMock(return_value=[]),
    )

    with pytest.raises(ValueError, match="No news articles"):
        await workflow_service.run_news_impact_workflow(request_data)


@pytest.mark.asyncio
async def test_workflow_uses_headline_when_content_is_unavailable(
    monkeypatch, request_data, sample_article, sample_graph
):
    graph_calls = []

    monkeypatch.setattr(
        workflow_service,
        "fetch_news",
        AsyncMock(return_value=[sample_article]),
    )
    monkeypatch.setattr(
        workflow_service,
        "fetch_article_content",
        AsyncMock(return_value=""),
    )

    def fake_generate_event_graph(**kwargs):
        graph_calls.append(kwargs)
        return sample_graph

    monkeypatch.setattr(
        workflow_service,
        "generate_event_graph",
        fake_generate_event_graph,
    )

    result = await workflow_service.run_news_impact_workflow(request_data)

    assert result.content_length == 0
    assert graph_calls[0]["headline"] == sample_article["title"]
    assert graph_calls[0]["article_content"] == ""
    assert any(
        "No article content" in item
        for item in result.limitations
    )


@pytest.mark.asyncio
async def test_workflow_calculates_market_impact_when_requested(
    monkeypatch, sample_article, sample_graph
):
    request = NewsImpactWorkflowRequest(
        query="RBI repo rate",
        limit=5,
        ticker="^NSEI",
        event_date=date(2026, 10, 10),
        window_days=5,
    )
    impact = {"change_percent": 1.2}
    impact_calls = []

    monkeypatch.setattr(
        workflow_service,
        "fetch_news",
        AsyncMock(return_value=[sample_article]),
    )
    monkeypatch.setattr(
        workflow_service,
        "fetch_article_content",
        AsyncMock(return_value="Article text"),
    )
    monkeypatch.setattr(
        workflow_service,
        "generate_event_graph",
        lambda **kwargs: sample_graph,
    )

    def fake_calculate_event_impact(**kwargs):
        impact_calls.append(kwargs)
        return impact

    monkeypatch.setattr(
        workflow_service,
        "calculate_event_impact",
        fake_calculate_event_impact,
    )

    result = await workflow_service.run_news_impact_workflow(request)

    assert result.market_impact == impact
    assert impact_calls[0]["ticker"] == "^NSEI"
    assert impact_calls[0]["event_date"] == date(2026, 10, 10)
    assert impact_calls[0]["window_days"] == 5
