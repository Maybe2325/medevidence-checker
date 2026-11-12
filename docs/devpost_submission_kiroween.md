# Kiroween 2026 Devpost Submission Form Answers (`SpecGuard-Crew`, ID: 1542903)

Below are the exact ready-to-submit answers mapped to all 20 official fields (`get_submission_requirements` schema) of **Kiroween 2026**.

---

### Field 1 (`id: 29617`): Age of Majority Checkbox
- **Value**: `true` (Checked)

### Field 2 (`id: 29638`): Eligible Jurisdiction Checkbox
- **Value**: `true` (Checked)

### Field 3 (`id: 29618`): Category
- **Value**: `Skeleton Crew`

### Field 4 (`id: 29619`): Public GitHub (NO GitLab or BitBucket) repo URL
- **Value**: `https://github.com/<YOUR_GITHUB_USERNAME>/specguard-crew`
- **Checklist Reminder**:
  - Repository is Public on GitHub.
  - MIT License is visible in the GitHub "About" section (top right).
  - `/.kiro` directory is at the repository root and NOT ignored in `.gitignore`.
  - Contains 2 separate folders for the 2 applications: `apps/repo-necromancer` and `apps/med-evidence-checker`.

### Field 5 (`id: 29620`): Provide a URL to a working demo, hosted application or test build of your project
- **Value**: `<YOUR_DEPLOYED_DEMO_URL_OR_GITHUB_PAGES_URL>`

### Field 6 (`id: 29621`): Testing instructions or credentials the judges need to test your project, if any
```text
Zero configuration or API keys required!
1. Open the Hosted Workbench URL.
2. Click "🎬 Auto-Demo Tour" in the top bar for a guided 5-scene walkthrough of both derived applications, the /.kiro Live Inspector, and the evaluation benchmarks.
3. Or manually switch between:
   - "🎃 App #1: RepoNecromancer (apps/repo-necromancer)" to test Python AST + Hypothesis Property-Based Testing (PBT) counterexample shrinking and patch synthesis.
   - "🩺 App #2: MedEvidence-Checker (apps/med-evidence-checker)" to test Zero-PHI clinical note decomposition and MCP guideline verification.
   - "⚡ /.kiro Live Inspector" to inspect all 21 compiled EARS clauses, Agent Hooks, Steering Docs, Kiro Crew agents, MCP tools, and Kiro Power.
4. To reproduce locally in <60 seconds:
   git clone <REPO_URL> && cd specguard-crew
   pip install pytest hypothesis pydantic fastapi uvicorn httpx pyyaml
   python3 -m pytest
   python3 benchmarks/run_evaluation.py
```

### Field 7 (`id: 29622`): Explain how your project meets the main technology requirement
*(Must name each Kiro product used: Kiro tools, custom agents, hooks, specs, steering, MCP, PBT, powers)*
```text
SpecGuard-Crew integrates every core Kiro capability inside our root `/.kiro/` directory (21 tracked configuration and specification files) to build a single verification skeleton (`packages/specguard_core`) powering two distinct applications (`apps/repo-necromancer` and `apps/med-evidence-checker`):

1. Kiro Specs (`/.kiro/specs/`):
   We authored 3 full specification suites (`skeleton-core`, `repo-necromancer`, `med-evidence-checker`), each containing `requirements.md` written in formal EARS syntax (`WHEN/IF/WHILE/WHERE ... THE SYSTEM SHALL ...` — 21 compiled EARS clauses in total), `design.md` defining 6 formal Correctness Properties, and `tasks.md`. Even further, our runtime `EARSCompiler` (`packages/specguard_core/compiler.py`) parses these exact `.kiro/specs/**/requirements.md` files into executable `VerificationDAG` graphs.

2. Property-Based Testing (`PBT`):
   We used PBT at two levels:
   (a) Development-time PBT (`tests/test_skeleton_properties.py`): All 6 Correctness Properties in `.kiro/specs/*/design.md` (EARS Compilation Idempotence, Monotonic Severity Escalation, 3-Agent Trace Completeness, Confusion Matrix Bounds, Patch Soundness, and Clinical Contraindication Non-Suppression) are verified via `@pytest.mark.property` `Hypothesis` `@given(...)` tests. During development, Hypothesis caught a real regex bug in our patch synthesizer when handling type-annotated parameters (`price: float`), prompting our switch to AST parameter extraction.
   (b) Runtime PBT (`packages/specguard_mcp_server/tools_code_sandbox.py`): `RepoNecromancer` runs property probes against submitted code to shrink minimal falsifying counterexamples (e.g., `discount_rate=1.5` yielding negative checkout totals or `[]` triggering `ZeroDivisionError`).

3. Kiro Steering (`/.kiro/steering/`):
   - `product.md`: Enforces dual-application boundaries and strict Zero-PHI clinical safety guardrails.
   - `tech.md`: Enforces Hypothesis PBT conventions and dual-mode LLM execution (supporting open-weight models Qwen3 Coder Next / DeepSeek 3.2 alongside deterministic offline execution).
   - `structure.md`: Enforces strict architectural decoupling so `packages/specguard_core` never imports from `apps/repo-necromancer` or `apps/med-evidence-checker`.

4. Kiro Agent Hooks (`/.kiro/hooks/`):
   - `spec-to-schema-sync.yaml`: Triggers `onFileSave` for `.kiro/specs/**/*.md` to run `python3 -m packages.specguard_core.compiler --validate-all`.
   - `property-test-guard.yaml`: Triggers `onFileSave` for `packages/**/*.py` and `apps/**/*.py` to run `pytest -m property`.
   - `benchmark-report-updater.yaml`: Triggers `onFileSave` for `benchmarks/*` to recompute Precision/Recall/F1 tables via `benchmarks/run_evaluation.py`.

5. Custom Agents & Kiro Crew (`/.kiro/agents/`):
   We defined 3 specialized agents (`claim-extractor.yaml`, `counterexample-hunter.yaml`, `evidence-auditor.yaml`) orchestrated sequentially via `crew-pipeline.yaml` and `CrewOrchestrator` (`packages/specguard_core/crew_orchestrator.py`). Every verification report includes an immutable 3-step `kiro_trace` linking runtime outputs back to their `.kiro/` definitions.

6. Model Context Protocol (`MCP` — `/.kiro/mcp/mcp.json`):
   We built a custom JSON-RPC 2.0 MCP server (`packages/specguard_mcp_server/server.py`) exposing 3 tools: `run_property_test_sandbox` (for `RepoNecromancer`), `query_clinical_guidelines_db` (for `MedEvidence-Checker`), and `list_compiled_ears_invariants`.

7. Kiro Powers (`/.kiro/powers/specguard-verification-power/POWER.md`):
   We packaged our EARS-to-PBT and multi-agent MCP verification workflow into a reusable Kiro Power (`POWER.md`) with frontmatter, tool bindings, and onboarding instructions.
```

### Field 8 (`id: 29623`): Disclose any pre-existing code or work you used
```text
100% of the SpecGuard-Crew codebase, `.kiro` specifications, MCP server, benchmarks, and web workbench were created from scratch during the Kiroween 2026 submission period. We used standard open-source libraries (FastAPI, Pydantic, Hypothesis, Pytest, Tailwind CSS) and grounded our synthetic clinical rules in publicly available FDA/KDIGO/ACOG/ISMP clinical guidelines.
```

### Field 9 (`id: 29624`): Which Bonus Prizes are you entering?
- **Select**:
  - `Best Student (must provide LinkedIn profiles, students emails, year and degree, and school name)`
  - `Best Kiro Crew App`
  - `Blog Prize`
  - `Social Blitz` *(if you post on X/LinkedIn with `#KiroweenHackathon26`)*

### Field 11 (`id: 29626`): Best Student Project Bonus Prize Details
```text
Confirmation: I am currently enrolled and attending classes as a graduate student at a recognized academic institution.
- Name: Vige Dihu
- Student Email: <YOUR_UNIVERSITY_EDU_CN_EMAIL>
- School Name: <YOUR_UNIVERSITY_ENGLISH_NAME>
- Year and Degree: <e.g., Master's Student (Graduate), Year 1, Computer Science>
- LinkedIn Profile: <YOUR_LINKEDIN_URL>
```

### Field 12 (`id: 29627`): Best Kiro Crew Bonus Prize Details
```text
GitHub Repository URL: https://github.com/<YOUR_GITHUB_USERNAME>/specguard-crew

Kiro Crew App Description & Features:
SpecGuard-Crew (`packages/specguard_core/crew_orchestrator.py` + `/.kiro/agents/crew-pipeline.yaml`) is a multi-agent verification system built on the Kiro Crew sequential orchestration pattern. It coordinates three specialized agents:
1. ClaimExtractor (`/.kiro/agents/claim-extractor.yaml`): Compiles formal EARS specifications (`/.kiro/specs/**/requirements.md`) into a `VerificationDAG` and decomposes untrusted source code or clinical notes into atomic claims.
2. CounterexampleHunter (`/.kiro/agents/counterexample-hunter.yaml`): Dynamically invokes domain-bound MCP tools (`run_property_test_sandbox` for code security or `query_clinical_guidelines_db` for clinical pharmacology) to hunt for falsifying counterexamples.
3. EvidenceAuditor (`/.kiro/agents/evidence-auditor.yaml`): Enforces formal Monotonic Severity Escalation (Property 2), synthesizes verified code patches or safer clinical regimens, and outputs a full 3-agent Kiro execution trace.
```

### Field 13 (`id: 29628`): Social Blitz Bonus Prize URL
- **Post Template (post on X / LinkedIn / Bluesky and paste URL here — MUST start with `#KiroweenHackathon26`)**:
```text
#KiroweenHackathon26 Just built SpecGuard-Crew with @kirodotdev for the Skeleton Crew track! 🎃⚡ One lean 3-agent Kiro Crew verification skeleton (EARS Specs + Hypothesis Property-Based Testing + MCP + Hooks + Powers) powering two distinct apps: RepoNecromancer (code security auditor) & MedEvidence-Checker (Zero-PHI clinical safety verifier) with 100% F1 on our evaluation benchmarks!
```

### Field 14 (`id: 29629`): Bonus Blog Prize URL
- Publish `docs/devto_blog_post.md` on `https://dev.to` and paste the public URL here.

### Field 15 (`id: 29630`): Were you registered for the Kiroween 2025 hackathon?
- **Value**: `No`

### Field 16 (`id: 29634`): Submitter Type
- **Value**: `Individual`

### Field 18 (`id: 29631`): Are you an employee of the hackathon sponsor (AWS)?
- **Value**: `No`

### Field 19 (`id: 29636`): How much did this hackathon help you develop new skills or knowledge?
- **Value**: `Significantly`

### Field 20 (`id: 29637`): How likely are you to use Kiro again, at work or in your personal projects?
- **Value**: `Very likely`
