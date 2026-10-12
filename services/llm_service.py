
import json
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ValidationError, field_validator


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=90000),
)

MODEL_NAME = "gemini-3.1-flash-lite"


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

    claims: list[str] = Field(
        default_factory=list,
        description="Specific claims extracted from the article",
    )

    supporting_evidence: list[str] = Field(
        default_factory=list,
        description="Short exact quotes from the article",
    )

    evidence_status: str = Field(default="unverified")

    evidence_match_status: str = Field(default="not_checked")

    @field_validator("impact_direction")
    @classmethod
    def validate_impact_direction(cls, value: str) -> str:
        allowed = {"positive", "negative", "mixed", "uncertain"}
        normalized = value.strip().lower()

        if normalized not in allowed:
            raise ValueError(
                f"impact_direction must be one of {sorted(allowed)}"
            )

        return normalized

    @field_validator("claims", "supporting_evidence")
    @classmethod
    def limit_list_items(cls, value: list[str]) -> list[str]:
        # Prevent unexpectedly large model responses.
        return [item.strip() for item in value if item.strip()][:5]


def validate_supporting_evidence(
    evidence: list[str],
    title: str,
    content: str,
) -> list[str]:
    """
    Keep only evidence excerpts found in the supplied article.

    Matching is case-insensitive but otherwise requires the complete
    excerpt to appear in the title or article text.
    """
    source_text = f"{title}\n{content}".casefold()
    matched = []
    seen = set()

    for item in evidence:
        quote = item.strip()

        if not quote:
            continue

        normalized_quote = quote.casefold()

        if normalized_quote in source_text and normalized_quote not in seen:
            matched.append(quote)
            seen.add(normalized_quote)

        if len(matched) == 3:
            break

    return matched


def determine_evidence_match_status(
    original_evidence: list[str],
    matched_evidence: list[str],
) -> str:
    """Describe whether returned evidence excerpts match the article."""
    original = [item.strip() for item in original_evidence if item.strip()]

    if not original:
        return "no_evidence"

    if len(matched_evidence) == len(original):
        return "matched"

    if matched_evidence:
        return "partial_match"

    return "no_match"


def analyze_news(title: str, content: str = "") -> NewsAnalysis:
    """Analyze financial news using Gemini with evidence safeguards."""

    title = (title or "").strip()
    content = (content or "").strip()[:6000]

    if not title:
        raise ValueError("Article title cannot be empty")

    # Do not call Gemini if article content is unavailable.
    if not content:
        return NewsAnalysis(
            event=title,
            affected_sectors=[],
            impact_direction="uncertain",
            reasoning=(
                "Article content is unavailable. A reliable financial "
                "impact assessment is not possible."
            ),
            uncertainties=[
                "Article text could not be retrieved.",
                "Claims cannot be extracted without sufficient content.",
            ],
            claims=[],
            supporting_evidence=[],
            evidence_status="unverified",
            evidence_match_status="not_checked",
        )

    prompt = f"""
Analyze the financial news article below.

TITLE:
{title}

ARTICLE:
{content}

Return a structured analysis with these fields:
- event: concise description of the main event
- affected_sectors: list of potentially affected sectors
- impact_direction: positive, negative, mixed, or uncertain
- reasoning: concise explanation of possible financial implications
- uncertainties: important unknowns or limitations
- claims: up to 5 specific claims explicitly supported by the article
- supporting_evidence: up to 3 short, exact excerpts copied from the article
- evidence_status: "unverified"
- evidence_match_status: "not_checked"

Rules:
- Do not invent facts, claims, figures, sources, or quotations.
- Distinguish reported facts from predictions and opinions.
- Do not treat a reported plan as a confirmed event.
- Do not claim that an article proves a financial outcome.
- Use "uncertain" if the direction of financial impact is unclear.
- Return data matching the required schema.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=NewsAnalysis,
            ),
        )

    except Exception as exc:
        error_name = type(exc).__name__
        error_message = str(exc).lower()

        if (
            "429" in error_message
            or "quota" in error_message
            or "resource_exhausted" in error_message
            or "ratelimit" in error_name.lower()
        ):
            raise RuntimeError(
                "Gemini quota/rate limit reached. Check the project's "
                "quota before making another request."
            ) from exc

        if (
            "timeout" in error_name.lower()
            or "timed out" in error_message
        ):
            raise RuntimeError(
                "Gemini request timed out. No automatic retry was attempted."
            ) from exc

        raise RuntimeError(
            f"Gemini analysis failed ({error_name}): {exc}"
        ) from exc

    output = (response.text or "").strip()

    if not output:
        raise RuntimeError("Gemini returned an empty response")

    # Tolerate an unexpected Markdown code fence.
    output = re.sub(
        r"^```(?:json)?\s*",
        "",
        output,
        flags=re.IGNORECASE,
    )
    output = re.sub(r"\s*```$", "", output)

    try:
        analysis = NewsAnalysis.model_validate_json(output)

    except (ValidationError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            "Gemini returned invalid analysis JSON. "
            "The response was not accepted."
        ) from exc

    # Check the original evidence before filtering it.
    original_evidence = analysis.supporting_evidence.copy()

    matched_evidence = validate_supporting_evidence(
        evidence=original_evidence,
        title=title,
        content=content,
    )

    analysis.supporting_evidence = matched_evidence

    analysis.evidence_match_status = determine_evidence_match_status(
        original_evidence=original_evidence,
        matched_evidence=matched_evidence,
    )

    # Matching text is not independent verification of factual claims.
    analysis.evidence_status = "unverified"

    return analysis
