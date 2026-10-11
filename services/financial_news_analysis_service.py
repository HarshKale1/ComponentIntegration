from services.news_service import fetch_news
from services.llm_service import analyze_news
from services.article_content_service import fetch_article_content


async def fetch_and_analyze_news(
    query: str = "finance OR stock market OR economy",
    limit: int = 5,
) -> list[dict]:
    """Fetch news articles, extract their content, and analyze them."""

    articles = await fetch_news(
        query=query,
        max_records=limit,
    )

    results = []

    for article in articles:
        content = await fetch_article_content(article["url"])

        analysis = analyze_news(
            title=article["title"],
            content=content,
        )

        results.append({
            "article": article,
            "content_length": len(content),
            "analysis": analysis.model_dump(mode="json"),
        })

    return results
