# Implementation Plan: SpecGuard-Core (`packages/specguard-core`)

- [x] 1. Define Pydantic v2 schemas and Kiro trace models (`packages/specguard-core/models.py`)
  - Implement `EARSClause`, `VerificationDAG`, `AtomicClaim`, `CounterexampleWitness`, `AgentTraceStep`, and `AuditReport`.
  - _Requirements: 1.1, 2.1_

- [ ] 2. Implement EARS Specification Compiler (`packages/specguard-core/compiler.py`)
  - [ ] 2.1 Implement regex & AST-assisted EARS parser supporting `WHEN`, `IF`, `WHILE`, and `WHERE` clauses with `THE <system> SHALL`.
  - [ ] 2.2 Write property-based test for **Property 1: EARS Compilation Idempotence & Round-Trip Determinism** in `tests/test_skeleton_properties.py`.
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 3. Implement 3-Agent Kiro Crew Orchestrator (`packages/specguard-core/crew_orchestrator.py`)
  - [ ] 3.1 Implement `ClaimExtractor`, `CounterexampleHunter`, and `EvidenceAuditor` pipeline with automatic `.kiro/` artifact trace attribution.
  - [ ] 3.2 Implement `LLMAdapter` (`packages/specguard-core/llm_adapter.py`) supporting OpenAI-compatible Live endpoints (`Qwen3`, `DeepSeek`) and deterministic fallback.
  - [ ] 3.3 Write property-based tests for **Property 2: Monotonic Severity Escalation** and **Property 3: 3-Agent Trace Completeness**.
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 4. Implement Quantitative Benchmark Evaluator (`packages/specguard-core/evaluator.py`)
  - [ ] 4.1 Implement confusion matrix and metric calculator (`precision`, `recall`, `specificity`, `f1_score`, `false_negative_rate`).
  - [ ] 4.2 Write property-based test for **Property 4: Confusion Matrix Metric Bounds & Zero-Division Safety**.
  - _Requirements: 3.1, 3.2_
