from services.news_service import fetch_news
from services.article_content_service import fetch_article_content
from services.claim_evaluation_service import evaluate_claim_against_article
from models.schemas import (
    CorroborationResult,
    CorroborationSource,
    CorroborationStatus,
)


async def find_corrobating_articles(
    query: str,
    limit: int = 5,
    exclude_url: str | None = None,
) -> list[dict]:
    """Find candidate articles related to a financial claim."""
    articles = await fetch_news(query=query, max_records=limit)
    original_url = exclude_url.strip() if exclude_url else None

    return [
        article
        for article in articles
        if article["url"] != original_url
    ]


async def collect_corroboration_sources(
    claim: str,
    query: str,
    limit: int = 5,
    exclude_url: str | None = None,
) -> CorroborationResult:
    """Evaluate candidate articles against a claim without treating
    model assessments as definitive verification.
    """
    if not claim.strip():
        raise ValueError("Claim cannot be empty")

    articles = await find_corrobating_articles(
        query=query,
        limit=limit,
        exclude_url=exclude_url,
    )

    sources = []

    for article in articles:
        content = await fetch_article_content(article["url"])
        available = bool(content.strip())

        supports_claim = None
        explanation = "Article content could not be retrieved."

        if available:
            try:
                evaluation = evaluate_claim_against_article(
                    claim=claim,
                    title=article["title"],
                    content=content,
                )

                explanation = evaluation.explanation

                if evaluation.verdict.value == "supports":
                    supports_claim = True
                elif evaluation.verdict.value == "contradicts":
                    supports_claim = False

            except Exception:
                # A failed evaluation must not be counted as evidence
                # supporting or contradicting the claim.
                explanation = (
                    "Claim evaluation failed; this source remains unresolved."
                )

        sources.append(
            CorroborationSource(
                source_name=article.get("source") or "Unknown source",
                url=article["url"],
                supports_claim=supports_claim,
                explanation=explanation,
                content_available=available,
            )
        )

    supporting = sum(
        source.supports_claim is True for source in sources
    )
    contradicting = sum(
        source.supports_claim is False for source in sources
    )

    if supporting == 0 and contradicting == 0:
        status = CorroborationStatus.UNVERIFIED
    elif supporting > 0 and contradicting > 0:
        status = CorroborationStatus.PARTIALLY_CORROBORATED
    elif contradicting > 0:
        status = CorroborationStatus.CONTRADICTED
    elif supporting >= 2:
        status = CorroborationStatus.CORROBORATED
    else:
        status = CorroborationStatus.PARTIALLY_CORROBORATED

    limitations = [
        "Assessments are AI-assisted and do not establish that a claim is true.",
        "Source independence and duplicate reporting have not been verified.",
    ]

    if supporting + contradicting < len(sources):
        limitations.append(
            "Some sources could not be conclusively assessed."
        )

    if supporting < 2:
        limitations.append(
            "Fewer than two sources were assessed as supporting the claim."
        )

    return CorroborationResult(
        claim=claim.strip(),
        status=status,
        sources_checked=len(sources),
        supporting_sources=supporting,
        contradicting_sources=contradicting,
        sources=sources,
        limitations=limitations,
    )
