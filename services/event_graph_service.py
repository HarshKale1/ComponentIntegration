
import json
import re

from pydantic import ValidationError

from models.schemas import EventGraph
from services.llm_service import client, MODEL_NAME


def generate_event_graph(
    headline: str,
    article_content: str = "",
) -> EventGraph:
    """Generate a validated financial event-impact graph."""

    if not headline.strip():
        raise ValueError("Headline cannot be empty")

    prompt = f"""
Create a financial event-impact graph from the supplied source.

HEADLINE:
{headline}

ARTICLE CONTENT:
{article_content[:10000]}

Return valid JSON with these fields:
- event_id: unique string identifier
- headline: event headline
- event_type: one of COMMODITY_SUPPLY, CENTRAL_BANK_RATE,
  INFLATION, GEOPOLITICAL, OTHER
- summary: concise event summary
- source: source URL or null if unavailable
- nodes: list of graph nodes
- edges: list of graph edges
- limitations: list of limitations

Each node must contain:
node_id, label, node_type, description

Allowed node_type values:
COMMODITY, INDICATOR, COUNTRY, SECTOR, COMPANY, ASSET

Each edge must contain:
edge_id, source_node_id, target_node_id, relationship,
strength, direction, explanation, evidence_type, evidence, limitations

Allowed direction values:
POSITIVE, NEGATIVE, MIXED, UNKNOWN

Allowed evidence_type values:
VERIFIED_SOURCE, ESTABLISHED_RELATIONSHIP, HYPOTHESIS,
INSUFFICIENT_VERIFIED_EVIDENCE

Each evidence item must contain:
evidence_id, source_name, url, published_at, claim

Use null for unavailable optional source fields.

Rules:
1. Include only relationships relevant to the event.
2. Never invent quotations, sources, URLs, or publication dates.
3. Distinguish source-reported facts from inferred market effects.
4. Mark inferred relationships as HYPOTHESIS and explain their limitations.
5. Use INSUFFICIENT_VERIFIED_EVIDENCE when evidence is inadequate.
6. Do not attach evidence to an edge unless it is actually available
   in the supplied source.
7. Use strength between 0 and 1 as an estimate of relationship strength,
   not a probability that a market outcome will occur.
8. Every edge must reference node IDs that exist in the nodes list.
9. Use unique node IDs and edge IDs.
10. Do not make guaranteed price predictions.
11. Return JSON only, without Markdown fences.
"""

    response = client.interactions.create(
        model=MODEL_NAME,
        input=prompt,
    )

    output = (response.output_text or "").strip()

    if not output:
        raise RuntimeError("Gemini returned an empty event graph")

    output = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        output,
        flags=re.IGNORECASE,
    )

    try:
        data = json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini returned invalid event graph JSON"
        ) from exc

    try:
        graph = EventGraph.model_validate(data)
    except ValidationError as exc:
        raise RuntimeError(
            "Generated event graph failed schema validation"
        ) from exc

    return graph
