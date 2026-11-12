"""Standalone CLI Entrypoint for MedEvidence-Checker (`apps/med-evidence-checker/cli.py`)."""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps import med_evidence_adapter, med_evidence_presets  # noqa: E402


def main() -> int:
    preset = med_evidence_presets.MED_EVIDENCE_PRESETS[0]
    report = med_evidence_adapter.audit_clinical_note(preset["clinical_text"], artifact_id=preset["id"])
    print(f"=== MedEvidence-Checker Clinical Safety Report ({report.artifact_id}) ===")
    print(f"Overall Status: {report.overall_status}")
    print(f"Compiled EARS Invariants: {report.compiled_invariants_count}")
    for w in report.witnesses:
        print(f"  - [{w.severity}] {w.witness_input} -> {w.observed_outcome}")
        if w.remediation_hint:
            print(f"    Safe Alternative: {w.remediation_hint}")
    print("\n--- Mandatory Safety & Harm Disclosure ---")
    if report.safety_disclosure:
        print("Who Benefits:", report.safety_disclosure.get("who_benefits"))
        print("Who Could Be Harmed:", report.safety_disclosure.get("who_could_be_harmed"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
