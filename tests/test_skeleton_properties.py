"""Formal Property-Based Testing (PBT) Suite using Hypothesis mapped to `.kiro/specs/*/design.md`."""

from __future__ import annotations

import string
import pytest
from hypothesis import given, settings, strategies as st

from apps import med_evidence_adapter, repo_necromancer_adapter
from packages.specguard_core.compiler import EARSCompiler
from packages.specguard_core.crew_orchestrator import CrewOrchestrator
from packages.specguard_core.evaluator import BenchmarkEvaluator
from packages.specguard_core.models import CounterexampleWitness


_SAFE_TOKEN = st.text(
    alphabet=string.ascii_letters + string.digits + "_",
    min_size=3,
    max_size=24,
).filter(lambda s: s[0].isalpha())

_SAFE_PHRASE = st.lists(_SAFE_TOKEN, min_size=2, max_size=6).map(lambda words: " ".join(words))


@pytest.mark.property
@settings(max_examples=50, deadline=500)
@given(
    keyword=st.sampled_from(["WHEN", "IF", "WHILE", "WHERE"]),
    condition=_SAFE_PHRASE,
    actor=_SAFE_TOKEN,
    obligation=_SAFE_PHRASE,
)
def test_property_1_ears_compilation_idempotence_and_round_trip(
    keyword: str, condition: str, actor: str, obligation: str
) -> None:
    """
    # Feature: skeleton-core, Property 1: EARS Compilation Idempotence & Round-Trip Determinism
    Validates: Requirement 1.1, Requirement 1.3
    """
    compiler = EARSCompiler()
    connector = "THEN THE" if keyword == "IF" else "THE"
    raw_md = f"- {keyword} {condition}, {connector} {actor} SHALL {obligation}.\n"

    dag_1 = compiler.compile_text(raw_md, spec_name="pbt-spec")
    dag_2 = compiler.compile_text(raw_md, spec_name="pbt-spec")

    assert dag_1.digest == dag_2.digest
    assert len(dag_1.clauses) == 1
    clause = dag_1.clauses[0]
    assert clause.keyword == keyword
    assert clause.condition == condition
    assert clause.system_actor == actor
    assert clause.obligation == obligation

    rendered = compiler.render_dag_to_markdown(dag_1)
    dag_roundtrip = compiler.compile_text(rendered, spec_name="pbt-spec")
    assert dag_roundtrip.digest == dag_1.digest


@pytest.mark.property
@settings(max_examples=50, deadline=500)
@given(
    witness_specs=st.lists(
        st.tuples(
            st.booleans(),
            st.sampled_from(["CRITICAL", "WARNING", "INFO", "SAFE"]),
        ),
        min_size=1,
        max_size=15,
    )
)
def test_property_2_monotonic_severity_escalation(
    witness_specs: list[tuple[bool, str]]
) -> None:
    """
    # Feature: skeleton-core, Property 2: Monotonic Severity Escalation in Evidence Auditor
    Validates: Requirement 2.3
    """
    witnesses = [
        CounterexampleWitness(
            claim_id=f"C-{idx}",
            violated=violated,
            severity=sev,  # type: ignore[arg-type]
            witness_input="probe",
            observed_outcome="outcome",
            mcp_tool_used="test_tool",
            evidence_citation="cite",
        )
        for idx, (violated, sev) in enumerate(witness_specs)
    ]

    status = CrewOrchestrator.aggregate_status(witnesses)
    has_critical_violation = any(v and s == "CRITICAL" for v, s in witness_specs)
    has_any_violation = any(v for v, _ in witness_specs)

    if has_critical_violation:
        assert status == "VIOLATION_DETECTED"
    elif has_any_violation:
        assert status == "WARNING_ONLY"
    else:
        assert status == "VERIFIED_SAFE"


@pytest.mark.property
@settings(max_examples=20, deadline=1000)
@given(
    price=st.floats(min_value=10.0, max_value=5000.0, allow_nan=False, allow_infinity=False),
    discount=st.floats(min_value=1.05, max_value=10.0, allow_nan=False, allow_infinity=False),
)
def test_property_3_and_5_trace_completeness_and_patch_soundness(
    price: float, discount: float
) -> None:
    """
    # Feature: skeleton-core & repo-necromancer, Property 3 & Property 5:
    # 3-Agent Trace Completeness & Counterexample Patch Soundness
    Validates: Skeleton Requirement 2.1, RepoNecromancer Requirement 2.2 & 3.1
    """
    buggy_code = (
        "def calc_total(price: float, discount_rate: float) -> float:\n"
        "    return round(price * (1.0 - discount_rate), 2)\n"
    )
    report = repo_necromancer_adapter.audit_code_snippet(buggy_code, artifact_id="pbt-code")

    # Property 3: 3-Agent Trace Completeness Invariant
    assert len(report.kiro_trace) == 3
    assert [step.agent_id for step in report.kiro_trace] == [
        "ClaimExtractor",
        "CounterexampleHunter",
        "EvidenceAuditor",
    ]
    assert all(step.duration_ms >= 0.0 for step in report.kiro_trace)

    # Property 5: Counterexample Reproducibility & Patch Soundness
    assert report.overall_status == "VIOLATION_DETECTED"
    assert report.patched_artifact is not None
    ns_patched: dict = {}
    exec(compile(report.patched_artifact, "<patched>", "exec"), ns_patched)  # noqa: S102
    with pytest.raises(ValueError):
        ns_patched["calc_total"](price, discount)


@pytest.mark.property
@settings(max_examples=100, deadline=500)
@given(
    tp=st.integers(min_value=0, max_value=10000),
    fp=st.integers(min_value=0, max_value=10000),
    tn=st.integers(min_value=0, max_value=10000),
    fn=st.integers(min_value=0, max_value=10000),
)
def test_property_4_confusion_matrix_bounds_and_zero_division_safety(
    tp: int, fp: int, tn: int, fn: int
) -> None:
    """
    # Feature: skeleton-core, Property 4: Confusion Matrix Metric Bounds & Zero-Division Safety
    Validates: Requirement 3.1, Requirement 3.2
    """
    metrics = BenchmarkEvaluator.compute_metrics(tp=tp, fp=fp, tn=tn, fn=fn)
    assert metrics.total == tp + fp + tn + fn
    assert 0.0 <= metrics.precision <= 1.0
    assert 0.0 <= metrics.recall <= 1.0
    assert 0.0 <= metrics.specificity <= 1.0
    assert 0.0 <= metrics.f1_score <= 1.0
    assert 0.0 <= metrics.false_negative_rate <= 1.0
    assert 0.0 <= metrics.accuracy <= 1.0


@pytest.mark.property
@settings(max_examples=30, deadline=1000)
@given(
    egfr=st.integers(min_value=5, max_value=29),
    dose_mg=st.sampled_from([500, 850, 1000]),
)
def test_property_6_clinical_contraindication_non_suppression_and_harm_disclosure(
    egfr: int, dose_mg: int
) -> None:
    """
    # Feature: med-evidence-checker, Property 6: Clinical Contraindication Non-Suppression & Harm Disclosure
    Validates: MedEvidence-Checker Requirement 1.2, 1.3, 3.1
    """
    note = (
        f"Synthetic Patient: 66yo with T2DM. Labs: eGFR {egfr} mL/min/1.73m2. "
        f"Allergies: NKDA. Plan: Start Metformin {dose_mg} mg PO BID."
    )
    report = med_evidence_adapter.audit_clinical_note(note, artifact_id=f"pbt-clin-{egfr}")
    assert report.overall_status == "VIOLATION_DETECTED"
    assert any(w.violated and w.severity == "CRITICAL" for w in report.witnesses)
    assert report.safety_disclosure is not None
    assert report.safety_disclosure.get("zero_phi_compliant") is True
    assert bool(report.safety_disclosure.get("who_benefits"))
    assert bool(report.safety_disclosure.get("who_could_be_harmed"))
