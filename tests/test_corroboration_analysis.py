import pytest
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace

from models.schemas import CorroborationStatus
from services.corroboration_service import collect_corroboration_sources


@pytest.mark.asyncio
async def test_collects_sources_but_keeps_claim_unverified():
    articles = [
        {
            "title": "RBI policy update",
            "url": "https://example.com/rbi",
            "source": "Example News",
        }
    ]

    fake_evaluation = SimpleNamespace(
        verdict=SimpleNamespace(value="unclear"),
        explanation="The evidence is inconclusive.",
    )

    with (
        patch(
            "services.corroboration_service.find_corrobating_articles",
            new_callable=AsyncMock,
            return_value=articles,
        ),
        patch(
            "services.corroboration_service.fetch_article_content",
            new_callable=AsyncMock,
            return_value="The RBI announced a policy update.",
        ),
        patch(
            "services.corroboration_service.evaluate_claim_against_article",
            return_value=fake_evaluation,
        ) as mock_evaluator,
    ):
        result = await collect_corroboration_sources(
            claim="The RBI announced a policy update.",
            query="RBI policy update",
        )

    mock_evaluator.assert_called_once()

    assert result.status == CorroborationStatus.UNVERIFIED
    assert result.sources_checked == 1
    assert result.sources[0].content_available is True
    assert result.sources[0].supports_claim is None
    assert result.supporting_sources == 0
    assert result.contradicting_sources == 0
    assert result.sources[0].explanation == "The evidence is inconclusive."


@pytest.mark.asyncio
async def test_empty_claim_is_rejected():
    with pytest.raises(ValueError, match="Claim cannot be empty"):
        await collect_corroboration_sources(
            claim=" ",
            query="RBI policy update",
        )
