# FinFlow AI — Scoring Methodology

## 1. Purpose

FinFlow AI represents possible relationships between financial events and affected commodities, indicators, countries, sectors, companies, and assets.

Each graph edge has a `strength` value between `0.0` and `1.0`.

## 2. Meaning of Strength

- `0.0`: Minimal represented relationship strength.
- `0.5`: Moderate illustrative relationship strength.
- `1.0`: Very strong represented relationship.

**Important:** Strength is not the probability that an event will happen, the probability of a market movement, or a guaranteed measure of financial impact.

## 3. Current MVP

The current MVP uses predefined scenario data and keyword matching. Its strength values are manually assigned demonstration values.

They are:
- Not statistically calibrated.
- Not calculated from live market data.
- Not validated against historical market outcomes.
- Not suitable for investment decisions.

## 4. Evidence Classification

Each edge uses an `evidence_type`:

- `VERIFIED_SOURCE`: Supported by a verified source recorded in the evidence list.
- `ESTABLISHED_RELATIONSHIP`: Represents a documented, established relationship.
- `HYPOTHESIS`: A plausible relationship that requires verification.
- `INSUFFICIENT_VERIFIED_EVIDENCE`: Insufficient verified evidence to support a specific relationship.

Hypotheses must include limitations. Edges marked `INSUFFICIENT_VERIFIED_EVIDENCE` must not contain evidence items.

## 5. Future Scoring Improvements

A future scoring model should evaluate:

1. Evidence quality and source reliability.
2. Relevance of the relationship to the event.
3. Recency of the information.
4. Independent source corroboration.
5. Conflicting evidence and uncertainty.
6. Historical validation against observed outcomes.

Any future scoring formula should be documented, tested, and validated before its scores are described as calibrated.

## 6. Responsible Interpretation

Graph edges describe possible transmission mechanisms, not guaranteed market outcomes. Direction can depend on the time horizon, economic conditions, policy responses, and other factors.

FinFlow AI's current output is a demonstration and should not be used as financial advice.