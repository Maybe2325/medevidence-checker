"""Unit & Integration Tests for Derived Application #2: MedEvidence-Checker (`apps/med-evidence-checker`)."""

from __future__ import annotations

import pytest
from apps import med_evidence_adapter, med_evidence_presets
from packages.specguard_mcp_server.server import handle_mcp_request


@pytest.mark.integration
def test_med_evidence_presets_end_to_end() -> None:
    presets = med_evidence_presets.MED_EVIDENCE_PRESETS
    assert len(presets) >= 5

    # First 4 presets have planted high-risk contraindications
    for preset in presets[:4]:
        report = med_evidence_adapter.audit_clinical_note(
            preset["clinical_text"], artifact_id=preset["id"]
        )
        assert report.overall_status == "VIOLATION_DETECTED"
        assert any(w.violated and w.severity == "CRITICAL" for w in report.witnesses)
        assert report.safety_disclosure is not None
        assert report.safety_disclosure["zero_phi_compliant"] is True

    # 5th preset is a verified safe renal-adjusted regimen
    safe_preset = presets[4]
    safe_report = med_evidence_adapter.audit_clinical_note(
        safe_preset["clinical_text"], artifact_id=safe_preset["id"]
    )
    assert safe_report.overall_status == "VERIFIED_SAFE"


@pytest.mark.unit
def test_zero_phi_redaction_guardrail() -> None:
    note_with_ssn = (
        "Synthetic test with accidental SSN 123-45-6789. "
        "Patient eGFR 85. Allergies: NKDA. Plan: Acetaminophen 500 mg."
    )
    report = med_evidence_adapter.audit_clinical_note(note_with_ssn, artifact_id="phi-test")
    assert report.safety_disclosure is not None
    assert report.safety_disclosure["phi_redaction_triggered"] is True
    assert "123-45-6789" not in (report.patched_artifact or "")


@pytest.mark.unit
def test_mcp_server_clinical_kb_tool_call() -> None:
    resp = handle_mcp_request(
        {
            "jsonrpc": "2.0",
            "id": 99,
            "method": "tools/call",
            "params": {
                "name": "query_clinical_guidelines_db",
                "arguments": {
                    "clinical_text": "29yo pregnant female (1st trimester). Plan: Start Warfarin 5 mg daily."
                },
            },
        }
    )
    structured = resp["result"]["structuredContent"]
    assert structured["status"] == "VIOLATION_DETECTED"
    assert any(v["guideline_id"] == "OB-TERAT-002" for v in structured["violations"])
