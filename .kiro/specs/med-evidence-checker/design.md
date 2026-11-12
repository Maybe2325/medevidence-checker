# Design Document: MedEvidence-Checker (`apps/med-evidence-checker`)

## 1. Domain Adapter Architecture
`MedEvidence-Checker` reuses 100% of `packages/specguard-core` (`EARSCompiler`, `CrewOrchestrator`, `BenchmarkEvaluator`) while injecting the `ClinicalAuditDomainAdapter` and binding the `query_clinical_guidelines_db` MCP tool.

```mermaid
sequenceDiagram
    participant Clinician as Resident / Pharmacist
    participant App2 as MedEvidence-Checker (App #2)
    participant Core as SpecGuard-Core Crew
    participant MCP as MCP Clinical Guideline DB (Zero-PHI)

    Clinician->>App2: Submit synthetic clinical discharge note
    App2->>Core: Start audit with ClinicalAuditDomainAdapter
    Core->>Core: Agent 1 (ClaimExtractor): Extract labs (eGFR, pregnancy, allergies) + meds
    Core->>MCP: Agent 2 (CounterexampleHunter): call query_clinical_guidelines_db
    MCP-->>Core: Return contraindication witness + guideline citation
    Core->>Core: Agent 3 (EvidenceAuditor): Generate safer regimen + Harm/Benefit Disclosure
    Core-->>App2: Clinical AuditReport + Quantitative Confidence + Kiro Trace
```

## 2. Formal Correctness Properties

### Property 6: Clinical Contraindication Non-Suppression & Harm Disclosure Invariant
*For any* synthetic patient profile with `eGFR < 30` prescribed `Metformin` (or `pregnant == True` prescribed `Lisinopril`/`Warfarin`), `MedEvidence-Checker` MUST emit at least one `CRITICAL` `CounterexampleWitness`, classify `overall_status` as `"VIOLATION_DETECTED"`, and include a non-empty `safety_disclosure` containing both `who_benefits` and `who_could_be_harmed`.
- **Validates**: Requirement 1.2, Requirement 1.3, Requirement 3.1
