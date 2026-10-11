import re
import os
import json

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.8-flash"


class NewsAnalysis(BaseModel):
    event: str = Field(description="The main financial event")
    affected_sectors: list[str] = Field(
        description="Sectors potentially affected by the event"
    )
    impact_direction: str = Field(
        description="positive, negative, mixed, or uncertain"
    )
    reasoning: str = Field(
        description="Reasoning behind the potential financial impact"
    )
    uncertainties: list[str] = Field(
        description="Important unknowns or limitations"
    )
    supporting_evidence: list[str] = Field(
        description=(
            "Exact facts or short quotes from the article "
            "that support the analysis. Return an empty list "
            "when the article provides no supporting evidence."
        )
    )
    
    evidence_status: str = Field(
        default="unverified",
        description=(
            "Verification status. Use unverified until "
            "independent sources or authoritative data "
            "confirm the claim."
        )
    )
    
    evidence_match_status: str = Field(
        default="not_checked",
        description=(
            "Whether supporting evidence has been checked "
            "for exact text matches against the article."
        )
    )



def validate_supporting_evidence(
    evidence: list[str],
    title: str,
    content: str,
) -> list[str]:
    """Keep only evidence found in the supplied article text."""
    source_text = f"{title}\n{content}".casefold()

    return [
        item
        for item in evidence
        if item.strip() and item.casefold() in source_text
    ]


def analyze_news(title: str, content: str = "") -> NewsAnalysis:
    prompt = f"""
Analyze this financial news.

Title: {title}
Content: {content}

Return a JSON object with these fields:
- event: string
- affected_sectors: list of strings
- impact_direction: positive, negative, mixed, or uncertain
- reasoning: string
- uncertainties: list of strings
- supporting_evidence: list of strings

Rules:
1. Distinguish reported facts from your own inferences.
2. supporting_evidence must contain only facts or short quotes
   that actually appear in the supplied title or content.
3. Never invent quotes, figures, sources, or events.
4. If the article content is empty or insufficient, use an
   empty supporting_evidence list and explain the limitation
   in uncertainties.
5. Do not present potential financial impacts as guaranteed
   predictions.
6. Use "uncertain" when the evidence does not establish a
   clear impact direction.
7. Do not use Markdown code fences. Return valid JSON only.
"""

    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=prompt,
    )

    if not interaction.output_text:
        raise RuntimeError("Gemini returned an empty response")

    # Remove optional Markdown JSON code fences.
    output = interaction.output_text.strip()
    output = re.sub(r"^```(?:json)?\s*", "", output, flags=re.IGNORECASE)
    output = re.sub(r"\s*```$", "", output)

    try:
        data = json.loads(output)
        analysis = NewsAnalysis.model_validate(data)
        analysis.supporting_evidence = validate_supporting_evidence(
            evidence=analysis.supporting_evidence,
            title=title,
            content=content,
        )
        analysis.evidence_match_status = (
            "matched" if analysis.supporting_evidence else "no_match"
        )

        analysis.evidence_status = "unverified"

        return analysis
    except (json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(
            f"Gemini returned invalid analysis JSON: {output}"
        ) from exc
