# Requirements Document: SpecGuard-Core Verification Skeleton

## Introduction
`specguard-core` is the domain-agnostic multi-agent verification skeleton at the heart of **SpecGuard-Crew**. It compiles formal EARS specifications into executable verification graphs and coordinates a 3-agent Kiro Crew (`ClaimExtractor` → `CounterexampleHunter` → `EvidenceAuditor`) via Model Context Protocol (MCP) tools.

## Glossary
- **EARS_Clause**: A formal requirement statement structured using Easy Approach to Requirements Syntax (`WHEN`, `IF/THEN`, `WHILE`, `WHERE ... THE SYSTEM SHALL ...`).
- **Verification_DAG**: A directed acyclic graph of atomic claims and invariant checks produced by compiling one or more `EARS_Clause` entries.
- **Crew_Orchestrator**: The 3-agent state machine coordinating `ClaimExtractor`, `CounterexampleHunter`, and `EvidenceAuditor`.
- **Counterexample_Witness**: A concrete, minimal input or domain rule citation that falsifies a claim.

---

## Requirements

### Requirement 1: EARS Specification Parsing & Invariant Compilation
**User Story:** As a verification architect, I want the skeleton to parse formal EARS requirement clauses into structured invariant objects, so that the same compiler can validate both software specifications and clinical safety guidelines.

#### Acceptance Criteria
1. WHEN a markdown specification document containing EARS clauses is provided to the `EARSCompiler`, THE `specguard-core` SHALL extract each `WHEN/IF/WHILE/WHERE ... THE SYSTEM SHALL ...` clause into a typed `InvariantNode` with a deterministic `invariant_id`, trigger condition, and normative requirement.
2. IF an input specification contains no valid `THE SYSTEM SHALL` clauses, THEN THE `specguard-core` SHALL return a structured `SpecCompilationError` identifying the line numbers that failed validation rather than silently producing an empty graph.
3. WHEN identical EARS specification text is compiled multiple times, THE `specguard-core` SHALL produce byte-identical serialized `VerificationDAG` outputs (idempotence).

### Requirement 2: Domain-Agnostic 3-Agent Kiro Crew Orchestration
**User Story:** As a developer building multiple applications on one skeleton, I want a domain-agnostic 3-agent orchestration pipeline, so that `RepoNecromancer` and `MedEvidence-Checker` share 100% of their core control flow.

#### Acceptance Criteria
1. WHEN a verification job is submitted with a `domain_plugin` (`code_audit` or `clinical_audit`), THE `CrewOrchestrator` SHALL execute `ClaimExtractor`, `CounterexampleHunter`, and `EvidenceAuditor` in strict sequential order and record an immutable `AgentTraceStep` for each stage.
2. WHILE `CounterexampleHunter` is executing, THE `CrewOrchestrator` SHALL invoke only the MCP tools registered for the active `domain_plugin` and attach raw tool outputs as verifiable evidence.
3. IF `CounterexampleHunter` discovers one or more `Counterexample_Witness` instances with severity `CRITICAL`, THEN THE `EvidenceAuditor` SHALL classify the overall artifact status as `VIOLATION_DETECTED` and synthesize a remediation block.
4. IF no external LLM API key is configured in the runtime environment, THEN THE `CrewOrchestrator` SHALL seamlessly execute using the deterministic rule-guided and replay adapter without raising authentication exceptions.

### Requirement 3: Quantitative Baseline Comparison Engine
**User Story:** As a researcher evaluating verification rigor, I want built-in quantitative benchmarking against a single-prompt baseline, so that I can measure precision, recall, F1, and hallucination reduction across domains.

#### Acceptance Criteria
1. WHEN `BenchmarkEvaluator.evaluate_suite()` is invoked on a labeled dataset of positive (defective/unsafe) and negative (safe) samples, THE `specguard-core` SHALL compute `precision`, `recall`, `specificity`, `f1_score`, and `false_negative_rate` for both the Single-Prompt Baseline and `SpecGuard-Crew`.
2. WHEN calculating metrics for any confusion matrix `(TP, FP, TN, FN)`, THE `BenchmarkEvaluator` SHALL enforce that `precision`, `recall`, `specificity`, and `f1_score` remain strictly bounded within `[0.0, 1.0]` and never raise a `ZeroDivisionError`.
