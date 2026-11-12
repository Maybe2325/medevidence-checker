# Application #1: RepoNecromancer (`apps/repo-necromancer`)

**Domain**: Software Engineering, DevSecOps & Legacy Code Resurrection  
**Powered By**: `packages/specguard_core` (`SpecGuard-Crew` 3-Agent Skeleton) + `packages/specguard_mcp_server` (`run_property_test_sandbox`)

## Overview
`RepoNecromancer` is the first standalone application built on the **SpecGuard-Crew** skeleton for the **Kiroween 2026 `Skeleton Crew` Category**. It takes brittle legacy functions or AI-generated code, maps them to formal **EARS (`WHEN ... THE SYSTEM SHALL ...`)** specifications in [`.kiro/specs/repo-necromancer/requirements.md`](../../.kiro/specs/repo-necromancer/requirements.md), executes **Property-Based Testing (`Hypothesis`)** + AST hazard analysis via MCP to shrink minimal falsifying counterexamples, and synthesizes verified patches.
