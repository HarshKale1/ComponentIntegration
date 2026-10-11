
import json
from pathlib import Path

from models.schemas import EventGraph


BASE_DIR = Path(__file__).resolve().parent.parent
SCENARIOS_FILE = BASE_DIR / "data" / "scenarios.json"


def _load_scenarios() -> list[dict]:
    with SCENARIOS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_all_events() -> list[EventGraph]:
    """Load scenarios, excluding service-only keywords."""
    events = []

    for scenario in _load_scenarios():
        event_data = {
            key: value
            for key, value in scenario.items()
            if key != "keywords"
        }
        events.append(EventGraph.model_validate(event_data))

    return events


def match_news(text: str) -> EventGraph | None:
    """Match text against keywords in demonstration scenarios."""
    normalized_text = text.casefold()
    best_event = None
    best_score = 0

    for scenario in _load_scenarios():
        keywords = scenario.get("keywords", [])
        score = sum(
            1
            for keyword in keywords
            if keyword.casefold() in normalized_text
        )

        if score > best_score:
            best_score = score
            best_event = scenario

    if best_event is None:
        return None

    event_data = {
        key: value
        for key, value in best_event.items()
        if key != "keywords"
    }

    return EventGraph.model_validate(event_data)
