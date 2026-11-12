# Application #2: MedEvidence-Checker (`apps/med-evidence-checker`)

**Domain**: Healthcare Clinical Decision Support & Medication Safety Verification (Zero-PHI)  
**Powered By**: `packages/specguard_core` (`SpecGuard-Crew` 3-Agent Skeleton) + `packages/specguard_mcp_server` (`query_clinical_guidelines_db`)

## Overview
`MedEvidence-Checker` is the second standalone application built on the **SpecGuard-Crew** skeleton (and entered in **AI for Medicine 2026**). It audits AI-generated clinical discharge notes and medication reconciliation plans against formal **EARS (`WHEN ... THE SYSTEM SHALL ...`)** specifications in [`.kiro/specs/med-evidence-checker/requirements.md`](../../.kiro/specs/med-evidence-checker/requirements.md) and structured clinical pharmacology guidelines (KDIGO renal thresholds, ACOG pregnancy teratogenicity, AAAAI allergy cross-reactivity, and ISMP high-alert drug-drug interactions).
