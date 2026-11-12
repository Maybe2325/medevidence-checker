"""Core Pydantic v2 Data Models and Domain Protocols for SpecGuard-Crew."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel as _PydanticBaseModel, Field


class BaseModel(_PydanticBaseModel):
    """Pydantic v1/v2 compatible BaseModel."""

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        if hasattr(super(), "model_dump"):
            return super().model_dump(*args, **kwargs)  # type: ignore[misc]
        return self.dict(*args, **kwargs)


EARSKeyword = Literal["WHEN", "IF", "WHILE", "WHERE"]
SeverityLevel = Literal["CRITICAL", "WARNING", "INFO", "SAFE"]
OverallStatus = Literal["VIOLATION_DETECTED", "WARNING_ONLY", "VERIFIED_SAFE"]


class EARSClause(BaseModel):
    """Formal requirement statement structured in EARS syntax."""

    clause_id: str = Field(..., description="Deterministic identifier for the EARS clause")
    keyword: EARSKeyword = Field(..., description="EARS trigger keyword (WHEN, IF, WHILE, WHERE)")
    condition: str = Field(..., min_length=1, description="Precondition or trigger state")
    system_actor: str = Field(..., min_length=1, description="Target system component name")
    obligation: str = Field(..., min_length=1, description="Normative requirement after SHALL")
    source_file: str = Field(default="inline", description="Source .kiro/specs file path")
    line_number: int = Field(default=1, ge=1, description="1-indexed line number in spec file")

    def to_ears_markdown(self) -> str:
        """Render canonical EARS requirement line."""
        conn = "THEN THE" if self.keyword == "IF" else "THE"
        return f"{self.keyword} {self.condition}, {conn} {self.system_actor} SHALL {self.obligation}."


class VerificationDAG(BaseModel):
    """Compiled directed acyclic graph of formal EARS invariant clauses."""

    spec_name: str
    source_path: str
    clauses: List[EARSClause] = Field(default_factory=list)
    digest: str = Field(..., description="SHA-256 deterministic content digest")


class AtomicClaim(BaseModel):
    """A single falsifiable claim extracted by Agent #1 (ClaimExtractor)."""

    claim_id: str
    category: str
    source_span: str
    statement: str
    mapped_clause_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CounterexampleWitness(BaseModel):
    """Evidence or minimal falsifying input discovered by Agent #2 (CounterexampleHunter)."""

    claim_id: str
    violated: bool
    severity: SeverityLevel
    witness_input: str
    observed_outcome: str
    mcp_tool_used: str
    evidence_citation: str
    remediation_hint: str = ""


class AgentTraceStep(BaseModel):
    """Immutable execution trace step linking runtime behavior to /.kiro artifacts."""

    step_index: int = Field(..., ge=1)
    agent_id: Literal["ClaimExtractor", "CounterexampleHunter", "EvidenceAuditor"]
    kiro_agent_config: str
    kiro_spec_ref: str
    kiro_steering_ref: str
    mcp_tools_invoked: List[str] = Field(default_factory=list)
    summary: str
    duration_ms: float = Field(..., ge=0.0)


class AuditReport(BaseModel):
    """Final multi-agent verification output produced by Agent #3 (EvidenceAuditor)."""

    artifact_id: str
    domain: Literal["code_audit", "clinical_audit"]
    overall_status: OverallStatus
    compiled_invariants_count: int = Field(..., ge=0)
    claims: List[AtomicClaim] = Field(default_factory=list)
    witnesses: List[CounterexampleWitness] = Field(default_factory=list)
    remediation: str
    patched_artifact: Optional[str] = None
    kiro_trace: List[AgentTraceStep] = Field(default_factory=list)
    safety_disclosure: Optional[Dict[str, Any]] = None
    llm_mode: Literal["live_api", "deterministic_rule_engine"] = "deterministic_rule_engine"


class ConfusionMatrixMetrics(BaseModel):
    """Quantitative evaluation metrics bounded strictly in [0.0, 1.0]."""

    tp: int = Field(..., ge=0)
    fp: int = Field(..., ge=0)
    tn: int = Field(..., ge=0)
    fn: int = Field(..., ge=0)
    total: int = Field(..., ge=0)
    precision: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    specificity: float = Field(..., ge=0.0, le=1.0)
    f1_score: float = Field(..., ge=0.0, le=1.0)
    false_negative_rate: float = Field(..., ge=0.0, le=1.0)
    accuracy: float = Field(..., ge=0.0, le=1.0)
