from google.genai import types
import json
import re
import uuid

from pydantic import ValidationError

from models.schemas import EventGraph
from services.llm_service import client, MODEL_NAME

def _clean_headline(headline: str) -> str:
    """Strip common news-feed suffixes that confuse the LLM."""
    if not headline:
        return headline
    h = headline.strip()
    # Remove trailing " - Source Name"
    import re as _re
    h = _re.sub(r"\s*[-|]\s*[^-|]{0,60}$", "", h)
    # Remove anything after a pipe
    if "|" in h:
        h = h.split("|", 1)[0]
    # Strip common Google News noise
    for noise in ["- Google News", "| Google News", "- Yahoo Finance",
                  "- Reuters", "- CNBC", "- Bloomberg", "- WSJ"]:
        if h.endswith(noise):
            h = h[: -len(noise)]
    return h.strip()




def normalize_limitations(obj):
    """
    Ensure every limitations field is a list of strings.
    Handles both graph-level and edge-level limitations.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == "limitations":
                if isinstance(value, str):
                    obj[key] = [value] if value.strip() else []
                elif isinstance(value, list):
                    obj[key] = [
                        item.strip()
                        for item in value
                        if isinstance(item, str) and item.strip()
                    ]
                else:
                    obj[key] = []
            else:
                normalize_limitations(value)

    elif isinstance(obj, list):
        for item in obj:
            normalize_limitations(item)


def extract_json(output: str) -> dict:
    """
    Parse JSON returned by the model.
    Supports plain JSON and JSON wrapped in Markdown fences.
    """
    if not output or not output.strip():
        raise RuntimeError("Gemini returned an empty event graph.")

    output = output.strip()

    # Remove optional Markdown code fences.
    output = re.sub(
        r"^\s*```(?:json)?\s*",
        "",
        output,
        flags=re.IGNORECASE,
    )
    output = re.sub(r"\s*```\s*$", "", output)

    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        # Recover a JSON object if the model added text around it.
        start = output.find("{")
        end = output.rfind("}")

        if start == -1 or end <= start:
            raise RuntimeError(
                "Gemini did not return a valid JSON object."
            )

        try:
            data = json.loads(output[start:end + 1])
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Gemini returned invalid JSON: {exc}"
            ) from exc

    if not isinstance(data, dict):
        raise RuntimeError(
            "Gemini returned an invalid graph: expected a JSON object."
        )

    return data


def generate_event_graph(
    headline: str,
    article_content: str = "",
    source_url: str | None = None,
) -> EventGraph:
    """
    Generate and validate a financial event-impact graph.

    Article content may be empty when a publisher blocks extraction.
    The headline is still supplied to the model.
    """

    if not isinstance(headline, str) or not headline.strip():
        raise ValueError("Headline cannot be empty.")

    headline = _clean_headline(headline)
    article_content = (
        article_content.strip()
        if isinstance(article_content, str)
        else ""
    )

    # An unavailable article body should not stop graph generation.
    if not article_content:
        article_content = (
            "The full article text could not be retrieved. "
            "Use the headline only, avoid unsupported factual claims, "
            "and explicitly identify uncertainty in the graph limitations."
        )

    source_url = source_url.strip() if source_url else None
    prompt = f"""
Create a financial event-impact graph from the supplied news source.

HEADLINE:
{headline}

SOURCE URL:
{source_url or "Unavailable"}

ARTICLE CONTENT:
{article_content[:10000]}

Return one valid JSON object with these fields:
- event_id: unique string identifier
- headline: event headline
- event_type: one of COMMODITY_SUPPLY, CENTRAL_BANK_RATE,
  INFLATION, GEOPOLITICAL, OTHER
- summary: concise event summary
- source: supplied source URL, or null if unavailable
- nodes: list of graph nodes
- edges: list of graph edges
- limitations: list of strings

Each node must contain:
- node_id
- label
- node_type
- description

Allowed node_type values:
COMMODITY, INDICATOR, COUNTRY, SECTOR, COMPANY, ASSET

Each edge must contain:
- edge_id
- source_node_id
- target_node_id
- relationship
- strength
- direction
- explanation
- evidence_type
- evidence
- limitations

Allowed direction values:
POSITIVE, NEGATIVE, MIXED, UNKNOWN

Allowed evidence_type values:
VERIFIED_SOURCE, ESTABLISHED_RELATIONSHIP, HYPOTHESIS,
INSUFFICIENT_VERIFIED_EVIDENCE

Each evidence item must contain:
- evidence_id
- source_name
- url
- published_at
- claim

GRAPH COMPLETENESS REQUIREMENT (important):
Produce a graph that traces the event's economic propagation chain,
not just its immediate effect. Aim for 8 to 14 nodes and 8 to 14 edges.

Include, when economically relevant to this event:
1. The primary commodity, asset, or indicator directly affected.
2. At least 2-3 affected sectors (for example: Energy, Transportation,
   Manufacturing, Banking, Real Estate, Consumer Goods, Technology).
3. At least 2-3 countries with different exposure profiles: a directly
   involved country, a major importer, and a diversified economy.
4. At least 1-2 downstream indicators (Inflation Expectations,
   Interest Rate Expectations, Currency, GDP Growth).
5. Follow-on sectors that respond to those indicators
   (for example: Banking and Real Estate respond to rate expectations).

Do NOT stop at 2 nodes when a clear economic propagation chain exists.
A node may be included even if its relationship is a well-known economic
mechanism rather than an article-specific fact, as long as the edge is
marked with an appropriate evidence_type and carries limitations.

Evidence rules (still strict):
- Never invent sources, quotations, URLs, publication dates, or evidence.
- Use VERIFIED_SOURCE only when the article content itself supports the
  specific relationship.
- Use ESTABLISHED_RELATIONSHIP for widely recognised economic mechanisms
  (for example: higher energy prices raise transport costs, or higher
  inflation expectations raise rate expectations) even without
  article-specific evidence. Provide a short explanation and at least
  one limitation on such edges.
- Use HYPOTHESIS for plausible but unverified relationships.
  Every HYPOTHESIS edge must include at least one limitation.
- Use INSUFFICIENT_VERIFIED_EVIDENCE only when the mechanism itself is
  unclear or unsupported; do not use it as a reason to omit a node.
- The evidence list may be empty on ESTABLISHED_RELATIONSHIP and
  HYPOTHESIS edges.

Other rules:
- Include only financial relationships relevant to this event.
- Use the supplied source URL for the graph source when available.
- Distinguish source-reported facts from inferred market effects.
- If the article body is unavailable, state this limitation clearly.
- Do not present a headline alone as proof of an event's details.
- Set strength between 0 and 1. It represents estimated relationship
  strength, not the probability of a market outcome.
- Every edge must reference existing node IDs.
- Node IDs and edge IDs must be unique.
- Do not make guaranteed price predictions.
- Every edge's limitations must be a JSON list of strings.
- The graph's limitations must be a JSON list of strings.
- Return JSON only, without Markdown fences.
- Return empty nodes or edges only if no defensible relationships
  can be identified at all.
- Use a unique event_id for this graph.

The JSON must match the application's graph schema.
"""

    output = None
    last_error = None
    for attempt in range(2):  # try twice
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    max_output_tokens=8192,
                ),
            )
            candidate = getattr(response, "text", None)
            if candidate and candidate.strip():
                output = candidate
                break
            last_error = "empty response"
        except Exception as exc:
            last_error = str(exc)

    if not output:
        raise RuntimeError(f"Graph generation failed after 2 attempts: {last_error}")

    data = extract_json(output or "")

    # Supply safe defaults for fields that can be derived reliably.
    data.setdefault("event_id", str(uuid.uuid4()))
    data.setdefault("headline", headline)
    data.setdefault("source", source_url)
    data.setdefault("nodes", [])
    data.setdefault("edges", [])
    data.setdefault("limitations", [])

    # Prefer the actual headline and URL supplied by the application.
    data["headline"] = headline

    if source_url:
        data["source"] = source_url

    if not article_content or article_content.startswith(
        "The full article text could not be retrieved."
    ):
        limitations = data.get("limitations")

        if not isinstance(limitations, list):
            limitations = []

        limitations.append(
            "Full article text was unavailable; graph generation "
            "relied on the headline and may lack verified evidence."
        )
        data["limitations"] = limitations

    normalize_limitations(data)

    # Validate that the generated graph matches the application's schema.
    try:
        graph = EventGraph.model_validate(data)
    except ValidationError as exc:
        print(
            "GRAPH VALIDATION ERRORS:",
            json.dumps(exc.errors(), indent=2, default=str),
        )
        raise RuntimeError(
            "Generated graph does not match the EventGraph schema. "
            "Check the backend terminal for GRAPH VALIDATION ERRORS."
        ) from exc

    return graph
