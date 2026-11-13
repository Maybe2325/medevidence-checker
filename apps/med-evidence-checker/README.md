# 🩺 Application #2: MedEvidence-Checker (`apps/med-evidence-checker`)

> 🌐 **[English](#english) | [简体中文](#简体中文)**

---

<a name="english"></a>
## English: Zero-PHI Clinical Discharge Note & Pharmacology Safety Verifier

**MedEvidence-Checker** is Application #2 built on the `packages/specguard_core` skeleton, serving both **AI for Medicine 2026** and **Kiroween 2026 (`Skeleton Crew`)**. It audits synthetic, 100% de-identified (`Zero-PHI`) clinical discharge summaries against structured clinical pharmacology guidelines (`KDIGO 2024`, `ACOG`, `AAAAI`, `ISMP`) via the `query_clinical_guidelines_db` MCP tool.

### Key Capabilities
1. **Clinical Claim & Biomarker Extraction (`ClaimExtractor`)**: Extracts renal function (`eGFR`), pregnancy status, documented drug allergies, and active medication orders from discharge notes.
2. **Deterministic Pharmacology Counterexample Hunting (`CounterexampleHunter`)**: Queries `query_clinical_guidelines_db` to catch fatal contraindications (e.g., `Metformin` when `eGFR < 30 mL/min/1.73m2`, `Lisinopril` in pregnancy, `Penicillin -> Piperacillin` cross-reactivity, `Sertraline + Linezolid` serotonin syndrome) with **100.0% Recall** and **0.0% False Positive Rate** on `N=20` benchmark cases.
3. **Evidence-Graded Audit & Bilingual Patient Safety Checklist (`EvidenceAuditor`)**: Generates guideline-cited clinical remediation notes, mandatory non-prescriptive ethics disclosures, and a plain-language Patient Safety Checklist.

### Quick CLI Usage
```bash
python3 apps/med-evidence-checker/cli.py --preset MED-01
```

---

<a name="简体中文"></a>
## 简体中文：零隐私泄露（Zero-PHI）临床出院医嘱与循证药理学安全审计台

**MedEvidence-Checker（临床循证核查台）** 是基于 `packages/specguard_core` 通用核查骨架构建的 **第二个垂直领域应用（临床医疗决策支持与用药安全）**，专为 **AI for Medicine 2026** 与 **Kiroween 2026 (`Skeleton Crew`)** 打造。系统在 100% 本地脱敏（Zero-PHI）环境下运行，将出院小结中的实验室生理指标与处方医嘱同权威指南（`KDIGO 2024`、`ACOG`、`AAAAI`、`ISMP`）进行确定性比对。

### 核心能力
1. **生理指标与医嘱提取（`ClaimExtractor`）**：从出院记录中提取估算肾小球滤过率（`eGFR`）、妊娠状态、既往过敏史及拟开具处方列表。
2. **循证药理禁忌反例猎杀（`CounterexampleHunter`）**：通过 `query_clinical_guidelines_db` MCP 工具精准拦截高危禁忌（如 `eGFR < 30` 禁用二甲双胍、妊娠期禁用赖诺普利、青霉素过敏交叉反应、5-羟色胺综合征药物相互作用），在 `N=20` 临床基准集上实现 **100.0% 召回率** 与 **0.0% 误报率**。
3. **指南引文修正与患者安全核对清单（`EvidenceAuditor`）**：输出带权威指南条款引文的修正建议、强制性非处方伦理披露，以及面向患者与家属的通俗安全复查清单。
