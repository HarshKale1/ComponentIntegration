
import json
from types import SimpleNamespace

import pytest

from services import claim_evaluation_service as evaluator


class FakeInteractions:
    def __init__(self, output):
        self.output = output

    def create(self, **kwargs):
        return SimpleNamespace(output_text=self.output)


class FakeClient:
    def __init__(self, output):
        self.interactions = FakeInteractions(output)


def set_gemini_response(monkeypatch, output):
    monkeypatch.setattr(
        evaluator,
        "client",
        FakeClient(output),
    )


def test_supporting_evidence(monkeypatch):
    set_gemini_response(
        monkeypatch,
        json.dumps({
            "verdict": "supports",
            "explanation": "The article reports a rate cut.",
            "evidence_quotes": ["The central bank cut interest rates."],
        }),
    )

    result = evaluator.evaluate_claim_against_article(
        claim="The central bank cut interest rates.",
        title="Central bank announces rate cut",
        content="The central bank cut interest rates.",
    )

    assert result.verdict == evaluator.ClaimVerdict.SUPPORTS
    assert result.evidence_quotes == [
        "The central bank cut interest rates."
    ]


def test_contradicting_evidence(monkeypatch):
    set_gemini_response(
        monkeypatch,
        json.dumps({
            "verdict": "contradicts",
            "explanation": "The article reports no rate change.",
            "evidence_quotes": ["The bank left rates unchanged."],
        }),
    )

    result = evaluator.evaluate_claim_against_article(
        claim="The central bank cut interest rates.",
        title="Central bank holds rates",
        content="The bank left rates unchanged.",
    )

    assert result.verdict == evaluator.ClaimVerdict.CONTRADICTS


def test_invalid_quote_forces_unclear(monkeypatch):
    set_gemini_response(
        monkeypatch,
        json.dumps({
            "verdict": "supports",
            "explanation": "The article supports the claim.",
            "evidence_quotes": ["This sentence is invented."],
        }),
    )

    result = evaluator.evaluate_claim_against_article(
        claim="The company reported higher profits.",
        title="Company reports earnings",
        content="The company reported quarterly earnings.",
    )

    assert result.verdict == evaluator.ClaimVerdict.UNCLEAR
    assert result.evidence_quotes == []


def test_empty_content_does_not_call_gemini(monkeypatch):
    def unexpected_call(**kwargs):
        pytest.fail("Gemini should not be called for empty content")

    monkeypatch.setattr(
        evaluator,
        "client",
        SimpleNamespace(
            interactions=SimpleNamespace(create=unexpected_call)
        ),
    )

    result = evaluator.evaluate_claim_against_article(
        claim="The company reported higher profits.",
        title="Company earnings",
        content="",
    )

    assert result.verdict == evaluator.ClaimVerdict.UNCLEAR
    assert result.evidence_quotes == []


def test_empty_claim_is_rejected():
    with pytest.raises(ValueError, match="Claim cannot be empty"):
        evaluator.evaluate_claim_against_article(
            claim="   ",
            title="Company earnings",
            content="The company reported higher profits.",
        )


def test_invalid_gemini_json_is_rejected(monkeypatch):
    set_gemini_response(monkeypatch, "not valid JSON")

    with pytest.raises(RuntimeError, match="invalid claim evaluation"):
        evaluator.evaluate_claim_against_article(
            claim="The company reported higher profits.",
            title="Company earnings",
            content="The company reported higher profits.",
        )
