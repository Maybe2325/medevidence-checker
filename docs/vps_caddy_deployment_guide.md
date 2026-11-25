# Linux VPS + Caddy 双站点自动 HTTPS 部署与参赛提交核对手册

> **适用范围**：单台个人 Linux VPS（Ubuntu 22.04 / 24.04 或 Debian 12+）同时托管两个独立后端实例：
> - **`specguard-crew`** → 仅监听本机 `127.0.0.1:8001`（默认首页进入 **🎃 App #1: RepoNecromancer**）
> - **`medevidence-checker`** → 仅监听本机 `127.0.0.1:8002`（默认首页进入 **🩺 App #2: MedEvidence-Checker**）
> - **Caddy 反向代理**：分别为两个子域名自动申请/续签 Let's Encrypt HTTPS 证书并代理到 `8001` 与 `8002`。

---

## 1. 架构与前置准备（DNS 与防火墙）

```text
Internet (HTTPS :443 / HTTP :80)
   ├── https://specguard.<your-domain>     ──▶ Caddy ──▶ 127.0.0.1:8001 (specguard-crew)
   └── https://medevidence.<your-domain>   ──▶ Caddy ──▶ 127.0.0.1:8002 (medevidence-checker)
```

1. **配置两条 DNS A 记录**（如使用 Cloudflare，证书验证阶段建议先设为 *DNS only* 灰云，HTTPS 就绪后再按需开启代理）：
   - `specguard.<your-domain>` → `<YOUR_VPS_PUBLIC_IP>`
   - `medevidence.<your-domain>` → `<YOUR_VPS_PUBLIC_IP>`
2. **放行 `80` / `443`（不要对外网开放 `8001` / `8002`）**：
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```
3. **克隆两个公开 GitHub 仓库到 VPS**（例如 `/opt/apps`）：
   ```bash
   sudo mkdir -p /opt/apps && sudo chown -R "$USER:$USER" /opt/apps
   cd /opt/apps
   git clone https://github.com/Maybe2325/specguard-crew.git
   git clone https://github.com/Maybe2325/medevidence-checker.git
   ```

---

## 2. 启动后端服务（二选一：Docker 方案 或 systemd 虚拟环境方案）

### 方案 A：Docker / Docker Compose 部署（推荐）

两个仓库根目录均已包含 [`Dockerfile`](../Dockerfile)（容器内监听 `8000` 端口，零 API 密钥离线即用）。只需将宿主机环回端口分别映射为 `127.0.0.1:8001` 与 `127.0.0.1:8002`：

#### 方式 A1：直接 `docker build` + `docker run`
```bash
# 1. 构建并启动 specguard-crew -> 127.0.0.1:8001
cd /opt/apps/specguard-crew
docker build -t specguard-crew:latest .
docker run -d \
  --name specguard-crew \
  --restart unless-stopped \
  -p 127.0.0.1:8001:8000 \
  specguard-crew:latest

# 2. 构建并启动 medevidence-checker -> 127.0.0.1:8002
cd /opt/apps/medevidence-checker
docker build -t medevidence-checker:latest .
docker run -d \
  --name medevidence-checker \
  --restart unless-stopped \
  -p 127.0.0.1:8002:8000 \
  medevidence-checker:latest
```

#### 方式 A2：使用 `/opt/apps/docker-compose.yml` 统一编排
```yaml
services:
  specguard-crew:
    build: /opt/apps/specguard-crew
    container_name: specguard-crew
    restart: unless-stopped
    ports:
      - "127.0.0.1:8001:8000"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')"]
      interval: 30s
      timeout: 5s
      retries: 3

  medevidence-checker:
    build: /opt/apps/medevidence-checker
    container_name: medevidence-checker
    restart: unless-stopped
    ports:
      - "127.0.0.1:8002:8000"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
```
启动并查看状态：
```bash
cd /opt/apps && docker compose up -d --build
docker compose ps
```

---

### 方案 B：Python `venv` + `systemd` 部署（轻量无 Docker 备选）

如果 VPS 未安装 Docker，可直接使用 Python 3.11+ 虚拟环境与 `systemd` 守护进程：

1. **创建两个仓库各自的虚拟环境并跑通测试**：
   ```bash
   for repo in specguard-crew medevidence-checker; do
     cd /opt/apps/$repo
     python3 -m venv .venv
     .venv/bin/pip install --upgrade pip
     .venv/bin/pip install fastapi uvicorn pydantic hypothesis pytest httpx pyyaml
     .venv/bin/python -m pytest
   done
   ```

2. **创建 `/etc/systemd/system/specguard-crew.service`**（监听 `127.0.0.1:8001`）：
   ```ini
   [Unit]
   Description=SpecGuard-Crew FastAPI Workbench (Port 8001)
   After=network.target

   [Service]
   Type=simple
   User=www-data
   Group=www-data
   WorkingDirectory=/opt/apps/specguard-crew
   ExecStart=/opt/apps/specguard-crew/.venv/bin/uvicorn apps.backend_api.main:app --host 127.0.0.1 --port 8001 --workers 2
   Restart=always
   RestartSec=3

   [Install]
   WantedBy=multi-user.target
   ```

3. **创建 `/etc/systemd/system/medevidence-checker.service`**（监听 `127.0.0.1:8002`）：
   ```ini
   [Unit]
   Description=MedEvidence-Checker FastAPI Workbench (Port 8002)
   After=network.target

   [Service]
   Type=simple
   User=www-data
   Group=www-data
   WorkingDirectory=/opt/apps/medevidence-checker
   ExecStart=/opt/apps/medevidence-checker/.venv/bin/uvicorn apps.backend_api.main:app --host 127.0.0.1 --port 8002 --workers 2
   Restart=always
   RestartSec=3

   [Install]
   WantedBy=multi-user.target
   ```

4. **赋权并启动服务**：
   ```bash
   sudo chown -R www-data:www-data /opt/apps/specguard-crew /opt/apps/medevidence-checker
   sudo systemctl daemon-reload
   sudo systemctl enable --now specguard-crew medevidence-checker
   sudo systemctl status specguard-crew medevidence-checker --no-pager
   ```

### 本机端口连通性验证（两种方案通用）
```bash
curl -fsS http://127.0.0.1:8001/api/health
curl -fsS http://127.0.0.1:8002/api/health
curl -fsS http://127.0.0.1:8001/api/kiro/specs | head -c 200
```

---

## 3. 配置 Caddy 双子域名自动 HTTPS 反向代理

1. **安装 Caddy（Ubuntu / Debian）**：
   ```bash
   sudo apt-get update
   sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
   curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
   sudo apt-get update && sudo apt-get install -y caddy
   ```

2. **编辑 `/etc/caddy/Caddyfile`**（将 `<your-domain>` 替换为你的真实域名）：
   ```caddyfile
   specguard.<your-domain> {
       encode zstd gzip
       header {
           X-Content-Type-Options "nosniff"
           Referrer-Policy "strict-origin-when-cross-origin"
       }
       reverse_proxy 127.0.0.1:8001
   }

   medevidence.<your-domain> {
       encode zstd gzip
       header {
           X-Content-Type-Options "nosniff"
           Referrer-Policy "strict-origin-when-cross-origin"
       }
       reverse_proxy 127.0.0.1:8002
   }
   ```

3. **校验配置并重载 Caddy**：
   ```bash
   sudo caddy validate --config /etc/caddy/Caddyfile
   sudo systemctl enable --now caddy
   sudo systemctl reload caddy
   ```

4. **线上 HTTPS 验证**：
   ```bash
   curl -fsSI https://specguard.<your-domain>
   curl -fsS  https://specguard.<your-domain>/api/health
   curl -fsSI https://medevidence.<your-domain>
   curl -fsS  https://medevidence.<your-domain>/api/health
   ```
   确认：
   - 打开 `https://specguard.<your-domain>` 默认直接进入 **🎃 App #1: RepoNecromancer**；
   - 打开 `https://medevidence.<your-domain>` 默认直接进入 **🩺 App #2: MedEvidence-Checker**（深海蓝临床监护仪暗色主题，无刺眼白屏）；
   - 两个域名点击 **🌐 中文 / EN** 与 **🎬 Auto-Demo Tour** 均正常调用后端 `/api/verify/code` 与 `/api/verify/clinical`。

---

## 4. 录制视频、博客 / 社交宣传与 Devpost 最终提交核对清单

### A. 录制 2分45秒（165秒）演示视频核对清单
- [ ] 在部署好的 `https://specguard.<your-domain>`（或本机）打开工作台，点击 **`🎬 Auto-Demo Tour`**（默认就是 `2:45` 配音同步模式）。
- [ ] 在 `0:00` 按 **`Space`** 暂停，点击 **`📜 提词器 / Script`** 弹出独立深色提词器窗口，拖出录屏采集框外。
- [ ] 仅采集主浏览器窗口，按 **`Space`** 开始录制，按 [`docs/video_script_and_storyboard.md`](video_script_and_storyboard.md) 同步朗读：
  - `0:00–0:30` 第一幕：App #1 + 顶部 `#skeleton-ribbon` 动画高亮边框
  - `0:30–1:10` 第二幕：`0:30` 运行 `RN-PRESET-01` → `0:54` 自动切 `RN-PRESET-03`
  - `1:10–1:55` 第三幕：`1:10` 无闪白切换至深色 App #2 运行 `MED-PRESET-01` → `1:40` 自动切 `MED-PRESET-02`
  - `1:55–2:25` 第四幕：展示 `view-kiro`（21 条 EARS 与 7 大 Kiro 能力）
  - `2:25–2:45` 第五幕：展示 `view-bench`，在 `2:45` 稳稳停在第五幕并显示 **`✅ 演示完成`**
- [ ] 确认视频总时长满足 **Kiroween 2026 (`<= 3:00`)** 与 **AI for Medicine (`>= 1:00`)**，无版权背景音乐，已上传 YouTube / Vimeo 并设为 Public（或 Unlisted 可访问）。

### B. 发布博客与社交媒体加分项核对清单
- [ ] **dev.to 技术博客（Kiroween `Blog Prize`）**：
  - 将 [`docs/devto_blog_post.md`](devto_blog_post.md) 发布到 `https://dev.to`，文中补充线上 Demo URL 与演示视频链接，确认公开可访问后复制文章 URL。
- [ ] **社交媒体帖子（Kiroween `Social Blitz`）**：
  - 在 X / LinkedIn / Bluesky 发布宣传帖，**正文开头必须严格包含 `#KiroweenHackathon26`**（可直接复用 [`docs/devpost_submission_kiroween.md`](devpost_submission_kiroween.md) Field 13 模板并附上视频/博客/线上体验链接），复制帖子直链。

### C. Devpost 最终提交前核对清单

#### 1) Kiroween 2026 提交表单（`SpecGuard-Crew`，[`docs/devpost_submission_kiroween.md`](devpost_submission_kiroween.md)）
- [ ] **Public GitHub URL**：`https://github.com/Maybe2325/specguard-crew`（确认仓库为 `Public`，右上角可见 `MIT License`，根目录存在 `/.kiro/`，且同时包含 `apps/repo-necromancer` 与 `apps/med-evidence-checker` 两个独立目录）。
- [ ] **Hosted Demo URL**：填入 `https://specguard.<your-domain>`。
- [ ] **Demo Video URL**：填入 2:45 演示视频链接。
- [ ] **Main Technology Explanation (Field 7)**：已点名全部 Kiro 能力（`Specs (EARS)`, `PBT`, `Steering`, `Hooks`, `Custom Agents / Kiro Crew`, `MCP`, `Powers`）。
- [ ] **Bonus Prizes 勾选与补全**：
  - `Best Student`：填写真实 `.edu` 学生邮箱、学校英文名、年级学位与 LinkedIn；
  - `Best Kiro Crew App`：确认 GitHub URL 与 3-Agent 描述完整；
  - `Blog Prize`：填入 dev.to 公开文章链接；
  - `Social Blitz`：填入包含 `#KiroweenHackathon26` 的公开社交帖链接。

#### 2) AI for Medicine 2026 提交表单（`MedEvidence-Checker`，[`docs/devpost_submission_ai_medicine.md`](devpost_submission_ai_medicine.md)）
- [ ] **Public GitHub URL**：`https://github.com/Maybe2325/medevidence-checker`（确认仓库为 `Public`，根目录包含 `/.kiro/`，默认视图直接进入临床精准审计台）。
- [ ] **Hosted Demo URL**：填入 `https://medevidence.<your-domain>`。
- [ ] **Demo Video URL**：填入演示视频链接。
- [ ] **6 项强制说明段落完整**：`Problem and User`、`Method and Comparison to a Simple Baseline`、`Evaluation (N=20, 100% Recall & F1 vs 8.33% Baseline)`、`Who Benefits, and Who Could Be Harmed (Zero-PHI + HITL)`、`Limitations and One-Month Roadmap`、`Full Attribution & AI Tools Disclosure`。
- [ ] **本地/VPS 最终回归验证**：两个仓库均通过 `python3 -m pytest`（`13 passed`）与 `python3 benchmarks/run_evaluation.py`。
