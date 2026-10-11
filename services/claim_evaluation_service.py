
import json
import re
from enum import Enum

from pydantic import BaseModel, Field

from services.llm_service import client, MODEL_NAME


class ClaimVerdict(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    UNCLEAR = "unclear"


class ClaimEvaluation(BaseModel):
    verdict: ClaimVerdict
    explanation: str = Field(min_length=1)
    evidence_quotes: list[str] = Field(default_factory=list)


def evaluate_claim_against_article(
    claim: str,
    title: str,
    content: str,
) -> ClaimEvaluation:
    if not claim.strip():
        raise ValueError("Claim cannot be empty")

    if not content.strip():
        return ClaimEvaluation(
            verdict=ClaimVerdict.UNCLEAR,
            explanation="Article content is unavailable; the claim cannot be evaluated.",
            evidence_quotes=[],
        )

    prompt = f"""
Evaluate whether this article supports or contradicts the specific claim.

CLAIM:
{claim}

ARTICLE TITLE:
{title}

ARTICLE CONTENT:
{content[:12000]}

Return valid JSON with exactly these fields:
- verdict: "supports", "contradicts", or "unclear"
- explanation: concise explanation grounded in the article
- evidence_quotes: list of exact short quotations from the supplied title/content

Rules:
1. Evaluate the claim itself, not merely whether the article discusses a related topic.
2. Use "supports" only when the article provides evidence consistent with the claim.
3. Use "contradicts" only when the article provides evidence against the claim.
4. Use "unclear" when evidence is missing, ambiguous, irrelevant, or insufficient.
5. Never invent facts or quotations.
6. Every evidence quote must appear verbatim in the supplied title/content.
7. Do not treat an article's own unsupported assertion as independently verified truth.
8. Do not infer that the claim is globally true or false from this article alone.
9. Return JSON only, without Markdown fences.
"""

    response = client.interactions.create(
        model=MODEL_NAME,
        input=prompt,
    )

    output = (response.output_text or "").strip()
    if not output:
        raise RuntimeError("Gemini returned an empty evaluation")

    output = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        output,
        flags=re.IGNORECASE,
    )

    try:
        data = json.loads(output)
        evaluation = ClaimEvaluation.model_validate(data)
    except (json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(
            "Gemini returned an invalid claim evaluation"
        ) from exc

    # Accept only evidence quotes found exactly in the supplied article.
    source_text = f"{title}\n{content}"
    evaluation.evidence_quotes = [
        quote
        for quote in evaluation.evidence_quotes
        if quote.strip() and quote in source_text
    ]

    # Without a matching quotation, the model's verdict is not sufficiently
    # grounded for this first version of the evaluator.
    if not evaluation.evidence_quotes:
        evaluation.verdict = ClaimVerdict.UNCLEAR
        evaluation.explanation = (
            "No verifiable quotation from the supplied article was returned. "
            "The claim remains unresolved."
        )

    return evaluation
