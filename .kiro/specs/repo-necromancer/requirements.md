# Requirements Document: RepoNecromancer (Derived Application #1)

## Introduction
`RepoNecromancer` (`apps/repo-necromancer`) is the first standalone application powered by the `SpecGuard-Crew` skeleton. It resurrects and audits brittle legacy code or AI-generated functions by extracting formal EARS specifications, running automated Property-Based Testing (`Hypothesis`) via MCP to hunt for minimal falsifying counterexamples, and synthesizing verified patches.

---

## Requirements

### Requirement 1: AST & Specification Claim Extraction
**User Story:** As a security or platform engineer auditing legacy code, I want `RepoNecromancer` to extract function signatures, preconditions, and implicit postconditions into EARS claims, so that hidden assumptions become explicitly testable.

#### Acceptance Criteria
1. WHEN a Python source snippet is submitted to `RepoNecromancer`, THE `ClaimExtractor` SHALL parse its AST and extract function signatures, boundary invariants, and security constraints mapped to `.kiro/specs/repo-necromancer/requirements.md`.
2. IF the submitted code contains dangerous sinks (`eval`, `exec`, `subprocess.Popen(..., shell=True)`, raw SQL string interpolation, or unchecked division/indexing), THEN THE `ClaimExtractor` SHALL emit a high-priority security invariant claim.

### Requirement 2: MCP Property-Based Counterexample Hunting
**User Story:** As a developer, I want `RepoNecromancer` to automatically execute Property-Based Tests (`Hypothesis`) against extracted invariants, so that I get concrete falsifying inputs instead of vague static warnings.

#### Acceptance Criteria
1. WHEN `CounterexampleHunter` evaluates an extracted code claim, THE `RepoNecromancer` SHALL invoke the MCP tool `run_property_test_sandbox` to test the target function across generated edge-case inputs (negative numbers, zero, NaN/Inf, empty collections, Unicode/SQL payloads, integer bounds).
2. WHEN a property violation or unhandled exception is triggered in the sandbox, THE `CounterexampleHunter` SHALL shrink and record the minimal falsifying input as a `CounterexampleWitness` with severity `CRITICAL`.

### Requirement 3: Verified Patch Synthesis
**User Story:** As a developer fixing a discovered bug, I want `RepoNecromancer` to generate a concrete code patch and re-verify that the patch eliminates the counterexample.

#### Acceptance Criteria
1. WHEN `EvidenceAuditor` receives one or more `CRITICAL` code witnesses, THE `RepoNecromancer` SHALL produce a remediated code snippet and verify that the previously falsifying input now passes without error.
