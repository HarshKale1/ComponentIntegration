from datetime import date
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


class CorroborationStatus(str, Enum):
    UNVERIFIED = "unverified"
    PARTIALLY_CORROBORATED = "partially_corroborated"
    CORROBORATED = "corroborated"
    CONTRADICTED = "contradicted"


class CorroborationSource(APIModel):
    source_name: str = Field(min_length=1)
    url: str = Field(min_length=1)
    supports_claim: Optional[bool] = None
    explanation: str = ""
    content_available: bool = False


class CorroborationResult(APIModel):
    claim: str = Field(min_length=1)
    status: CorroborationStatus = CorroborationStatus.UNVERIFIED
    sources_checked: int = Field(ge=0)
    supporting_sources: int = Field(ge=0)
    contradicting_sources: int = Field(ge=0)
    sources: list[CorroborationSource] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class CorroborationRequest(APIModel):
    claim: str = Field(min_length=10, max_length=20000)
    query: str = Field(min_length=2, max_length=500)
    limit: int = Field(default=5, ge=1, le=10)
    exclude_url: str | None = None


class EventGraphRequest(APIModel):
    headline: str = Field(min_length=5, max_length=1000)
    url: str | None = None


class EventImpactRequest(APIModel):
    ticker: str = Field(min_length=1, max_length=20)
    event_date: date
    window_days: int = Field(default=7, ge=1, le=30)


class NewsImpactWorkflowRequest(APIModel):
    query: str = Field(
        default="finance OR stock market OR economy",
        min_length=2,
        max_length=500,
    )
    limit: int = Field(default=5, ge=1, le=10)
    ticker: str | None = Field(default=None, min_length=1, max_length=20)
    event_date: date | None = None
    window_days: int = Field(default=7, ge=1, le=30)

    @model_validator(mode="after")
    def validate_market_inputs(self):
        if (self.ticker is None) != (self.event_date is None):
            raise ValueError(
                "ticker and event_date must either both be provided "
                "or both be omitted"
            )

        return self


class NewsImpactWorkflowResponse(APIModel):
    success: bool
    article: dict
    content_length: int
    event_graph: EventGraph
    market_impact: dict | None = None
    limitations: list[str] = Field(default_factory=list)
