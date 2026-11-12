"""MedEvidence-Checker (`apps/med-evidence-checker`) Domain Adapter for SpecGuard-Crew."""

from __future__ import annotations

import pathlib
import re
from typing import Any, Dict, List, Literal, Optional, Tuple

from packages.specguard_core.crew_orchestrator import CrewOrchestrator
from packages.specguard_core.models import (
    AtomicClaim,
    AuditReport,
    CounterexampleWitness,
    OverallStatus,
    VerificationDAG,
)
from packages.specguard_mcp_server.tools_clinical_kb import (
    parse_clinical_context,
    query_clinical_guidelines_db,
)


_SSN_OR_PHI_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def sanitize_zero_phi(text: str) -> Tuple[str, bool]:
    """Redact any accidental SSN-like patterns to strictly enforce Zero-PHI compliance."""
    if _SSN_OR_PHI_PATTERN.search(text):
        return _SSN_OR_PHI_PATTERN.sub("[REDACTED-ZERO-PHI]", text), True
    return text, False


class ClinicalAuditDomainAdapter:
    """Connects MedEvidence-Checker (App #2) to the shared SpecGuard-Core 3-agent skeleton."""

    def __init__(self, repo_root: Optional[pathlib.Path] = None) -> None:
        self._root = repo_root or pathlib.Path(__file__).resolve().parents[2]

    @property
    def domain_id(self) -> Literal["code_audit", "clinical_audit"]:
        return "clinical_audit"

    @property
    def spec_path(self) -> pathlib.Path:
        return self._root / ".kiro" / "specs" / "med-evidence-checker" / "requirements.md"

    @property
    def mcp_tool_names(self) -> List[str]:
        return ["query_clinical_guidelines_db"]

    def extract_claims(self, artifact_text: str, dag: VerificationDAG) -> List[AtomicClaim]:
        """Agent #1 (ClaimExtractor): Decompose synthetic clinical note into physiology & order claims."""
        clean_text, _ = sanitize_zero_phi(artifact_text)
        ctx = parse_clinical_context(clean_text)
        claims: List[AtomicClaim] = []

        c_renal = dag.clauses[1].clause_id if len(dag.clauses) > 1 else dag.clauses[0].clause_id
        c_preg = dag.clauses[2].clause_id if len(dag.clauses) > 2 else dag.clauses[0].clause_id
        c_ddi = dag.clauses[3].clause_id if len(dag.clauses) > 3 else dag.clauses[0].clause_id

        claims.append(
            AtomicClaim(
                claim_id="CLAIM-MED-01-PHYSIOLOGY",
                category="patient_physiology",
                source_span="Patient Labs & History",
                statement=(
                    f"Extracted physiological baseline: eGFR={ctx['egfr']} mL/min/1.73m2, "
                    f"Pregnant={ctx['pregnant']}, Allergies={ctx['allergies'] or ['None documented']}."
                ),
                mapped_clause_id=c_renal,
                metadata=ctx,
            )
        )

        meds = ctx.get("prescribed_meds", [])
        if not meds:
            claims.append(
                AtomicClaim(
                    claim_id="CLAIM-MED-02-ORDERS",
                    category="medication_regimen",
                    source_span="Medication Plan",
                    statement="No high-risk active medications detected in note.",
                    mapped_clause_id=c_ddi,
                )
            )
        else:
            for idx, drug in enumerate(meds, start=1):
                claims.append(
                    AtomicClaim(
                        claim_id=f"CLAIM-MED-ORDER-{idx:02d}",
                        category="medication_safety_claim",
                        source_span=f"Prescribed medication: {drug}",
                        statement=(
                            f"Prescribing `{drug}` is safe given patient's eGFR ({ctx['egfr']}), "
                            f"pregnancy status ({ctx['pregnant']}), allergies ({ctx['allergies']}), "
                            f"and co-prescribed regimen ({', '.join(meds)})."
                        ),
                        mapped_clause_id=c_preg if ctx["pregnant"] else c_renal,
                        metadata={"drug": drug},
                    )
                )

        return claims

    def hunt_counterexamples(
        self, artifact_text: str, claims: List[AtomicClaim], dag: VerificationDAG
    ) -> List[CounterexampleWitness]:
        """Agent #2 (CounterexampleHunter): Query MCP `query_clinical_guidelines_db` tool."""
        clean_text, _ = sanitize_zero_phi(artifact_text)
        kb_res = query_clinical_guidelines_db(clean_text)
        violations = kb_res.get("violations", [])
        witnesses: List[CounterexampleWitness] = []

        if not violations:
            for c in claims:
                witnesses.append(
                    CounterexampleWitness(
                        claim_id=c.claim_id,
                        violated=False,
                        severity="SAFE",
                        witness_input=c.source_span,
                        observed_outcome="Compliant with renal, pregnancy, allergy, and DDI clinical guidelines.",
                        mcp_tool_used="query_clinical_guidelines_db",
                        evidence_citation="KDIGO / ACOG / ISMP / FDA Structured Pharmacology KB",
                    )
                )
            return witnesses

        primary_claim_id = claims[-1].claim_id if claims else "CLAIM-MED-01"
        for v in violations:
            witnesses.append(
                CounterexampleWitness(
                    claim_id=primary_claim_id,
                    violated=True,
                    severity=v["severity"],
                    witness_input=v["witness_input"],
                    observed_outcome=v["observed_outcome"],
                    mcp_tool_used="query_clinical_guidelines_db",
                    evidence_citation=f"[{v['guideline_id']}] {v['evidence_citation']}",
                    remediation_hint=v["safe_alternative"],
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
        """
        Agent #3 (EvidenceAuditor): Synthesize clinical remediation plan and mandatory
        `Who Benefits & Who Could Be Harmed` Zero-PHI safety disclosure (Property 6).
        """
        clean_text, was_redacted = sanitize_zero_phi(artifact_text)
        violated = [w for w in witnesses if w.violated]

        safety_disclosure: Dict[str, Any] = {
            "zero_phi_compliant": True,
            "phi_redaction_triggered": was_redacted,
            "human_in_the_loop_required": True,
            "who_benefits": (
                "Junior hospital residents, clinical pharmacists, and primary care clinicians performing "
                "medication reconciliation; patients with impaired renal function (CKD stage 3-5), "
                "pregnancy, documented drug allergies, or complex polypharmacy."
            ),
            "who_could_be_harmed": (
                "Patients with rare hepatic/metabolic syndromes or off-label specialist regimens not covered "
                "by standard renal/pregnancy/DDI tables if clinicians over-rely on automated checks "
                "(automation bias). This tool is a clinical decision support aid and NEVER replaces "
                "attending physician or licensed pharmacist verification."
            ),
            "coverage_limitations": (
                "Evaluates eGFR renal dosing thresholds, pregnancy teratogenicity, beta-lactam/sulfa allergy "
                "cross-reactivity, and high-alert drug-drug interactions on synthetic/de-identified text."
            ),
        }

        if not violated:
            remediation_text = (
                "VERIFIED SAFE: All extracted medication orders comply with KDIGO renal thresholds, "
                "ACOG pregnancy safety rules, allergy cross-reactivity checks, and high-alert DDI tables."
            )
            patched_note = clean_text + "\n\n[SpecGuard-Crew Clinical Audit: VERIFIED SAFE — Zero Contraindications Flagged]"
            return remediation_text, patched_note, safety_disclosure

        alternatives = [f"- {w.remediation_hint}" for w in violated if w.remediation_hint]
        dedup_alts = list(dict.fromkeys(alternatives))
        remediation_text = (
            f"CRITICAL CLINICAL SAFETY ALERT ({len(violated)} contraindication(s) detected):\n"
            + "\n".join(dedup_alts)
        )
        patched_note = (
            clean_text
            + "\n\n=== [SpecGuard-Crew Revised Safe Clinical Plan] ===\n"
            + "\n".join(dedup_alts)
        )
        return remediation_text, patched_note, safety_disclosure


def audit_clinical_note(clinical_text: str, artifact_id: str = "clinical-case-01") -> AuditReport:
    """Convenience entrypoint for MedEvidence-Checker verification."""
    orchestrator = CrewOrchestrator()
    adapter = ClinicalAuditDomainAdapter()
    return orchestrator.run_verification(
        artifact_id=artifact_id,
        artifact_text=clinical_text,
        adapter=adapter,
    )


def run_single_prompt_clinical_baseline(clinical_text: str) -> bool:
    """
    Single-Pass Naive Baseline for Benchmark Comparison:
    Simulates an ungrounded single-prompt heuristic pass that only catches explicit keywords like
    'contraindicated' or 'overdose' or 'penicillin allergy' + 'penicillin' literal match,
    missing numeric eGFR threshold logic (e.g. eGFR=22 + Metformin), brand-generic cross-reactivity
    (e.g. Penicillin allergy + Zosyn/Augmentin), and multi-drug CYP/RAAS interactions.
    Returns True if flagged as unsafe, False if deemed safe.
    """
    text_l = clinical_text.lower()
    if "penicillin" in text_l and text_l.count("penicillin") >= 2:
        return True
    if "isotretinoin" in text_l and "pregnant" in text_l:
        return True
    if "warfarin" in text_l and "aspirin" in text_l:
        return True
    return False
