---
inclusion: always
---

# Product Steering: SpecGuard-Crew

## 1. Product Vision & Skeleton Crew Mandate
**SpecGuard-Crew** is built for the **Kiroween 2026 `Skeleton Crew` Category** and **AI for Medicine 2026**.
Our core architectural thesis is that **formal verification of AI-generated artifacts**—whether untrusted source code or clinical medical notes—follows an isomorphic 3-stage pipeline:
1. **Claim Extraction (`ClaimExtractor`)**: Decompose an artifact into atomic, testable claims and formal EARS (`WHEN ... THE SYSTEM SHALL ...`) invariants.
2. **Adversarial Counterexample Search (`CounterexampleHunter`)**: Invoke domain-specific Model Context Protocol (MCP) tools (Property-Based Testing sandboxes or structured clinical guideline databases) to actively hunt for falsifying counterexamples.
3. **Evidence-Graded Audit (`EvidenceAuditor`)**: Synthesize a structured verification report with concrete counterexamples, severity grades, and verified remediation patches.

## 2. Two Distinct Derived Applications (Mandatory Separation)
The shared skeleton (`packages/specguard-core`) MUST power two distinct, full-featured applications housed in separate directories:
- **Application #1 (`apps/repo-necromancer`)**:
  - **Domain**: Software Engineering, DevSecOps, and Legacy Code Resurrection.
  - **Persona**: Security engineers and developers auditing legacy Python/TypeScript code or AI-generated pull requests.
  - **UI Aesthetic**: Haunted CRT / Necromancer Terminal (`#0a0d0e` obsidian background, `#00ff9d` phosphor green, `#a855f7` arcane purple).
- **Application #2 (`apps/med-evidence-checker`)**:
  - **Domain**: Clinical Decision Support & Medication Safety Verification.
  - **Persona**: Hospital residents, clinical pharmacists, and medical AI researchers auditing discharge summaries and medication orders.
  - **UI Aesthetic**: High-Contrast Clinical Precision Dashboard (`#f8fafc` sterile slate, `#0284c7` clinical cyan, `#dc2626` critical alert crimson).

## 3. Non-Negotiable Safety & Compliance Guardrails
- **Zero-PHI Mandate**: No Protected Health Information (PHI) or real patient records may ever enter the repository, logs, or test suites. All clinical test cases MUST be 100% synthetic vignettes or derived from public benchmarks (`PubMedQA`).
- **Explicit Scope & Harm Disclosure**: Every clinical verification output MUST include a `Who Benefits & Who Could Be Harmed` safety block and a human-in-the-loop sign-off reminder to prevent automation bias.
- **Zero-Configuration Judge Experience**: Judges testing the hosted application MUST be able to run end-to-end verifications immediately without supplying their own API keys, via our deterministic verified replay engine paired with optional live LLM inference.
