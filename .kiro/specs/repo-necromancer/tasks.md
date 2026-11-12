# Implementation Plan: RepoNecromancer (`apps/repo-necromancer`)

- [ ] 1. Implement MCP Code & Property-Based Test Sandbox (`packages/specguard-mcp-server/tools_code_sandbox.py`)
  - Implement AST security detector and `Hypothesis` property runner for boundary/overflow/injection/precision invariants.
  - _Requirements: 1.2, 2.1, 2.2_

- [ ] 2. Implement `RepoNecromancer` Standalone Application (`apps/repo-necromancer/`)
  - [ ] 2.1 Implement `CodeAuditDomainAdapter` connecting `apps/repo-necromancer` to `packages/specguard-core`.
  - [ ] 2.2 Add curated real-world legacy bug presets and benchmark dataset (`benchmarks/dataset_code_bugs.json`).
  - [ ] 2.3 Write property and integration tests in `tests/test_repo_necromancer.py`.
  - _Requirements: 1.1, 2.1, 3.1_
