from starlette.concurrency import run_in_threadpool

from models.schemas import (
    NewsImpactWorkflowRequest,
    NewsImpactWorkflowResponse,
)
from services.article_content_service import fetch_article_content
from services.event_graph_service import generate_event_graph
from services.event_impact_service import calculate_event_impact
from services.news_service import fetch_news


async def run_news_impact_workflow(
    request: NewsImpactWorkflowRequest,
) -> NewsImpactWorkflowResponse:
    """Fetch news, generate an event graph, and optionally analyze prices."""

    articles = await fetch_news(
        query=request.query,
        max_records=request.limit,
    )

    if not articles:
        raise ValueError("No news articles were found for this query")

    article = articles[0]

    content = await fetch_article_content(article["url"])

    # Gemini is called synchronously, so keep it off the event loop.
    graph = await run_in_threadpool(
        generate_event_graph,
        headline=article["title"],
        article_content=content,
    )

    market_impact = None

    if request.ticker and request.event_date:
        # yfinance and the price calculation are synchronous as well.
        market_impact = await run_in_threadpool(
            calculate_event_impact,
            ticker=request.ticker,
            event_date=request.event_date,
            window_days=request.window_days,
        )

    limitations = [
        "The first article returned by the provider was selected.",
        "Extracted article content may be incomplete or unavailable.",
        "AI-generated graph relationships are not automatically verified facts.",
        "Historical price movements do not establish that an event caused them.",
        "The supplied event date may differ from the article publication date.",
    ]

    if not content:
        limitations.append(
            "No article content was extracted; graph generation used the headline."
        )

    return NewsImpactWorkflowResponse(
        success=True,
        article=article,
        content_length=len(content),
        event_graph=graph,
        market_impact=market_impact,
        limitations=limitations,
    )
