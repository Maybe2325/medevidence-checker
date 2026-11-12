# Implementation Plan: MedEvidence-Checker (`apps/med-evidence-checker`)

- [ ] 1. Implement MCP Clinical Guideline & Drug Interaction Knowledge Base (`packages/specguard-mcp-server/tools_clinical_kb.py`)
  - Implement structured rules for renal dosing (`eGFR` thresholds), pregnancy contraindications, penicillin/cephalosporin allergy cross-reactivity, and high-risk drug-drug interactions (`Warfarin`, `NSAIDs`, `Potassium-sparing diuretics`, `ACEi`, `SSRIs/MAOIs`, `Macrolides/Statins`).
  - _Requirements: 1.2, 1.3, 2.1, 2.2_

- [ ] 2. Implement `MedEvidence-Checker` Standalone Application (`apps/med-evidence-checker/`)
  - [ ] 2.1 Implement `ClinicalAuditDomainAdapter` with Zero-PHI guardrails and mandatory `Who Benefits & Who Could Be Harmed` disclosure blocks.
  - [ ] 2.2 Build 20 synthetic clinical evaluation cases (`benchmarks/dataset_clinical_cases.json`) and run `benchmarks/run_evaluation.py`.
  - [ ] 2.3 Write property and integration tests in `tests/test_med_evidence_checker.py`.
  - _Requirements: 1.1, 2.1, 3.1, 3.2_
