
from services.llm_service import analyze_news

result = analyze_news(
    title="RBI cuts repo rate by 0.25 percentage points",
    content=(
        "The Reserve Bank of India announced a rate cut. "
        "The effects on lending, demand, and markets may vary."
    ),
)

print(result)
