"""
AI assistant service.

Classifies a user's message into one of several intents and returns a short
reply plus an optional navigation action for the frontend.
"""
from __future__ import annotations

import json
import re
from typing import Any

from google.genai import types

from services.llm_service import client, MODEL_NAME


SYSTEM_PROMPT = """
You are the FinFlow AI assistant inside a market-impact dashboard.

The dashboard has these views:
- home           (impact graph, country impact, sectors, assets, relationships, evidence)
- stocks         (live stock prices)
- events
- watchlist
- history
- reports
- settings

The dashboard can be driven by the user's message. Your job:

1. Classify the user's message into exactly ONE intent:
   - NAVIGATE_STOCK     : user wants a specific stock / company / ticker
   - NAVIGATE_TAB       : user wants to open a tab (country, sectors, assets, relationships, evidence)
   - BUILD_GRAPH        : user describes an event/headline and wants its impact graph
   - EXPLAIN            : user asks a market/economics question, no navigation
   - NAVIGATE_VIEW      : user wants to go to a top-level view (stocks, events, home, settings, watchlist, history, reports)
   - CHAT               : anything else

2. Return the reply as a SHORT summary followed by 2-4 bullet points using "- " for each bullet.
   Keep the reply under 900 characters. Do not use markdown headings.

3. Return an "action" object only when navigation is intended:
   - NAVIGATE_STOCK  -> {"type":"navigate_stock", "symbol":"<TICKER>"}
       Use Yahoo Finance tickers: US = plain (AAPL), India = suffix .NS (RELIANCE.NS).
       If the user names a company without a ticker, pick the most likely ticker.
   - NAVIGATE_TAB    -> {"type":"navigate_tab", "tab":"country|sectors|assets|rels|evid|graph"}
   - BUILD_GRAPH     -> {"type":"build_graph", "headline":"<short headline>", "url":null}
   - NAVIGATE_VIEW   -> {"type":"navigate_view", "view":"stocks|events|home|settings|watchlist|history|reports"}
   - EXPLAIN or CHAT -> {"type":"none"}

Return ONLY a valid JSON object matching this schema:

{
  "intent": "NAVIGATE_STOCK | NAVIGATE_TAB | BUILD_GRAPH | EXPLAIN | NAVIGATE_VIEW | CHAT",
  "reply": "short reply text with bullets",
  "action": { ... }  or  {"type":"none"}
}

Rules:
- Never invent market numbers, prices, or dates.
- If the user asks about an event's impact, use BUILD_GRAPH with a concise headline.
- If the user asks a general question about how events propagate, use EXPLAIN and give
  a short chain of transmission (commodity -> sectors -> indicators -> follow-on sectors).
- Keep replies factual and clearly separate observed facts from hypotheses.
- If you are unsure of the intent, use CHAT and answer helpfully.
"""


def _extract_json(text: str) -> dict:
    """Parse Gemini's JSON response, tolerating code fences."""
    if not text:
        raise RuntimeError("Assistant returned empty response.")

    t = text.strip()
    t = re.sub(r"^\s*```(?:json)?\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*```\s*$", "", t)

    try:
        return json.loads(t)
    except json.JSONDecodeError:
        # Recover the JSON object if the model added text around it.
        start = t.find("{")
        end = t.rfind("}")
        if start == -1 or end <= start:
            raise RuntimeError("Assistant did not return a JSON object.")
        return json.loads(t[start:end + 1])


ALLOWED_TABS = {"country", "sectors", "assets", "rels", "evid", "graph"}
ALLOWED_VIEWS = {"home", "stocks", "events", "settings", "watchlist", "history", "reports"}


def _sanitize_action(action: Any) -> dict:
    """Ensure the action is one of the whitelisted types and values."""
    if not isinstance(action, dict):
        return {"type": "none"}

    t = action.get("type", "none")

    if t == "navigate_stock":
        sym = str(action.get("symbol", "")).strip().upper()
        if not sym or len(sym) > 20:
            return {"type": "none"}
        return {"type": "navigate_stock", "symbol": sym}

    if t == "navigate_tab":
        tab = str(action.get("tab", "")).strip()
        if tab not in ALLOWED_TABS:
            return {"type": "none"}
        return {"type": "navigate_tab", "tab": tab}

    if t == "navigate_view":
        v = str(action.get("view", "")).strip()
        if v not in ALLOWED_VIEWS:
            return {"type": "none"}
        return {"type": "navigate_view", "view": v}

    if t == "build_graph":
        headline = str(action.get("headline", "")).strip()[:300]
        if not headline:
            return {"type": "none"}
        return {
            "type": "build_graph",
            "headline": headline,
            "url": action.get("url") if isinstance(action.get("url"), str) else None,
        }

    return {"type": "none"}


def chat(user_message: str) -> dict:
    """Send the user message to Gemini and return {intent, reply, action}."""
    user_message = (user_message or "").strip()
    if not user_message:
        raise ValueError("Message cannot be empty.")
    if len(user_message) > 1000:
        user_message = user_message[:1000]

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=SYSTEM_PROMPT + "\n\nUSER MESSAGE:\n" + user_message,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=2048,
            ),
        )
    except Exception as exc:
        raise RuntimeError(f"Assistant request failed: {exc}") from exc

    text = getattr(response, "text", None)
    data = _extract_json(text or "")

    intent = str(data.get("intent", "CHAT")).strip().upper()
    if intent not in {"NAVIGATE_STOCK", "NAVIGATE_TAB", "BUILD_GRAPH",
                      "EXPLAIN", "NAVIGATE_VIEW", "CHAT"}:
        intent = "CHAT"

    reply = str(data.get("reply", "")).strip() or "I could not generate a reply."
    action = _sanitize_action(data.get("action"))

    return {"intent": intent, "reply": reply, "action": action}