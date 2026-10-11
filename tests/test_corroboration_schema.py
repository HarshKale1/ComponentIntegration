
import pytest
from pydantic import ValidationError

from models.schemas import (
    CorroborationResult,
    CorroborationStatus,
    CorroborationSource,
)


def test_default_status_is_unverified():
    result = CorroborationResult(
        claim="The RBI changed its policy rate",
        sources_checked=0,
        supporting_sources=0,
        contradicting_sources=0,
    )

    assert result.status == CorroborationStatus.UNVERIFIED
    assert result.sources == []


def test_accepts_source_details():
    source = CorroborationSource(
        source_name="Example News",
        url="https://example.com/news",
        supports_claim=True,
        explanation="The article reports the same announcement.",
        content_available=True,
    )

    result = CorroborationResult(
        claim="The RBI changed its policy rate",
        status=CorroborationStatus.PARTIALLY_CORROBORATED,
        sources_checked=1,
        supporting_sources=1,
        contradicting_sources=0,
        sources=[source],
    )

    assert result.sources[0].source_name == "Example News"
    assert result.supporting_sources == 1


def test_rejects_negative_source_counts():
    with pytest.raises(ValidationError):
        CorroborationResult(
            claim="A financial claim",
            sources_checked=-1,
            supporting_sources=0,
            contradicting_sources=0,
        )
