# Requirements Document: MedEvidence-Checker (Derived Application #2)

## Introduction
`MedEvidence-Checker` (`apps/med-evidence-checker`) is the second standalone application powered by the `SpecGuard-Crew` skeleton, also entered in **AI for Medicine 2026**. It verifies AI-generated clinical discharge summaries, triage notes, and medication plans against structured clinical pharmacology guidelines via MCP, catching life-threatening dosing errors, renal/hepatic contraindications, drug-drug interactions, and teratogenic risks while strictly enforcing **Zero-PHI** compliance.

---

## Requirements

### Requirement 1: Clinical Context & Medication Claim Extraction
**User Story:** As a hospital resident or clinical pharmacist, I want `MedEvidence-Checker` to decompose unstructured clinical notes into patient physiology parameters (eGFR, pregnancy status, allergies, age) and medication claims, so that each order can be checked against formal clinical EARS rules.

#### Acceptance Criteria
1. WHEN a synthetic clinical note or medication plan is submitted to `MedEvidence-Checker`, THE `ClaimExtractor` SHALL extract structured patient physiological markers (e.g., `eGFR`, `serum_creatinine`, `pregnancy_status`, `known_allergies`) and each prescribed drug with its dose and frequency.
2. WHEN eGFR is below `30 mL/min/1.73m2` AND `Metformin` (or another renally cleared contraindicated medication) is prescribed, THE `MedEvidence-Checker` SHALL flag a `CRITICAL` renal contraindication.
3. WHEN a patient is pregnant AND a known teratogenic agent (e.g., `Warfarin`, `Isotretinoin`, `Lisinopril`, `Methotrexate`) is prescribed, THE `MedEvidence-Checker` SHALL flag a `CRITICAL` pregnancy contraindication.

### Requirement 2: MCP Clinical Guideline Lookup & Evidence Citation
**User Story:** As a clinician, I want every flagged warning to cite a specific clinical guideline and interaction mechanism from the MCP knowledge base, so that I can trust and verify the alert.

#### Acceptance Criteria
1. WHILE `CounterexampleHunter` evaluates extracted medication claims, THE `MedEvidence-Checker` SHALL query the MCP tool `query_clinical_guidelines_db` to check renal thresholds, pregnancy safety categories, allergy cross-reactivity, and major drug-drug interactions.
2. WHEN a guideline violation is identified, THE `CounterexampleHunter` SHALL attach the exact guideline ID, clinical mechanism (e.g., lactic acidosis risk, CYP2C9 inhibition, teratogenicity), and evidence-based safe alternative.

### Requirement 3: Mandatory Ethics, Harm Analysis & Zero-PHI Guardrails
**User Story:** As a healthcare AI auditor, I want every report to explicitly state who benefits, who could be harmed, and verify zero PHI exposure.

#### Acceptance Criteria
1. WHEN `EvidenceAuditor` generates a clinical `AuditReport`, THE `MedEvidence-Checker` SHALL attach a structured `safety_disclosure` containing `who_benefits`, `who_could_be_harmed`, `coverage_limitations`, and `human_in_the_loop_required: True`.
2. IF an input text matches patterns indicative of real unmasked personal identifiers (e.g., SSN patterns), THEN THE `MedEvidence-Checker` SHALL redact or reject the input before processing to uphold the Zero-PHI mandate.
