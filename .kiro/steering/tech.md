---
inclusion: always
---

# Technical Steering: Stack, PBT & Verification Standards

## 1. Core Technology Stack
- **Backend & Core Skeleton**: Python 3.11+, FastAPI, Pydantic v2 (strict schema validation).
- **Property-Based Testing (PBT)**: `pytest` + `Hypothesis` (`@given(...)`) for both internal correctness property testing and runtime counterexample shrinking in `RepoNecromancer`.
- **Protocol Layer**: Model Context Protocol (`MCP`) JSON-RPC 2.0 server (`packages/specguard-mcp-server`).
- **Frontend Workbench**: React 18, TypeScript, Tailwind CSS, Lucide Icons, with a built-in **`.kiro` Live Inspector** drawer.

## 2. Dual-Mode LLM & Deterministic Replay Architecture
To guarantee 100% reliability in mainland China and for international hackathon judges:
- **Live Open-Weight / API Mode**: Supports OpenAI-compatible endpoints (`Qwen3 Coder Next`, `DeepSeek 3.2`, `GLM-5`, `SiliconFlow`) configured via environment variables (`SPECGUARD_LLM_API_KEY`, `SPECGUARD_LLM_BASE_URL`, `SPECGUARD_LLM_MODEL`).
- **Deterministic Replay & Rule-Guided Mode (Default Fallback)**: When no external API key is configured, the adapter automatically executes deterministic AST/rule extraction + real `Hypothesis` PBT execution + real MCP clinical database lookups. Never return mock/static placeholder errors.

## 3. Property-Based Testing (PBT) Mandate
Every formal Correctness Property defined in `.kiro/specs/*/design.md` MUST have a corresponding `@pytest.mark.property` test in `tests/test_skeleton_properties.py` decorated with `@given(...)` from `Hypothesis` and tagged with a docstring referencing `# Feature: <spec-name>, Property <N>: <property-title>`.

## 4. Security Rules
- Never hardcode API keys, OAuth tokens, or credentials in any tracked file.
- Execute untrusted code analysis in `RepoNecromancer` using Python `ast` static analysis and bounded `Hypothesis` property runners with strict timeouts (`max_examples=50`, `deadline=500`).
