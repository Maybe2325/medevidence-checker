---
inclusion: always
---

# Structural Steering: Monorepo & Skeleton Crew Separation

## 1. Root Directory Invariants
- **`/.kiro/` MUST remain at the repository root** and MUST NOT be ignored in `.gitignore`.
- **`LICENSE` (MIT)** and **`README.md`** MUST remain at the repository root.

## 2. Strict Separation Between Skeleton Core and Derived Apps
To satisfy the **Kiroween 2026 `Skeleton Crew`** requirement (*"Skeleton Crew: 2 separate folders for the 2 apps"*):
1. **`packages/specguard-core/` (Domain-Agnostic Skeleton)**:
   - Contains `compiler.py` (EARS specification parser & invariant DAG builder), `crew_orchestrator.py` (3-agent Kiro Crew coordinator), `models.py` (Pydantic schemas), and `evaluator.py` (quantitative benchmark engine).
   - **Rule**: `packages/specguard-core/` MUST NOT import from `apps/repo-necromancer` or `apps/med-evidence-checker`. It interacts with domain logic exclusively through abstract `DomainPlugin` / `MCPToolBinding` interfaces.
2. **`apps/repo-necromancer/` (Derived Application #1 — Software Security & PBT)**:
   - Standalone application folder for legacy code resurrection, EARS spec synthesis, `Hypothesis` property-based counterexample hunting, and automated patch verification.
   - Contains its own `app.py` / CLI / service module, domain prompts, presets, and `README.md`.
3. **`apps/med-evidence-checker/` (Derived Application #2 — Clinical Care & Evidence Audit)**:
   - Standalone application folder for clinical note decomposition, renal/teratogenic/interaction guideline verification, `Who Benefits & Who Could Be Harmed` safety analysis, and `README.md`.
4. **`packages/specguard-mcp-server/` (Shared Protocol Server)**:
   - Exposes MCP tools consumed by the Kiro Crew agents across both applications.
5. **`benchmarks/` (Reproducible Quantitative Evaluation)**:
   - Houses `dataset_code_bugs.json`, `dataset_clinical_cases.json`, and `run_evaluation.py` to generate side-by-side metrics comparing a Single-Prompt Baseline against `SpecGuard-Crew`.
