
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, model_validator


class EventType(str, Enum):
    COMMODITY_SUPPLY = "COMMODITY_SUPPLY"
    CENTRAL_BANK_RATE = "CENTRAL_BANK_RATE"
    INFLATION = "INFLATION"
    GEOPOLITICAL = "GEOPOLITICAL"
    OTHER = "OTHER"


class NodeType(str, Enum):
    COMMODITY = "COMMODITY"
    INDICATOR = "INDICATOR"
    COUNTRY = "COUNTRY"
    SECTOR = "SECTOR"
    COMPANY = "COMPANY"
    ASSET = "ASSET"


class ImpactDirection(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class EvidenceType(str, Enum):
    VERIFIED_SOURCE = "VERIFIED_SOURCE"
    ESTABLISHED_RELATIONSHIP = "ESTABLISHED_RELATIONSHIP"
    HYPOTHESIS = "HYPOTHESIS"
    INSUFFICIENT_VERIFIED_EVIDENCE = "INSUFFICIENT_VERIFIED_EVIDENCE"


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvidenceItem(APIModel):
    evidence_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    url: Optional[str] = None
    published_at: Optional[str] = None
    claim: str = Field(min_length=1)


class GraphNode(APIModel):
    node_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    node_type: NodeType
    description: str = ""


class GraphEdge(APIModel):
    edge_id: str = Field(min_length=1)
    source_node_id: str = Field(min_length=1)
    target_node_id: str = Field(min_length=1)
    relationship: str = Field(min_length=1)
    strength: float = Field(ge=0.0, le=1.0)
    direction: ImpactDirection
    explanation: str = Field(min_length=1)
    evidence_type: EvidenceType
    evidence: list[EvidenceItem] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_evidence(self):
        if (
            self.evidence_type == EvidenceType.INSUFFICIENT_VERIFIED_EVIDENCE
            and self.evidence
        ):
            raise ValueError(
                "Evidence must be empty when evidence_type is "
                "INSUFFICIENT_VERIFIED_EVIDENCE"
            )

        if (
            self.evidence_type == EvidenceType.HYPOTHESIS
            and not self.limitations
        ):
            raise ValueError(
                "Hypothesis edges must include their limitations"
            )

        return self


class EventGraph(APIModel):
    event_id: str = Field(min_length=1)
    headline: str = Field(min_length=1)
    event_type: EventType
    summary: str = Field(min_length=1)
    source: Optional[str] = None
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_graph(self):
        node_ids = [node.node_id for node in self.nodes]

        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Node IDs must be unique within an event")

        edge_ids = [edge.edge_id for edge in self.edges]

        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError("Edge IDs must be unique within an event")

        valid_ids = set(node_ids)

        for edge in self.edges:
            if edge.source_node_id not in valid_ids:
                raise ValueError(
                    f"Unknown source node: {edge.source_node_id}"
                )

            if edge.target_node_id not in valid_ids:
                raise ValueError(
                    f"Unknown target node: {edge.target_node_id}"
                )

        return self


class NewsRequest(APIModel):
    text: str = Field(min_length=20, max_length=20000)


class AnalysisResponse(APIModel):
    matched: bool
    event: Optional[EventGraph] = None
    message: str
