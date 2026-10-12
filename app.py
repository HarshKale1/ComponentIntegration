from datetime import date

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    AnalysisResponse,
    CorroborationRequest,
    EventGraph,
    EventGraphRequest,
    NewsRequest,
)
from models.impact_schemas import EventImpactRequest

from services.article_content_service import fetch_article_content
from services.corroboration_service import collect_corroboration_sources
from services.event_graph_service import generate_event_graph
from services.event_impact_service import calculate_event_impact
from services.financial_news_analysis_service import fetch_and_analyze_news
from services.llm_service import analyze_news as analyze_news_with_ai
from services.market_data_service import fetch_historical_prices
from services.news_service import fetch_news, NewsServiceError
from services.scenario_service import get_all_events, match_news
from services.stock_service import fetch_quotes, fetch_candles
from services.assistant_service import chat as assistant_chat
from models.schemas import NewsImpactWorkflowRequest
from services.news_impact_workflow_service import run_news_impact_workflow

app = FastAPI(
    title="FinFlow AI",
    description="Financial News Impact Analysis API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Welcome to FinFlow AI",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/events", response_model=list[EventGraph])
def list_events():
    return get_all_events()


@app.post("/news/analyze", response_model=AnalysisResponse)
def analyze_news_endpoint(request: NewsRequest):
    event = match_news(request.text)

    if event is None:
        return AnalysisResponse(
            matched=False,
            event=None,
            message=(
                "No predefined scenario matched this text. "
                "This endpoint uses keyword matching, not AI analysis."
            ),
        )

    return AnalysisResponse(
        matched=True,
        event=event,
        message=(
            "Matched a predefined illustrative scenario using keywords. "
            "This is not verified live-news analysis."
        ),
    )


@app.get("/news")
async def get_news(
    query: str = "finance OR stock market OR economy",
    limit: int = Query(default=10, ge=1, le=50),
):
    try:
        articles = await fetch_news(
            query=query,
            max_records=limit,
        )
        return {
            "count": len(articles),
            "articles": articles,
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except NewsServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/news/ai-analyze")
def ai_analyze_news(request: NewsRequest):
    try:
        result = analyze_news_with_ai(title=request.text)
        return {
            "success": True,
            "analysis": result.model_dump(mode="json"),
        }

    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail="AI news analysis failed. Please try again later.",
        ) from exc


@app.get("/news/analyze-live")
async def analyze_live_news(
    query: str = "finance OR stock market OR economy",
    limit: int = Query(default=5, ge=1, le=10),
):
    try:
        results = await fetch_and_analyze_news(
            query=query,
            limit=limit,
        )
        return {
            "count": len(results),
            "results": results,
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        print(f"Live news analysis failed: {type(exc).__name__}")
        raise HTTPException(
            status_code=502,
            detail="Live news analysis failed. Please try again later.",
        ) from exc


@app.post("/news/corroborate")
async def corroborate_news(request: CorroborationRequest):
    try:
        result = await collect_corroboration_sources(
            claim=request.claim,
            query=request.query,
            limit=request.limit,
            exclude_url=request.exclude_url,
        )
        return result.model_dump(mode="json")

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        print(f"News corroboration failed: {type(exc).__name__}")
        raise HTTPException(
            status_code=502,
            detail="News corroboration failed. Please try again later.",
        ) from exc


@app.post("/news/event-graph")
async def create_event_graph(request: EventGraphRequest):
    try:
        article_content = ""

        if request.url:
            article_content = await fetch_article_content(request.url)

        graph = generate_event_graph(
            headline=request.headline,
            article_content=article_content,
        )
        return graph.model_dump(mode="json")

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail=f"Event graph generation failed: {type(exc).__name__}: {exc}",
        ) from exc



@app.get("/market/history")
def get_market_history(
    ticker: str = Query(min_length=1, max_length=20),
    start_date: date = Query(),
    end_date: date = Query(),
):
    try:
        return fetch_historical_prices(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        print(f"Market history retrieval failed: {type(exc).__name__}")
        raise HTTPException(
            status_code=502,
            detail="Market history retrieval failed.",
        ) from exc


@app.get("/market/event-impact")
def get_market_event_impact(
    ticker: str = Query(min_length=1, max_length=20),
    event_date: date = Query(),
    window_days: int = Query(default=7, ge=1, le=30),
):
    try:
        return calculate_event_impact(
            ticker=ticker,
            event_date=event_date,
            window_days=window_days,
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        print(f"Event impact calculation failed: {type(exc).__name__}")
        raise HTTPException(
            status_code=502,
            detail="Event impact calculation failed.",
        ) from exc


@app.post("/market/analyze-event")
def analyze_market_event(request: EventImpactRequest):
    try:
        impact = calculate_event_impact(
            ticker=request.ticker,
            event_date=request.event_date,
            window_days=request.window_days,
        )
        return {
            "success": True,
            "analysis": impact,
            "message": (
                "Historical price movement calculated. "
                "This does not establish that the event caused the movement."
            ),
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except Exception as exc:
        print(f"Market event analysis failed: {type(exc).__name__}")
        raise HTTPException(
            status_code=502,
            detail="Market event analysis failed.",
        ) from exc
@app.post("/news/impact-workflow")
async def news_impact_workflow(request: NewsImpactWorkflowRequest):
    try:
        result = await run_news_impact_workflow(request)
        return result.model_dump(mode="json")

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(f"News impact workflow failed: {type(exc).__name__}")
        raise HTTPException(
            status_code=502,
            detail="News impact workflow failed. Please try again later.",
        ) from exc

# ---------- Stock market endpoints (Yahoo Finance via yfinance) ----------

from fastapi import Query as _Query

DEFAULT_SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "AAPL", "MSFT", "GOOGL", "TSLA", "NVDA",
    "^NSEI", "^GSPC", "^DJI",
]


@app.get("/market/quotes")
def get_market_quotes(
    symbols: str = _Query(
        default="",
        description="Comma-separated list of Yahoo Finance tickers. Empty = default set.",
    ),
):
    if symbols.strip():
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
    else:
        sym_list = DEFAULT_SYMBOLS

    if len(sym_list) > 25:
        raise HTTPException(status_code=400, detail="Too many symbols (max 25).")

    try:
        return {"quotes": fetch_quotes(sym_list)}
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Quote fetch failed: {type(exc).__name__}: {exc}",
        ) from exc


@app.get("/market/candles")
def get_market_candles(
    symbol: str = _Query(min_length=1, max_length=20),
    days: int = _Query(default=30, ge=5, le=365),
):
    try:
        return fetch_candles(symbol=symbol, days=days)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Candle fetch failed: {type(exc).__name__}: {exc}",
        ) from exc
# ---------- AI assistant endpoint ----------

from pydantic import BaseModel as _BaseModel, Field as _Field


class AssistantRequest(_BaseModel):
    message: str = _Field(min_length=1, max_length=1000)


@app.post("/assistant/chat")
def assistant_chat_endpoint(request: AssistantRequest):
    try:
        result = assistant_chat(request.message)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=502,
            detail=f"Assistant failed: {type(exc).__name__}: {exc}",
        ) from exc