"""Domain-Agnostic 3-Agent Kiro Crew Orchestrator (`ClaimExtractor` -> `CounterexampleHunter` -> `EvidenceAuditor`)."""

from __future__ import annotations

import pathlib
import time
from typing import Any, Dict, List, Literal, Optional, Protocol, Tuple

from .compiler import EARSCompiler
from .llm_adapter import LLMAdapter
from .models import (
    AgentTraceStep,
    AtomicClaim,
    AuditReport,
    CounterexampleWitness,
    OverallStatus,
    VerificationDAG,
)


class DomainAdapter(Protocol):
    """Protocol implemented by derived applications (`RepoNecromancer` and `MedEvidence-Checker`)."""

    @property
    def domain_id(self) -> Literal["code_audit", "clinical_audit"]:
        ...

    @property
    def spec_path(self) -> pathlib.Path:
        ...

    @property
    def mcp_tool_names(self) -> List[str]:
        ...

    def extract_claims(self, artifact_text: str, dag: VerificationDAG) -> List[AtomicClaim]:
        ...

    def hunt_counterexamples(
        self, artifact_text: str, claims: List[AtomicClaim], dag: VerificationDAG
    ) -> List[CounterexampleWitness]:
        ...

    def synthesize_remediation(
        self,
        artifact_text: str,
        claims: List[AtomicClaim],
        witnesses: List[CounterexampleWitness],
        overall_status: OverallStatus,
    ) -> Tuple[str, Optional[str], Optional[Dict[str, Any]]]:
        ...


class CrewOrchestrator:
    """Executes the 3-agent Kiro Crew pipeline over any DomainAdapter."""

    def __init__(
        self,
        compiler: Optional[EARSCompiler] = None,
        llm_adapter: Optional[LLMAdapter] = None,
    ) -> None:
        self.compiler = compiler or EARSCompiler()
        self.llm_adapter = llm_adapter or LLMAdapter()

    @staticmethod
    def aggregate_status(witnesses: List[CounterexampleWitness]) -> OverallStatus:
        """
        Formal Correctness Property 2: Monotonic Severity Escalation.
        - If any witness has violated=True and severity=='CRITICAL' -> 'VIOLATION_DETECTED'
        - Else if any witness has violated=True -> 'WARNING_ONLY'
        - Else -> 'VERIFIED_SAFE'
        """
        violated_witnesses = [w for w in witnesses if w.violated]
        if not violated_witnesses:
            return "VERIFIED_SAFE"
        if any(w.severity == "CRITICAL" for w in violated_witnesses):
            return "VIOLATION_DETECTED"
        return "WARNING_ONLY"

    def run_verification(
        self,
        artifact_id: str,
        artifact_text: str,
        adapter: DomainAdapter,
    ) -> AuditReport:
        """Execute Agent #1 -> Agent #2 -> Agent #3 sequentially and record Kiro trace steps."""
        dag = self.compiler.compile_file(adapter.spec_path)
        trace: List[AgentTraceStep] = []

        # Stage 1: ClaimExtractor (Agent #1)
        t0 = time.perf_counter()
        claims = adapter.extract_claims(artifact_text, dag)
        t1 = time.perf_counter()
        trace.append(
            AgentTraceStep(
                step_index=1,
                agent_id="ClaimExtractor",
                kiro_agent_config=".kiro/agents/claim-extractor.yaml",
                kiro_spec_ref=str(adapter.spec_path),
                kiro_steering_ref=".kiro/steering/product.md",
                mcp_tools_invoked=["list_compiled_ears_invariants"],
                summary=(
                    f"Compiled {len(dag.clauses)} EARS clauses (digest={dag.digest[:8]}) "
                    f"and extracted {len(claims)} atomic domain claims."
                ),
                duration_ms=round(max(0.01, (t1 - t0) * 1000.0), 3),
            )
        )

        # Stage 2: CounterexampleHunter (Agent #2)
        t2 = time.perf_counter()
        witnesses = adapter.hunt_counterexamples(artifact_text, claims, dag)
        t3 = time.perf_counter()
        violations_count = sum(1 for w in witnesses if w.violated)
        trace.append(
            AgentTraceStep(
                step_index=2,
                agent_id="CounterexampleHunter",
                kiro_agent_config=".kiro/agents/counterexample-hunter.yaml",
                kiro_spec_ref=str(adapter.spec_path),
                kiro_steering_ref=".kiro/steering/tech.md",
                mcp_tools_invoked=list(adapter.mcp_tool_names),
                summary=(
                    f"Executed MCP verification tools ({', '.join(adapter.mcp_tool_names)}) "
                    f"across {len(claims)} claims; found {violations_count} violation(s)."
                ),
                duration_ms=round(max(0.01, (t3 - t2) * 1000.0), 3),
            )
        )

        # Stage 3: EvidenceAuditor (Agent #3)
        t4 = time.perf_counter()
        overall_status = self.aggregate_status(witnesses)
        remediation, patched_artifact, safety_disclosure = adapter.synthesize_remediation(
            artifact_text=artifact_text,
            claims=claims,
            witnesses=witnesses,
            overall_status=overall_status,
        )
        t5 = time.perf_counter()
        trace.append(
            AgentTraceStep(
                step_index=3,
                agent_id="EvidenceAuditor",
                kiro_agent_config=".kiro/agents/evidence-auditor.yaml",
                kiro_spec_ref=".kiro/specs/skeleton-core/design.md",
                kiro_steering_ref=".kiro/steering/structure.md",
                mcp_tools_invoked=[],
                summary=(
                    f"Adjudicated final status={overall_status} under Property 2 "
                    f"(Monotonic Severity Escalation) and synthesized remediation."
                ),
                duration_ms=round(max(0.01, (t5 - t4) * 1000.0), 3),
            )
        )

        return AuditReport(
            artifact_id=artifact_id,
            domain=adapter.domain_id,
            overall_status=overall_status,
            compiled_invariants_count=len(dag.clauses),
            claims=claims,
            witnesses=witnesses,
            remediation=remediation,
            patched_artifact=patched_artifact,
            kiro_trace=trace,
            safety_disclosure=safety_disclosure,
            llm_mode=self.llm_adapter.mode,
        )
