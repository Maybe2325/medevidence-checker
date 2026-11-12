---
title: "How We Built SpecGuard-Crew with Kiro: One EARS + PBT Verification Skeleton Powering Code Security & Clinical Safety"
published: true
tags: kiro, kiroween, ai, python
---

# How We Built SpecGuard-Crew with Kiro: One EARS + PBT Verification Skeleton Powering Code Security & Clinical Safety

When building with Large Language Models in high-stakes domains—whether **auditing untrusted code** or **reviewing clinical discharge summaries**—the core failure mode is identical: **plausible-sounding hallucinations and silent boundary violations**.

For **Kiroween 2026 (`Skeleton Crew` Category)**, we wanted to prove that formal multi-agent verification doesn't need to be reinvented for every domain. Using **Kiro** (`Specs`, `Property-Based Testing`, `Steering Docs`, `Agent Hooks`, `Custom Agents / Kiro Crew`, `MCP`, and `Powers`), we built **SpecGuard-Crew**: a lean (<800 LOC) verification skeleton (`packages/specguard_core`) that powers **two radically different applications** from the exact same 3-agent foundation:

1. **🎃 App #1: `RepoNecromancer` (`apps/repo-necromancer`)** — A DevSecOps & legacy code resurrection workbench that compiles formal EARS specifications, runs **Hypothesis Property-Based Testing (PBT)** in an MCP sandbox to shrink minimal falsifying inputs, and synthesizes verified patches.
2. **🩺 App #2: `MedEvidence-Checker` (`apps/med-evidence-checker`)** — A Zero-PHI clinical decision support dashboard that decomposes clinical notes into physiological parameters (`eGFR`, pregnancy, allergies) and medication orders, cross-examining them against KDIGO/ACOG/ISMP pharmacology guidelines via MCP.

---

## 1. Spec-Driven Development with Kiro EARS Syntax (`/.kiro/specs/`)

Instead of starting with ad-hoc prompts, we started in `/.kiro/specs/` by writing formal **EARS (Easy Approach to Requirements Syntax)** clauses across three modules (`skeleton-core`, `repo-necromancer`, and `med-evidence-checker`):

```markdown
1. WHEN a markdown specification document containing EARS clauses is provided to the EARSCompiler, THE specguard-core SHALL extract each clause into a typed InvariantNode.
2. WHEN eGFR is below 30 mL/min/1.73m2 AND Metformin is prescribed, THE MedEvidence-Checker SHALL flag a CRITICAL renal contraindication.
```

Then we took Spec-Driven Development one step further: our runtime `EARSCompiler` (`packages/specguard_core/compiler.py`) parses our actual `.kiro/specs/**/requirements.md` files into a deterministic `VerificationDAG` with a SHA-256 digest!

---

## 2. How Hypothesis Property-Based Testing (PBT) Caught a Real Bug in Our Own Patch Synthesizer

In `.kiro/specs/skeleton-core/design.md` and `.kiro/specs/repo-necromancer/design.md`, we defined **6 formal Correctness Properties** and mapped each one to a `@pytest.mark.property` `Hypothesis` test in `tests/test_skeleton_properties.py`.

When we first ran **Property 5 (Counterexample Reproducibility & Patch Soundness)**:

```python
@pytest.mark.property
@given(
    price=st.floats(min_value=10.0, max_value=5000.0, allow_nan=False, allow_infinity=False),
    discount=st.floats(min_value=1.05, max_value=10.0, allow_nan=False, allow_infinity=False),
)
def test_property_3_and_5_trace_completeness_and_patch_soundness(price: float, discount: float) -> None:
    ...
```

`Hypothesis` immediately falsified our initial patch synthesizer! Why? Our initial patch injector used a regex `r"def\s+\w+\(\s*(\w+)\s*,\s*(\w+)"` to locate parameter names, which failed whenever the target function had Python type annotations like `def calc_total(price: float, discount_rate: float) -> float:`. Switching to AST parameter extraction (`[a.arg for a in funcs[0].args.args]`) fixed the bug permanently and brought all 13 test suites (including hundreds of generated Hypothesis examples) to 100% green in `0.74s`.

---

## 3. Orchestrating the 3-Agent Kiro Crew + MCP Tools (`/.kiro/agents/` & `/.kiro/mcp/`)

Both applications share 100% of `CrewOrchestrator` (`packages/specguard_core/crew_orchestrator.py`), which executes three specialized Kiro Crew agents sequentially:

1. **`ClaimExtractor` (`.kiro/agents/claim-extractor.yaml`)**: Extracts AST boundary claims (for code) or physiological markers + prescribed drugs (for clinical notes).
2. **`CounterexampleHunter` (`.kiro/agents/counterexample-hunter.yaml`)**: Invokes our local JSON-RPC 2.0 MCP server (`packages/specguard_mcp_server/server.py` configured in `.kiro/mcp/mcp.json`)—calling `run_property_test_sandbox` for App #1 or `query_clinical_guidelines_db` for App #2.
3. **`EvidenceAuditor` (`.kiro/agents/evidence-auditor.yaml`)**: Enforces **Property 2 (Monotonic Severity Escalation)** and synthesizes either a PBT-verified Python patch or a safer clinical medication regimen with mandatory `Who Benefits & Who Could Be Harmed` Zero-PHI disclosures.

---

## 4. Quantitative Benchmark Results (`benchmarks/run_evaluation.py`)

We evaluated `SpecGuard-Crew` against a `Single-Prompt Baseline` across 15 code bug samples and 20 synthetic clinical vignettes:

- **App #1 (`RepoNecromancer`, N=15)**: Single-Prompt Baseline achieved `20.00%` Recall (`33.33%` F1), whereas **SpecGuard-Crew (Kiro + Hypothesis PBT)** achieved **`100.00%` Recall, `100.00%` Specificity, and `100.00%` F1**.
- **App #2 (`MedEvidence-Checker`, N=20, Zero-PHI)**: Single-Prompt Baseline achieved `8.33%` Recall (`15.38%` F1), whereas **SpecGuard-Crew (Kiro + MCP Clinical KB)** achieved **`100.00%` Recall, `100.00%` Specificity, and `100.00%` F1**.

By combining **Kiro Specs (EARS)**, **Agent Hooks**, **Steering Docs**, **Kiro Crew**, **MCP**, **Powers**, and **Hypothesis PBT**, Kiro turned formal verification from an academic exercise into a practical, reusable multi-agent skeleton!
