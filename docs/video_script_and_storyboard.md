# 2m45s Demo Video Script & Storyboard (`SpecGuard-Crew` & `MedEvidence-Checker`)

> **Target Duration**: `2 minutes 45 seconds` (`165 seconds`, `0:00 – 2:45`)  
> **Compliance**: Satisfies **Kiroween 2026** (`<= 3:00`) and **AI for Medicine 2026** (`>= 1:00`, 100% live working software demonstration, zero copyrighted music).  
> **1:1 Auto-Demo Sync**: Clicking **`🎬 Auto-Demo Tour`** in [`apps/web-workbench/index.html`](../apps/web-workbench/index.html) defaults to **`2:45` Voiceover Sync Mode** (`165s`), executing every UI transition, preset switch, and skeleton highlight at the exact timestamps below, and automatically stopping on Scene 5 (`✅ 演示完成`). Need a quick preview? Click **`⚡ 40s 速览`** (`40s Quick`).

---

## 🎥 使用 `📜 提词器 / Script` 单标签页高效录屏操作说明

使用工作台内置的 **同步倒计时 + 独立提词器弹窗**，可以在**单浏览器标签页录屏（OBS / QuickTime / Loom / 微信或系统区域录屏）**时让提词器**完全不入镜**、实现零剪辑一镜到底：

1. **打开线上或本地工作台**：访问部署好的 HTTPS 域名（或本地 `http://127.0.0.1:8001` / `8002`）。
2. **启动自动演示并立即暂停在 `0:00`**：
   - 点击右上角 **`🎬 Auto-Demo Tour`**（默认即为 **`2:45` 配音同步模式**）；
   - 立即按键盘 **`Space` 键**（或点击控制栏 **`⏸`**）暂停在 `0:00`（`本幕剩 30s · 总 0:00 / 2:45`）。
3. **弹出独立深色提词器窗口**：
   - 点击控制栏上的 **`📜 提词器 / Script`** 按钮，通过 `window.open` 弹出独立的深色提词器小窗口；
   - 将该提词器小窗口拖到**录屏框区域外**（或副屏 / 主屏侧边留白处），在提词器顶部可按需切换 **`双语` / `中文` / `EN`** 并通过 **`A-` / `A+`** 调整字号。
4. **开始录屏并按节奏照念**：
   - 只框选（或窗口捕获）**主工作台浏览器窗口**，开始录屏；
   - 按 **`Space`** 继续播放，主界面与提词器窗口会以 `200 ms` 精度实时同步当前幕倒计时、进度条、画面切换节点（包括 `0:54` 与 `1:40` 的半幕自动切题）以及下方完整中英文逐字配音稿；
   - 如需重录某一段，可使用控制栏 **`⏮` / `⏸` / `⏭`** 或键盘 **`←` / `Space` / `→`** 快捷键精确切幕；
   - 到 **`2:45`** 时，工作台会**稳稳停留在第五幕（定量评估基准）**并显示 **`✅ 演示完成`**（不会跳回第一幕），此时自然收尾即可停止录屏。

---

## Scene 1 (`0:00 – 0:30`, 30s): Hook & Shared Kiro Skeleton Crew Architecture

- **On-Screen Action (Auto-Synced)**:
  - Opens **App #1 (`RepoNecromancer`)** (`apps/repo-necromancer`) in Haunted Dark CRT theme with `RN-PRESET-01` loaded.
  - Animates a pulsing emerald/purple highlight border (`ribbon-spotlight`) around the top **`#skeleton-ribbon`** (`1. ClaimExtractor` → `2. CounterexampleHunter` → `3. EvidenceAuditor`).
- **Voiceover (English — Verbatim)**:
  > Whether an AI is generating Python checkout code or drafting a hospital discharge summary, the most dangerous bugs are silent boundary violations. For Kiroween 2026's Skeleton Crew track and AI for Medicine, we built SpecGuard-Crew: a single, domain-agnostic 3-agent verification skeleton in Kiro—ClaimExtractor, CounterexampleHunter, and EvidenceAuditor—that powers two completely different applications from the exact same formal foundation.
- **配音逐字稿（简体中文）**：
  > 无论是让 AI 生成 Python 结账代码，还是起草医院出院小结，最危险的缺陷往往是静默的边界违例。针对 Kiroween 2026 Skeleton Crew 赛道与 AI for Medicine，我们基于 Kiro 打造了 SpecGuard-Crew：一套与领域无关的三智能体核查骨架——依次经过断言提取、反例猎手与证据裁决——用同一套形式化底座驱动两个完全不同的应用。

---

## Scene 2 (`0:30 – 0:54 – 1:10`, 40s): Application #1 — `RepoNecromancer` (`apps/repo-necromancer`)

- **On-Screen Action (Auto-Synced)**:
  - **`0:30` (`+0s`)**: Runs **`RN-PRESET-01`** (`discount_rate=1.5` negative payable total bug), displaying the Hypothesis shrunk witness (`calculate_checkout_total(100.0, 1.5) -> -50.0`) and the AST-verified guard patch.
  - **`0:54` (`+24s`)**: Automatically switches the dropdown to **`RN-PRESET-03`** (CWE-208 timing side-channel) and runs the audit, showing `==` replaced by constant-time `hmac.compare_digest`.
- **Voiceover (English — Verbatim)**:
  > **[0:30–0:54]** First is RepoNecromancer in `apps/repo-necromancer`. Given an AI-generated discount function, a single-prompt review sees valid syntax and misses the bug. Our Kiro Crew compiles formal EARS specs and runs our MCP Hypothesis sandbox, shrinking `discount_rate=1.5` yielding `-50.0`, and synthesizes a verified guard patch.
  >
  > **[0:54–1:10]** Next, switching to `RN-PRESET-03`, it detects a subtle CWE-208 timing side-channel in `==` token verification and automatically replaces it with constant-time `hmac.compare_digest`.
- **配音逐字稿（简体中文）**：
  > **【0:30–0:54】** 首先是 `apps/repo-necromancer` 代码审计台。面对 AI 生成的折扣函数，单次 Prompt 检查只看语法会直接漏报。而我们的 Kiro Crew 会编译 EARS 规约并调用 MCP Hypothesis 沙盒，自动收缩出 `discount_rate=1.5` 导致应付金额为 `-50.0` 的最小反例，并自动合成通过属性测试的安全补丁。
  >
  > **【0:54–1:10】** 接着切换到 `RN-PRESET-03`，系统还能精准揪出 `==` 签名比对中的 CWE-208 时序侧信道漏洞，并自动替换为恒定时间的 `hmac.compare_digest`。

---

## Scene 3 (`1:10 – 1:40 – 1:55`, 45s): Application #2 — `MedEvidence-Checker` (`apps/med-evidence-checker`)

- **On-Screen Action (Auto-Synced)**:
  - **`1:10` (`+0s`)**: Transitions smoothly (zero white flash) into **App #2 (`MedEvidence-Checker`)** in the **Deep Ocean Blue Clinical Monitor Dark Theme**, running **`MED-PRESET-01`** (Stage 4 CKD, `eGFR = 22 mL/min` + Metformin & Ibuprofen), showing extracted physiology cards, two `CRITICAL` KDIGO citations, safe alternatives (`Linagliptin` + `Acetaminophen`), and the mandatory **`Who Benefits, and Who Could Be Harmed` (`Zero-PHI`)** disclosure block.
  - **`1:40` (`+30s`)**: Automatically switches the dropdown to **`MED-PRESET-02`** (First-Trimester Pregnancy) and runs the audit, flagging teratogenic `Lisinopril` and `Warfarin` (`OB-TERAT-001` / `002`) with `Labetalol` and `Enoxaparin` alternatives.
- **Voiceover (English — Verbatim)**:
  > **[1:10–1:40]** With one click, the exact same skeleton powers App #2: MedEvidence-Checker in `apps/med-evidence-checker`. On a synthetic Stage 4 CKD discharge note with `eGFR 22`, ClaimExtractor isolates renal function and orders. CounterexampleHunter queries our Zero-PHI MCP pharmacology database, flagging critical risks for Metformin lactic acidosis and Ibuprofen kidney injury, while EvidenceAuditor recommends safe alternatives and attaches mandatory harm disclosures.
  >
  > **[1:40–1:55]** Switching to `MED-PRESET-02`, it immediately flags first-trimester teratogenic orders—Lisinopril and Warfarin—recommending pregnancy-safe Labetalol and Enoxaparin.
- **配音逐字稿（简体中文）**：
  > **【1:10–1:40】** 一键切换，同一套骨架驱动第二个应用：`apps/med-evidence-checker` 临床核查台。面对一份合成的 CKD 四期、`eGFR 22` 出院小结，ClaimExtractor 自动提取肾功能与医嘱；CounterexampleHunter 查询 Zero-PHI 本地 MCP 药理库，立即拦截二甲双胍乳酸酸中毒与布洛芬肾损伤两大高危禁忌，并推荐安全替代方案，同时强制附加伦理与受损风险披露。
  >
  > **【1:40–1:55】** 切换到 `MED-PRESET-02` 孕早期病例，系统同样即时拦截致畸药物赖诺普利与华法林，并提示改用妊娠安全的拉贝洛尔与低分子肝素。

---

## Scene 4 (`1:55 – 2:25`, 30s): Root `/.kiro` Live Inspector & 7 Kiro Capabilities

- **On-Screen Action (Auto-Synced)**:
  - Switches to **`⚡ /.kiro Live Inspector`** (`view-kiro`), showcasing all 21 tracked configuration & specification files across all 7 Kiro capabilities: Specs (21 compiled EARS clauses across 3 modules), 6 PBT Properties, 3 Agent Hooks, 3 Steering Docs, Kiro Crew custom agents, local MCP server, and the Kiro Power.
- **Voiceover (English — Verbatim)**:
  > Under the hood, our root `/.kiro` directory integrates all seven Kiro capabilities: 21 compiled EARS clauses across 3 spec modules, 6 formal Correctness Properties tested with Hypothesis PBT, Agent Hooks that validate specs and property tests on save, Steering docs enforcing Zero-PHI and strict separation, custom Kiro Crew agents, our local MCP server, and a reusable Kiro Power.
- **配音逐字稿（简体中文）**：
  > 深入底层，仓库根目录 `/.kiro` 完整集成了 Kiro 的七大核心能力：跨 3 个规约模块的 21 条可编译 EARS 条款、经过 Hypothesis 属性测试验证的 6 项正确性属性、保存即触发的自动化 Agent Hooks、强制 Zero-PHI 与架构解耦的 Steering 文档、自定义 Kiro Crew 智能体、本地 MCP 服务以及可复用的 Kiro Power。

---

## Scene 5 (`2:25 – 2:45`, 20s): Quantitative Evaluation Benchmarks (`100% F1`)

- **On-Screen Action (Auto-Synced)**:
  - Switches to **`📊 Evaluation Benchmarks`** (`view-bench`), comparing Single-Prompt Baseline vs. SpecGuard-Crew on `N = 15` code samples (`20.00%` Recall / `33.33%` F1 vs. `100.00%` Recall / `100.00%` F1) and `N = 20` synthetic clinical vignettes (`8.33%` Recall / `15.38%` F1 vs. `100.00%` Recall / `100.00%` F1).
  - At **`2:45` (`165s`)**, the tour holds firmly on Scene 5 and displays **`✅ 演示完成`** (never wrapping back to Scene 1).
- **Voiceover (English — Verbatim)**:
  > Finally, on reproducible benchmarks across 15 code defect samples and 20 synthetic clinical vignettes, the single-prompt baseline achieved only 20% recall on code bugs and 8.3% on clinical risks—whereas SpecGuard-Crew achieved 100% recall, 100% specificity, and 100% F1 across both domains. Thank you!
- **配音逐字稿（简体中文）**：
  > 最后，在 15 组代码缺陷与 20 组合成临床病例的可复现定量评测中，单次 Prompt 基线在代码和临床上的召回率仅分别为 20% 和 8.3%；而 SpecGuard-Crew 在两个领域均实现 100% 召回率、100% 特异度与 100% F1。感谢观看！
