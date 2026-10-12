
from services.llm_service import (
    NewsAnalysis,
    validate_supporting_evidence,
    analyze_news,
)

title = "Apple announces a new MacBook"
content = (
    "Apple reportedly plans a touchscreen MacBook. "
    "The launch date has not been confirmed."
)

# Test 1: Exact evidence should be retained.
evidence = [
    "Apple reportedly plans a touchscreen MacBook.",
    "The launch date has not been confirmed.",
]
result = validate_supporting_evidence(evidence, title, content)
assert len(result) == 2
print("PASS 1: Valid evidence retained")

# Test 2: Invented evidence should be rejected.
evidence = [
    "Apple reportedly plans a touchscreen MacBook.",
    "Apple confirmed sales will double.",
]
result = validate_supporting_evidence(evidence, title, content)
assert len(result) == 1
assert result[0] == "Apple reportedly plans a touchscreen MacBook."
print("PASS 2: Unsupported evidence rejected")

# Test 3: Matching should ignore capitalization.
result = validate_supporting_evidence(
    ["APPLE REPORTEDLY PLANS A TOUCHSCREEN MACBOOK."],
    title,
    content,
)
assert len(result) == 1
print("PASS 3: Case-insensitive matching works")

# Test 4: Empty evidence should return an empty list.
result = validate_supporting_evidence([], title, content)
assert result == []
print("PASS 4: Empty evidence handled")

# Test 5: Missing article content must not require a Gemini request.
analysis = analyze_news(title="Test financial headline", content="")
assert isinstance(analysis, NewsAnalysis)
assert analysis.claims == []
assert analysis.supporting_evidence == []
assert analysis.evidence_match_status == "not_checked"
assert analysis.evidence_status == "unverified"
print("PASS 5: Missing content handled without Gemini")

print("\nAll five local tests passed. No Gemini API request was made.")
