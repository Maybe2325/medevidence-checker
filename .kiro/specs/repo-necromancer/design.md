# Design Document: RepoNecromancer (`apps/repo-necromancer`)

## 1. Domain Adapter Architecture
`RepoNecromancer` plugs into `packages/specguard-core` by implementing the `CodeAuditDomainAdapter` and binding the `run_property_test_sandbox` MCP tool from `packages/specguard-mcp-server`.

```mermaid
sequenceDiagram
    participant User as Engineer / Judge
    participant App1 as RepoNecromancer (App #1)
    participant Core as SpecGuard-Core Crew
    participant MCP as MCP Code Sandbox (Hypothesis)

    User->>App1: Submit legacy/AI code snippet
    App1->>Core: Start audit with CodeAuditDomainAdapter
    Core->>Core: Agent 1 (ClaimExtractor): AST + EARS Spec mapping
    Core->>MCP: Agent 2 (CounterexampleHunter): call run_property_test_sandbox
    MCP-->>Core: Return minimal falsifying input (e.g. amount=-0.01 or SQL payload)
    Core->>Core: Agent 3 (EvidenceAuditor): Synthesize & verify patch
    Core-->>App1: AuditReport + Patched Code + Kiro Trace
```

## 2. Formal Correctness Properties

### Property 5: Counterexample Reproducibility & Patch Soundness
*For any* buggy code sample in the `RepoNecromancer` benchmark where `run_property_test_sandbox` reports a falsifying `witness_input`, executing the original function on `witness_input` MUST trigger the violation, and executing the synthesized patched function on `witness_input` MUST satisfy the EARS postcondition without raising an unhandled exception.
- **Validates**: Requirement 2.2, Requirement 3.1
