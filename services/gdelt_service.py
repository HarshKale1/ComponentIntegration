
from typing import Any

import httpx


GDELT_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


class GDELTServiceError(Exception):
    """Raised when GDELT cannot return usable news data."""


async def fetch_news(
    query: str = "finance",
    timespan: str = "1d",
    max_records: int = 10,
) -> list[dict[str, Any]]:
    """Fetch and normalize recent articles from GDELT."""

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if not 1 <= max_records <= 50:
        raise ValueError("max_records must be between 1 and 50")

    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "timespan": timespan,
        "maxrecords": max_records,
        "sort": "datedesc",
    }

    headers = {
        "User-Agent": "FinFlowAI/1.0"
    }

    try:
        async with httpx.AsyncClient(
            timeout=30.0,
            headers=headers,
        ) as client:
            response = await client.get(
                GDELT_API_URL,
                params=params,
            )
            response.raise_for_status()
            payload = response.json()

    except (httpx.HTTPError, ValueError) as exc:
        raise GDELTServiceError(
            f"GDELT request failed: {exc}"
        ) from exc

    if not isinstance(payload, dict):
        raise GDELTServiceError(
            "GDELT returned an unexpected response"
        )

    raw_articles = payload.get("articles", [])

    if not isinstance(raw_articles, list):
        raise GDELTServiceError(
            "GDELT article list has an invalid format"
        )

    articles = []

    for article in raw_articles:
        if not isinstance(article, dict):
            continue

        title = article.get("title")
        url = article.get("url")

        if not isinstance(title, str) or not title.strip():
            continue

        if not isinstance(url, str):
            continue

        if not url.startswith(("http://", "https://")):
            continue

        articles.append({
            "title": title.strip(),
            "url": url,
            "source": article.get("domain"),
            "published_at": article.get("seendate"),
            "language": article.get("language"),
            "source_country": article.get("sourcecountry"),
        })

    return articles
