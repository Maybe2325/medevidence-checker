---
name: "specguard-verification-power"
displayName: "SpecGuard Multi-Agent Verification Power"
description: "Compiles formal EARS specifications into executable Hypothesis Property-Based Tests and MCP clinical/security audits using the SpecGuard-Crew 3-agent skeleton."
keywords:
  - "ears"
  - "property-based-testing"
  - "hypothesis"
  - "kiro-crew"
  - "clinical-safety"
  - "code-audit"
mcpServers:
  - "specguard-local-mcp"
---

# SpecGuard Multi-Agent Verification Power

## Overview
This Kiro Power equips agents with the **SpecGuard-Crew** verification workflow. It bridges `.kiro/specs/` EARS requirements directly to runtime **Property-Based Testing (PBT)** and **Model Context Protocol (MCP)** domain verifiers.

## Available MCP Tools
1. `run_property_test_sandbox`: Executes AST boundary analysis and `Hypothesis` property tests against target code functions, shrinking falsifying inputs to minimal counterexamples.
2. `query_clinical_guidelines_db`: Queries our Zero-PHI clinical pharmacology database for renal (`eGFR`) dosing thresholds, pregnancy teratogenicity, allergy cross-reactivity, and drug-drug interactions.
3. `list_compiled_ears_invariants`: Compiles all `.kiro/specs/**/requirements.md` files into an inspectable JSON invariant DAG.

## Recommended Workflow
1. Read `.kiro/steering/product.md` and `.kiro/steering/structure.md` to confirm domain boundaries (`apps/repo-necromancer` vs. `apps/med-evidence-checker`).
2. Compile EARS clauses via `list_compiled_ears_invariants`.
3. Execute the 3-agent pipeline (`ClaimExtractor` → `CounterexampleHunter` → `EvidenceAuditor`) and verify all `@pytest.mark.property` invariants pass.
