
from datetime import datetime, timezone
from xml.etree import ElementTree

import httpx


GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search"


class NewsServiceError(Exception):
    """Raised when a news feed cannot be fetched or parsed."""


async def fetch_news(
    query: str = "finance OR stock market OR economy",
    max_records: int = 10,
) -> list[dict]:
    """Fetch and normalize news articles from Google News RSS."""

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if not 1 <= max_records <= 50:
        raise ValueError("max_records must be between 1 and 50")

    params = {
        "q": query,
        "hl": "en-IN",
        "gl": "IN",
        "ceid": "IN:en",
    }

    headers = {
        "User-Agent": "FinFlowAI/1.0"
    }

    try:
        async with httpx.AsyncClient(
            timeout=20.0,
            headers=headers,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                GOOGLE_NEWS_RSS_URL,
                params=params,
            )
            response.raise_for_status()

        root = ElementTree.fromstring(response.content)

    except (httpx.HTTPError, ElementTree.ParseError) as exc:
        raise NewsServiceError(
            f"Unable to fetch or parse news feed: {exc}"
        ) from exc

    articles = []

    for item in root.findall("./channel/item")[:max_records]:
        title = item.findtext("title")
        url = item.findtext("link")
        published_at = item.findtext("pubDate")
        source_element = item.find("source")

        if not title or not url:
            continue

        articles.append({
            "title": title.strip(),
            "url": url.strip(),
            "source": (
                source_element.text.strip()
                if source_element is not None and source_element.text
                else None
            ),
            "published_at": published_at,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        })

    return articles
