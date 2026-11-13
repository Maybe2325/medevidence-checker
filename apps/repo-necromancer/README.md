# 🧟 Application #1: Repo-Necromancer (`apps/repo-necromancer`)

> 🌐 **[English](#english) | [简体中文](#简体中文)**

---

<a name="english"></a>
## English: Legacy Code Verification & Self-Healing via SpecGuard-Crew

**Repo-Necromancer** is Application #1 built on the `packages/specguard_core` skeleton for the **Kiroween 2026 (`Skeleton Crew`)** hackathon. It resurrects haunted legacy Python functions by compiling `.kiro/specs/repo-necromancer/requirements.md` EARS invariants and hunting down minimal falsifying inputs via AST + **Hypothesis Property-Based Testing (PBT)** (`run_property_test_sandbox` MCP tool).

### Key Capabilities
1. **EARS Invariant Extraction (`ClaimExtractor`)**: Extracts mathematical and security invariants (division-by-zero guards, bounded discount clamping, constant-time HMAC comparison, mutable default state isolation).
2. **Hypothesis PBT Counterexample Shrinking (`CounterexampleHunter`)**: Invokes `run_property_test_sandbox` to shrink minimal crashing or invariant-violating inputs (e.g., `discount_rate=1.25` yielding `-25.0`, or `weights=[]` raising `ZeroDivisionError`).
3. **Verified Self-Healing Patch Synthesis (`EvidenceAuditor`)**: Synthesizes an AST-verified patch and re-runs the PBT harness to guarantee `0 VIOLATED` obligations before issuing a SHA-256 `AuditCertificate`.

### Quick CLI Usage
```bash
python3 apps/repo-necromancer/cli.py --preset NECRO-01
```

---

<a name="简体中文"></a>
## 简体中文：基于 SpecGuard-Crew 的遗留代码边界猎杀与自愈应用

**Repo-Necromancer（代码死灵法师）** 是基于 `packages/specguard_core` 通用核查骨架构建的 **第一个垂直领域应用（软件工程与代码安全）**。它将 `.kiro/specs/repo-necromancer/requirements.md` 中的 EARS 规格编译为形式化核查义务，并通过 MCP 工具调用 `run_property_test_sandbox`（AST 静态危险扫描 + **Hypothesis 属性测试反例收缩**），自动寻找令遗留 Python 函数崩溃或违背数学不变量的最小反例证人（Counterexample Witness），进而合成经过二次属性测试验证的自愈补丁。

### 核心能力
1. **EARS 契约提取（`ClaimExtractor`）**：自动识别数值边界、除零风险、可变默认参数泄露、非恒定时间密钥比较等安全契约。
2. **Hypothesis 最小反例猎杀（`CounterexampleHunter`）**：构造确定性反例输入（例如 `discount_rate=1.25` 导致结算金额为负 `-25.0`，或空数组触发 `ZeroDivisionError`）。
3. **AST 补丁合成与二次验证（`EvidenceAuditor`）**：自动生成修复补丁并重新运行属性测试沙盒，确认所有 EARS 义务均为 `VERIFIED` 后签发 SHA-256 审计证书。
