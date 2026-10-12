import asyncio

from services.article_content_service import fetch_article_content
from services.llm_service import analyze_news

ARTICLE_URL = (
    "https://www.theverge.com/tech/1008422/"
    "apple-macbook-pro-touchscreen-ipad-mini-rumor"
)

ARTICLE_TITLE = (
    "Apple will reportedly debut its first touchscreen MacBook "
    "in three weeks"
)


async def main():
    print("1. Fetching article...")

    content = await fetch_article_content(ARTICLE_URL)
    print("Content length:", len(content))

    if not content:
        print("FAILED: Article content unavailable.")
        return

    print("\n2. Sending article to Gemini...")

    try:
        analysis = analyze_news(
            title=ARTICLE_TITLE,
            content=content,
        )
    except RuntimeError as exc:
        print("Analysis failed:", exc)
        return

    print("\n3. Analysis result")
    print("Event:", analysis.event)

    print("\nClaims:")
    for claim in analysis.claims:
        print("-", claim)

    print("\nSupporting evidence:")
    for evidence in analysis.supporting_evidence:
        print("-", evidence)

    print("\nEvidence match status:", analysis.evidence_match_status)
    print("Evidence status:", analysis.evidence_status)
    print("\nTest finished.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
