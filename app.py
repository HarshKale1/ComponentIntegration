
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import NewsRequest, AnalysisResponse, EventGraph
from services.scenario_service import get_all_events, match_news


app = FastAPI(
    title="FinFlow AI",
    description="Financial News Impact Analysis API",
    version="1.0.0"
)

# Allow requests from the frontend development server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def home():
    return {
        "message": "Welcome to FinFlow AI",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/events", response_model=list[EventGraph])
def list_events():
    return get_all_events()


@app.post("/news/analyze", response_model=AnalysisResponse)
def analyze_news(request: NewsRequest):
    event = match_news(request.text)

    if event is None:
        return AnalysisResponse(
            matched=False,
            event=None,
            message=(
                "No predefined scenario matched this text. "
                "This MVP uses keyword matching, not live AI analysis."
            )
        )

    return AnalysisResponse(
        matched=True,
        event=event,
        message=(
            "Matched a predefined illustrative scenario using keywords. "
            "This is not verified live-news analysis."
        )
    )
