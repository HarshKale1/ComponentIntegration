
import pytest
from unittest.mock import AsyncMock, patch

from services.corroboration_service import find_corrobating_articles


@pytest.mark.asyncio
async def test_finds_related_articles():
    mock_articles = [
        {"title": "Original article", "url": "https://example.com/1"},
        {"title": "Another report", "url": "https://example.com/2"},
    ]

    with patch(
        "services.corroboration_service.fetch_news",
        new_callable=AsyncMock,
        return_value=mock_articles,
    ):
        result = await find_corrobating_articles(
            query="RBI interest rate",
            limit=5,
            exclude_url="https://example.com/1",
        )

    assert len(result) == 1
    assert result[0]["title"] == "Another report"


@pytest.mark.asyncio
async def test_returns_articles_when_no_url_excluded():
    mock_articles = [
        {"title": "Report A", "url": "https://example.com/1"},
        {"title": "Report B", "url": "https://example.com/2"},
    ]

    with patch(
        "services.corroboration_service.fetch_news",
        new_callable=AsyncMock,
        return_value=mock_articles,
    ):
        result = await find_corrobating_articles(
            query="stock market",
            limit=5,
        )

    assert len(result) == 2
