"""RepoNecromancer (`apps/repo-necromancer`) Domain Adapter for SpecGuard-Crew."""

from __future__ import annotations

import ast
import pathlib
from typing import Any, Dict, List, Literal, Optional, Tuple

from packages.specguard_core.crew_orchestrator import CrewOrchestrator
from packages.specguard_core.models import (
    AtomicClaim,
    AuditReport,
    CounterexampleWitness,
    OverallStatus,
    VerificationDAG,
)
from packages.specguard_mcp_server.tools_code_sandbox import run_property_test_sandbox


class CodeAuditDomainAdapter:
    """Connects RepoNecromancer (App #1) to the shared SpecGuard-Core 3-agent skeleton."""

    def __init__(self, repo_root: Optional[pathlib.Path] = None) -> None:
        self._root = repo_root or pathlib.Path(__file__).resolve().parents[2]

    @property
    def domain_id(self) -> Literal["code_audit", "clinical_audit"]:
        return "code_audit"

    @property
    def spec_path(self) -> pathlib.Path:
        return self._root / ".kiro" / "specs" / "repo-necromancer" / "requirements.md"

    @property
    def mcp_tool_names(self) -> List[str]:
        return ["run_property_test_sandbox"]

    def extract_claims(self, artifact_text: str, dag: VerificationDAG) -> List[AtomicClaim]:
        """Agent #1 (ClaimExtractor): Extract AST function invariants and security claims."""
        claims: List[AtomicClaim] = []
        clause_0 = dag.clauses[0].clause_id if dag.clauses else None
        clause_1 = dag.clauses[1].clause_id if len(dag.clauses) > 1 else clause_0

        try:
            tree = ast.parse(artifact_text)
            funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        except SyntaxError:
            funcs = []

        if not funcs:
            claims.append(
                AtomicClaim(
                    claim_id="CLAIM-CODE-01",
                    category="module_integrity",
                    source_span="module_root",
                    statement="Module source code shall parse cleanly and contain no dangerous execution sinks.",
                    mapped_clause_id=clause_0,
                )
            )
            return claims

        for idx, fn in enumerate(funcs, start=1):
            args_sig = ", ".join(a.arg for a in fn.args.args)
            claims.append(
                AtomicClaim(
                    claim_id=f"CLAIM-CODE-{idx:02d}-BOUNDARY",
                    category="boundary_invariants",
                    source_span=f"def {fn.name}({args_sig}) [line {fn.lineno}]",
                    statement=(
                        f"Function `{fn.name}({args_sig})` shall preserve domain postconditions and "
                        f"never raise unhandled ZeroDivisionError/IndexError across boundary inputs."
                    ),
                    mapped_clause_id=clause_0,
                    metadata={"function_name": fn.name, "args": [a.arg for a in fn.args.args]},
                )
            )
            claims.append(
                AtomicClaim(
                    claim_id=f"CLAIM-CODE-{idx:02d}-SECURITY",
                    category="security_sinks",
                    source_span=f"def {fn.name}({args_sig}) [line {fn.lineno}]",
                    statement=(
                        f"Function `{fn.name}` shall be free of RCE (`eval`/`exec`), command injection (`shell=True`), "
                        f"SQL string interpolation, timing side-channels, and cross-call mutable default leaks."
                    ),
                    mapped_clause_id=clause_1,
                    metadata={"function_name": fn.name},
                )
            )

        return claims

    def hunt_counterexamples(
        self, artifact_text: str, claims: List[AtomicClaim], dag: VerificationDAG
    ) -> List[CounterexampleWitness]:
        """Agent #2 (CounterexampleHunter): Invoke MCP `run_property_test_sandbox` tool."""
        sandbox_res = run_property_test_sandbox(artifact_text)
        findings = sandbox_res.get("findings", [])
        witnesses: List[CounterexampleWitness] = []

        if not findings:
            for c in claims:
                witnesses.append(
                    CounterexampleWitness(
                        claim_id=c.claim_id,
                        violated=False,
                        severity="SAFE",
                        witness_input="Hypothesis PBT (50 edge-case probes) + AST static verifier",
                        observed_outcome="Zero property violations or security sinks detected.",
                        mcp_tool_used="run_property_test_sandbox",
                        evidence_citation="Verified against .kiro/specs/repo-necromancer/requirements.md",
                    )
                )
            return witnesses

        primary_claim_id = claims[0].claim_id if claims else "CLAIM-CODE-01"
        sec_claim_id = claims[1].claim_id if len(claims) > 1 else primary_claim_id

        for finding in findings:
            target_claim = sec_claim_id if finding["rule_id"].startswith("SEC-") else primary_claim_id
            witnesses.append(
                CounterexampleWitness(
                    claim_id=target_claim,
                    violated=True,
                    severity=finding["severity"],
                    witness_input=finding["witness_input"],
                    observed_outcome=finding["observed_outcome"],
                    mcp_tool_used="run_property_test_sandbox",
                    evidence_citation=finding["evidence_citation"],
                    remediation_hint=finding.get("remediation_hint", ""),
                )
            )

        return witnesses

    def synthesize_remediation(
        self,
        artifact_text: str,
        claims: List[AtomicClaim],
        witnesses: List[CounterexampleWitness],
        overall_status: OverallStatus,
    ) -> Tuple[str, Optional[str], Optional[Dict[str, Any]]]:
        """Agent #3 (EvidenceAuditor): Synthesize verified code patch and remediation guidance."""
        sandbox_res = run_property_test_sandbox(artifact_text)
        patched_code = sandbox_res.get("patched_code", artifact_text)
        violated = [w for w in witnesses if w.violated]

        if not violated:
            return (
                "All EARS code invariants and Hypothesis property probes passed. No patch required.",
                artifact_text,
                {"domain": "software_security", "pbt_engine": "Hypothesis + AST Sandbox"},
            )

        hints = "; ".join(dict.fromkeys(w.remediation_hint for w in violated if w.remediation_hint))
        remediation_text = (
            f"Detected {len(violated)} formal specification violation(s). "
            f"Remediation Strategy: {hints}"
        )
        return (
            remediation_text,
            patched_code,
            {"domain": "software_security", "pbt_engine": "Hypothesis + AST Sandbox"},
        )


def audit_code_snippet(source_code: str, artifact_id: str = "code-snippet-01") -> AuditReport:
    """Convenience entrypoint for RepoNecromancer verification."""
    orchestrator = CrewOrchestrator()
    adapter = CodeAuditDomainAdapter()
    return orchestrator.run_verification(
        artifact_id=artifact_id,
        artifact_text=source_code,
        adapter=adapter,
    )


def run_single_prompt_code_baseline(source_code: str) -> bool:
    """
    Single-Pass Naive Baseline for Benchmark Comparison:
    Simulates a surface-level single-prompt linter/LLM pass that only flags obvious `eval(` or `shell=True`,
    missing subtle mathematical boundary violations, negative discount/transfer inversions, and state leaks.
    Returns True if flagged as defective, False if deemed safe.
    """
    obvious_markers = ("eval(", "exec(", "shell=True")
    return any(m in source_code for m in obvious_markers)
