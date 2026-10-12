import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import services.event_graph_service as graph_service


def valid_graph_data():
    return {
        "event_id": "event-1",
        "headline": "RBI changes repo rate",
        "event_type": "CENTRAL_BANK_RATE",
        "summary": "The RBI announced a repo rate decision.",
        "source": None,
        "nodes": [
            {
                "node_id": "rbi",
                "label": "Reserve Bank of India",
                "node_type": "COMPANY",
                "description": "Central bank of India",
            }
        ],
        "edges": [],
        "limitations": [],
    }


def mock_gemini_response(text):
    return SimpleNamespace(output_text=text)


def test_rejects_empty_headline():
    with pytest.raises(ValueError, match="Headline cannot be empty"):
        graph_service.generate_event_graph("   ")


def test_generates_valid_event_graph(monkeypatch):
    payload = valid_graph_data()
    fake_client = Mock()
    fake_client.interactions.create.return_value = mock_gemini_response(
        json.dumps(payload)
    )

    monkeypatch.setattr(graph_service, "client", fake_client)

    result = graph_service.generate_event_graph(
        headline="RBI changes repo rate",
        article_content="The RBI announced a policy decision.",
    )

    assert result.event_id == "event-1"
    assert result.headline == "RBI changes repo rate"
    assert result.event_type.value == "CENTRAL_BANK_RATE"
    assert len(result.nodes) == 1
    fake_client.interactions.create.assert_called_once()


def test_accepts_json_wrapped_in_markdown_fences(monkeypatch):
    payload = valid_graph_data()
    response_text = "```json\n" + json.dumps(payload) + "\n```"

    fake_client = Mock()
    fake_client.interactions.create.return_value = mock_gemini_response(
        response_text
    )
    monkeypatch.setattr(graph_service, "client", fake_client)

    result = graph_service.generate_event_graph("RBI changes repo rate")

    assert result.event_id == "event-1"


def test_rejects_empty_gemini_response(monkeypatch):
    fake_client = Mock()
    fake_client.interactions.create.return_value = mock_gemini_response("")
    monkeypatch.setattr(graph_service, "client", fake_client)

    with pytest.raises(RuntimeError, match="empty event graph"):
        graph_service.generate_event_graph("RBI changes repo rate")


def test_rejects_invalid_json(monkeypatch):
    fake_client = Mock()
    fake_client.interactions.create.return_value = mock_gemini_response(
        "{not valid json"
    )
    monkeypatch.setattr(graph_service, "client", fake_client)

    with pytest.raises(RuntimeError, match="invalid event graph JSON"):
        graph_service.generate_event_graph("RBI changes repo rate")


def test_rejects_schema_invalid_graph(monkeypatch):
    payload = valid_graph_data()
    payload["event_type"] = "NOT_A_VALID_EVENT_TYPE"

    fake_client = Mock()
    fake_client.interactions.create.return_value = mock_gemini_response(
        json.dumps(payload)
    )
    monkeypatch.setattr(graph_service, "client", fake_client)

    with pytest.raises(RuntimeError, match="failed schema validation"):
        graph_service.generate_event_graph("RBI changes repo rate")


def test_rejects_edge_referencing_missing_node(monkeypatch):
    payload = valid_graph_data()
    payload["nodes"].append(
        {
            "node_id": "oil",
            "label": "Crude oil",
            "node_type": "COMMODITY",
            "description": "Crude oil prices",
        }
    )
    payload["edges"] = [
        {
            "edge_id": "edge-1",
            "source_node_id": "rbi",
            "target_node_id": "missing-node",
            "relationship": "affects",
            "strength": 0.7,
            "direction": "NEGATIVE",
            "explanation": "Test relationship",
            "evidence_type": "HYPOTHESIS",
            "evidence": [],
            "limitations": ["Hypothetical relationship used for testing"],
        }
    ]

    fake_client = Mock()
    fake_client.interactions.create.return_value = mock_gemini_response(
        json.dumps(payload)
    )
    monkeypatch.setattr(graph_service, "client", fake_client)

    with pytest.raises(RuntimeError, match="failed schema validation"):
        graph_service.generate_event_graph("RBI changes repo rate")
    id="8e3v5x"
