# 2m45s Demo Video Script & Storyboard (`SpecGuard-Crew`)

> **Target Duration**: `2 minutes 45 seconds` (`165 seconds`)  
> **Compliance**: Satisfies **Kiroween 2026** (`<= 3:00`) and **AI for Medicine** (`>= 1:00`, 100% real working software demonstration, zero copyrighted music).  
> **Effortless Recording Tip**: Open the Web Workbench (`http://localhost:8000` or `specguard_crew_workbench.html`) and click the **`🎬 Auto-Demo Tour`** button in the top-right corner—it automatically sequences through all 5 scenes below while you read the voiceover!

---

## Scene 1 (`0:00 – 0:30`): The Hook & Skeleton Crew Architecture
- **On Screen**:
  - Start on the **SpecGuard-Crew Dual-Application Workbench** (`App #1: RepoNecromancer` active in Haunted CRT mode).
  - Highlight the top **Shared Kiro Crew Skeleton Pipeline** ribbon (`1. ClaimExtractor` → `2. CounterexampleHunter` → `3. EvidenceAuditor`).
- **Voiceover (English)**:
  > *"Whether an AI is generating Python checkout code or drafting a hospital discharge summary, the most dangerous bugs are silent boundary violations. For Kiroween 2026's Skeleton Crew track and AI for Medicine, we built SpecGuard-Crew: a single, domain-agnostic 3-agent verification skeleton in Kiro that powers two completely different applications from the same formal foundation."*

---

## Scene 2 (`0:30 – 1:10`): Application #1 — `RepoNecromancer` (`apps/repo-necromancer`)
- **On Screen**:
  - In `App #1: RepoNecromancer`, select **`RN-PRESET-01: Ghost Discount Overflow`** and click **`⚡ Run 3-Agent EARS + Hypothesis PBT Audit`**.
  - Point to the shrunk counterexample (`calculate_checkout_total(100.0, 1.5) -> -50.0`) and the synthesized patch below it.
  - Switch dropdown to **`RN-PRESET-03: Cryptographic Timing Oracle`** to show `==` replaced by `hmac.compare_digest`.
- **Voiceover (English)**:
  > *"First is RepoNecromancer, our DevSecOps code auditor in `apps/repo-necromancer`. When given an AI-generated discount function, a naive single-prompt review sees no syntax errors and misses the bug. Our Kiro Crew compiles formal EARS specifications, invokes our MCP Hypothesis property-testing sandbox, shrinks the exact falsifying input `discount_rate=1.5` yielding `-50.0`, and synthesizes a verified patch. It also catches timing side-channels and command injection."*

---

## Scene 3 (`1:10 – 1:55`): Application #2 — `MedEvidence-Checker` (`apps/med-evidence-checker`)
- **On Screen**:
  - Click **`🩺 App #2: MedEvidence-Checker`** in the top bar (theme transitions cleanly to the sterile Clinical Precision Dashboard).
  - Show **`MED-PRESET-01: Stage 4 CKD Discharge Note (eGFR 22 + Metformin & Ibuprofen)`** and click **`🩺 Run 3-Agent Clinical Guideline & Contraindication Audit`**.
  - Point to the extracted physiology cards (`Renal eGFR: 22 mL/min`), the two `CRITICAL` KDIGO guideline citations, the recommended safe regimen (`Linagliptin + Acetaminophen`), and the mandatory **`Who Benefits, and Who Could Be Harmed` (Zero-PHI)** box.
  - Briefly select **`MED-PRESET-02 (First-Trimester Pregnancy)`** or **`MED-PRESET-03 (Penicillin Anaphylaxis + Zosyn Cross-Reactivity)`**.
- **Voiceover (English)**:
  > *"With one click, the exact same SpecGuard-Crew skeleton powers our second application in `apps/med-evidence-checker`: MedEvidence-Checker. Given a synthetic Stage 4 CKD discharge note with an eGFR of 22, ClaimExtractor isolates the patient's renal function and medication orders. CounterexampleHunter queries our Zero-PHI MCP pharmacology database, flagging critical risks for Metformin lactic acidosis and NSAID kidney injury, while EvidenceAuditor recommends safe renal-adjusted alternatives and attaches mandatory harm disclosures."*

---

## Scene 4 (`1:55 – 2:25`): Inside `/.kiro` Live Inspector & Terminal Proof
- **On Screen**:
  - Click **`⚡ /.kiro Live Inspector`** in the top bar to display all 21 compiled EARS clauses, the 3 Agent Hooks, 3 Steering Docs, Custom Agents, MCP config, and Kiro Power.
  - Switch briefly to the terminal running `python3 -m pytest` (`13 passed in 0.74s`) and `python3 -m packages.specguard_core.compiler --validate-all`.
- **Voiceover (English)**:
  > *"Under the hood, our root `/.kiro` directory integrates all seven Kiro capabilities: 21 EARS clauses across 3 spec modules, 6 formal Correctness Properties tested with Hypothesis PBT, Agent Hooks that validate specs and run property tests on save, Steering docs enforcing Zero-PHI and structural separation, custom Kiro Crew agents, our local MCP server, and a reusable Kiro Power."*

---

## Scene 5 (`2:25 – 2:45`): Quantitative Evaluation Benchmarks (`100% F1`)
- **On Screen**:
  - Click **`📊 Evaluation Benchmarks`** in the top bar (and/or show `python3 benchmarks/run_evaluation.py` output in terminal).
- **Voiceover (English)**:
  > *"Finally, we ran reproducible benchmarks across 15 code defect samples and 20 synthetic clinical vignettes. While the single-prompt baseline achieved only 20% recall on code bugs and 8.3% recall on clinical contraindications, SpecGuard-Crew achieved 100% recall, 100% specificity, and 100% F1 across both domains. Thank you!"*
