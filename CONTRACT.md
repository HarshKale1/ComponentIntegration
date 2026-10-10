# FinFlow AI — API Contract

**Status:** Draft — confirm with Member 2 before implementation  
**Backend:** FastAPI  
**Base URL:** `http://localhost:8000`

## 1. Common conventions

- All API request and response bodies use JSON.
- IDs are strings, stable within the dataset, and unique within their entity type.
- Field names use `snake_case`.
- Arrays must be returned as `[]` when empty, never `null`.
- Relationship strength is a numeric value from `0.0` to `1.0`. It is not a probability.
- Missing verified evidence must be stated explicitly; evidence must never be fabricated.

## 2. Enums

### Event types
- `COMMODITY_SUPPLY`
- `CENTRAL_BANK_RATE`
- `INFLATION`
- `GEOPOLITICAL`
- `OTHER`

### Node types
- `COMMODITY`
- `INDICATOR`
- `COUNTRY`
- `SECTOR`
- `COMPANY`
- `ASSET`

### Impact direction
- `POSITIVE`
- `NEGATIVE`
- `MIXED`
- `UNKNOWN`

Direction describes the expected effect on the target node, not whether the event itself is good or bad.

### Evidence types
- `VERIFIED_SOURCE`
- `ESTABLISHED_RELATIONSHIP`
- `HYPOTHESIS`
- `INSUFFICIENT_VERIFIED_EVIDENCE`

## 3. Event response

An event contains:

- `event_id`: string
- `headline`: string
- `event_type`: Event type
- `summary`: string
- `source`: string or null
- `nodes`: array of nodes
- `edges`: array of edges
- `limitations`: array of strings

## 4. Node

Each node contains:

- `node_id`: string
- `label`: string
- `node_type`: Node type
- `description`: string

## 5. Edge

Each edge contains:

- `edge_id`: string
- `source_node_id`: string
- `target_node_id`: string
- `relationship`: string
- `strength`: float from 0.0 to 1.0
- `direction`: Impact direction
- `explanation`: string
- `evidence_type`: Evidence type
- `evidence`: array of evidence items
- `limitations`: array of strings

Every node referenced by an edge must exist in the same graph.

## 6. Evidence item

Each evidence item contains:

- `evidence_id`: string
- `source_name`: string
- `url`: string or null
- `published_at`: ISO 8601 date/time string or null
- `claim`: string describing what the source supports

An empty evidence array does not mean evidence exists. Use `INSUFFICIENT_VERIFIED_EVIDENCE` when no adequate support is available.

## 7. Initial endpoints

### `GET /health`
Returns server status.

### `GET /events`
Returns a list of predefined illustrative financial event scenarios. These are demo scenarios, not verified live-news events.

### `POST /news/analyze`
Accepts news text and returns the matching event graph.

Request:

    {
      "text": "Crude oil prices rise amid supply concerns."
    }

Successful response:

    {
      "matched": true,
      "event": {
        "event_id": "event_oil_supply",
        "headline": "Example oil supply scenario",
        "event_type": "COMMODITY_SUPPLY",
        "summary": "Illustrative scenario for oil supply disruption.",
        "source": null,
        "nodes": [],
        "edges": [],
        "limitations": [
          "Illustrative scenario; not a verified live-news analysis."
        ]
      },
      "message": "Matched a predefined illustrative scenario using keywords. This is not verified live-news analysis."
    }

The example above demonstrates the response shape only. It is not a claim about a real event.

For unmatched text, return `matched: false` and an explicit explanation rather than inventing a graph.

## 8. Compatibility rules

- Do not rename fields or change enum values without discussing the change with both team members.
- Validate all responses against the agreed Pydantic models.
- Any future LLM extraction must produce the same contract.
- The backend owns the contract; the frontend consumes it.
