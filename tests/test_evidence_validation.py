
from services.llm_service import validate_supporting_evidence
from services.llm_service import determine_evidence_match_status

def test_keeps_evidence_found_in_article():
    evidence = [
        "RBI raised the repo rate by 0.25%",
        "The stock market crashed by 50%",
    ]

    result = validate_supporting_evidence(
        evidence=evidence,
        title="RBI raises the repo rate",
        content="RBI raised the repo rate by 0.25% today.",
    )

    assert result == ["RBI raised the repo rate by 0.25%"]


def test_evidence_matching_ignores_capitalization():
    result = validate_supporting_evidence(
        evidence=["RBI raised the repo rate"],
        title="",
        content="rbi raised the repo rate today.",
    )

    assert result == ["RBI raised the repo rate"]


def test_rejects_evidence_not_found_in_article():
    result = validate_supporting_evidence(
        evidence=["Company profits doubled"],
        title="Company announces quarterly results",
        content="Revenue increased slightly.",
    )

    assert result == []


def test_rejects_empty_evidence():
    result = validate_supporting_evidence(
        evidence=[],
        title="RBI announcement",
        content="The RBI announced a policy update.",
    )

    assert result == []

from services.llm_service import NewsAnalysis


def test_evidence_status_defaults_to_unverified():
    analysis = NewsAnalysis(
        event="RBI changes repo rate",
        affected_sectors=["Banking"],
        impact_direction="uncertain",
        reasoning="The article reports a policy change.",
        uncertainties=["The market reaction is unknown."],
        supporting_evidence=["RBI changed the repo rate."],
    )

    assert analysis.evidence_status == "unverified"
    assert analysis.evidence_match_status == "not_checked"


def test_evidence_status_can_be_set_explicitly():
    analysis = NewsAnalysis(
        event="RBI changes repo rate",
        affected_sectors=["Banking"],
        impact_direction="uncertain",
        reasoning="The article reports a policy change.",
        uncertainties=[],
        supporting_evidence=["RBI changed the repo rate."],
        evidence_status="unverified",
        evidence_match_status="text_matched",
    )

    assert analysis.evidence_status == "unverified"
    assert analysis.evidence_match_status == "text_matched"

# Test 6: Evidence matching status
assert determine_evidence_match_status(
    ["quote A", "quote B"], ["quote A", "quote B"]
) == "matched"

assert determine_evidence_match_status(
    ["quote A", "quote B"], ["quote A"]
) == "partial_match"

assert determine_evidence_match_status(
    ["quote A"], []
) == "no_match"

assert determine_evidence_match_status([], []) == "no_evidence"

print("PASS 6: All evidence status cases")