# pFDO-Specification: Physical FAIR Digital Objects for the 1.6Tbps Era
# pFDO-Specification: 1.6Tbps 时代的物理层 FAIR 数字对象

## Bilingual Governance Notice

## Standard Domain Entry / 标准域入口

- Standard ID / 标准编号：`RR-pFDO`
- Registry Row / 注册表定位：https://github.com/joy7758/RedRock-Constitution/blob/main/docs/registry/STANDARDS_REGISTRY.md#rr-pfdo
- Hub / 总入口：https://github.com/joy7758/RedRock-Constitution
- Onepager / 一页纸：`docs/onepager/RR-pFDO_ONEPAGER_CN_EN.md`

中文说明：所有标准以中文与英文双语发布，英文必须为完整翻译版本。  
English: All standards are published in Chinese and English, and the English content must be a full translation.

## 🌐 Vision: Fait Accompli of Physical Layer Governance
## 愿景：物理层治理的既成事实

In the 1.6Tbps (IEEE 802.3dj) era, traditional Software-Defined Governance is facing the failure of physical latency. pFDO-Specification aims to sink the **FAIR Principles** directly to the physical bitstream (Physical Layer), building the world's first autonomous data governance standard with "Physical Determinism".

在 1.6Tbps (IEEE 802.3dj) 时代，传统的软件定义治理（Software-Defined Governance）正面临物理时延的失效。pFDO-Specification 旨在将 **FAIR 原则** 直接下沉至物理比特流（Physical Layer），构建全球首个具备“物理确定性”的自治数据治理标准。

## Core Technology Pillars (OMAP Architecture) / 核心技术支柱 (OMAP 架构)

### 1. MBS (Medical Bit-sequence)
Defines a medical-grade physical frame structure at 1.6T line speed. Through hardware-level policy matching, it ensures that high-value medical data possesses tamper-proof "Autonomous Attributes" during transmission.
定义了 1.6T 线速下的医疗级物理帧结构。通过硬件级的策略匹配，确保高价值医疗数据在传输过程中具备不可篡改的“自治属性”。

### 2. Clinical Epoch Clock (CEC)
A "Clinical Epoch Clock" designed for remote fully automated surgery. utilizing physical layer steganography (IPG/Idle Steganography) to achieve nanosecond-level physical synchronization, solving the latency jitter caused by RS-FEC in 1.6T environments.
为远程全自动手术设计的“临床纪元时钟”。利用物理层隐写技术（IPG/Idle Steganography），实现纳秒级的物理同步，解决 1.6T 环境下 RS-FEC 带来的时延抖动。

### 3. A-pFDO Audit Kernel / A-pFDO 审计内核
Hardware-level AI logic audit based on Q-LUT. When AI decision-making drifts logically, the system triggers a "Safety Hover" at the physical layer to ensure the absolute safety of vital signs.
基于 Q-LUT 的硬件级 AI 逻辑审计。当 AI 决策发生逻辑漂移时，系统在物理层触发“安全悬停（Safety Hover）”，确保生命体征的绝对安全。

## ⚖️ Governance & Licensing / 治理与许可

- **Governance Plane (Protocol Layer) / 协议层**: Adheres to open standards, aiming to become the physical reference implementation of the FDO International Working Group. / 遵循开放标准，旨在成为 FDO 国际工作组的物理参考实现。
- **Data Plane (Hardware Acceleration Layer) / 硬件加速层**: Retains specific private IP core authorizations to ensure commercial sustainability and technical sovereignty of the ecosystem. / 保留特定私有 IP 核授权，确保生态的商业可持续性与技术主权。

> *"Carbon-based piloting, Silicon-based anchoring. In the wasteland of 1.6T, we define the rules."*
> *“碳基领航，硅基锚定。在 1.6T 的荒原上，我们定义规则。”*

---

## 🔴 RedRock Digital Compliance / 红岩 · 园区数字合规共建平台

This project includes an enterprise-level compliance audit platform (`product_api`), providing real-time sensitive data scanning and park situational awareness capabilities.
本项目包含一个企业级合规审计平台 (`product_api`)，提供实时敏感数据扫描与园区态势感知能力。

### 🚀 One-Click Start (Recommended) / 一键启动 (推荐)

```bash
# Automatically handle environment and ports, directly start the dashboard service
# 自动处理环境与端口，直接启动大屏服务
./scripts/run_park.sh
```

### ✅ Pre-release Checklist (3 Minutes) / 发布前必跑清单 (3分钟)

Before every code submission or demo, please ensure to execute the following steps for quality assurance:
每次代码提交或演示前，请务必执行以下步骤确保质量：

1. **Enter Repository Root / 进入仓库根目录**
   ```bash
   cd ~/pFDO-Specification
   ```

2. **Execute Health Check / 执行健康检查**
   Ensure all core interfaces return 200 OK without errors. / 确保所有核心接口返回 200 OK，且无报错。
   ```bash
   ./scripts/healthcheck.sh
   ```

3. **Execute Smoke Test / 执行冒烟测试**
   Simulate the cold start process to verify the full link from environment activation to service readiness. / 模拟冷启动流程，验证从环境激活到服务就绪的全链路。
   ```bash
   ./scripts/smoke.sh
   ```

### Access Points / 访问入口

| Page/Interface | Path | Description |
| :--- | :--- | :--- |
| **Product Home / 产品首页** | `http://127.0.0.1:8000/` | Minimalist portal containing all function entries / 极简风格门户，包含所有功能入口 |
| **Park Dashboard / 园区大屏** | `http://127.0.0.1:8000/park` | Real-time compliance situation and risk warning / 实时合规态势与风险预警 |
| **Enterprise Detection / 企业检测** | `http://127.0.0.1:8000/demo` | Interactive demo for privacy data scanning / 隐私数据扫描交互式演示 |
| **API Docs / 接口文档** | `http://127.0.0.1:8000/docs-cn` | Custom Chinese API documentation / 自定义中文 API 文档 |

### 📖 Narrative Simulation Engine / 叙事模拟引擎

v2.0 introduces a deterministic narrative simulation engine to generate consistent, interpretable trend data, supporting demo and drill scenarios.
v2.0 引入了确定性叙事模拟引擎，用于生成一致的、可解释的趋势数据，支持演示与演练场景。

#### Environment Variable Control / 环境变量控制

You can switch between different narrative scripts by setting `DATA_MODE` and `SIMULATION_MODE` environment variables.
可以通过设置环境变量 `DATA_MODE` 和 `SIMULATION_MODE` 来切换不同的叙事剧本。

- `improving` => `Continuous Improvement / 持续改善`
- `stable` => `Stable Operation / 平稳运行`
- `crisis` => `Risk Rising / 风险上升`

**Example: Crisis Mode / 危机叙事**
```bash
DATA_MODE=simulation SIMULATION_MODE=crisis ./scripts/run_park.sh
```

#### Dashboard Read-Only Switch / 大屏只读切换
Directly access URLs to demonstrate different narrative universes:
可直接访问下列 URL 在前端演示不同叙事宇宙：

```
http://127.0.0.1:8000/park?sim=improving
http://127.0.0.1:8000/park?sim=stable
http://127.0.0.1:8000/park?sim=crisis
```

### 🧠 Digital Metabolism Entropy Control / 数字代谢熵控制

Based on Shannon Entropy and compliance volatility, we quantify system disorder as **Metabolism Entropy $H(t)$**.
基于香农熵与合规波动率，我们将系统无序度量化为 **代谢熵 $H(t)$**。

#### How to Run Experiment / 如何运行实验

Reproduce the entropy evolution under different narrative modes and generate analysis charts:
复现不同叙事模式下的熵值演变，并生成分析图表：

```bash
# Run experiment and generate figures in docs/paper/figures
# 运行实验并在 docs/paper/figures 生成图表
./scripts/run_entropy_experiment.sh
```

#### View in Dashboard / 在大屏查看

The **System Entropy & Metabolism Health** card has been added to the Park Dashboard.
**系统熵与代谢健康度** 卡片已新增至园区大屏。

- **Status Entropy / 状态熵**: Alert distribution disorder.
- **Drift Entropy / 漂移熵**: Compliance baseline volatility.
- **Access Entropy / 访问熵**: Risk exposure degree.

### 📊 Park Dashboard Modules / 园区大屏模块说明 (/park)

The dashboard is designed to be the "Master Console" for park managers, integrating the following core modules:
大屏旨在成为园区管理者“每天离不开的总控台”，集成以下核心模块：

1.  **Environment Awareness / 环境感知**: Real-time weather, apparent temperature, wind speed, AQI, and health advice.
2.  **Time Service / 时间服务**: Gregorian/Lunar calendar dual display, solar term reminders, and holiday countdowns.
3.  **Compliance Overview / 合规总览**: Real-time PII scan volume, sensitive info hits, and Alerts Stream.
4.  **Trend Analysis / 趋势分析**: **30-day** compliance index and risk event trend chart (SVG rendered).
5.  **Ecosystem Integration / 生态集成**: Display connected subsystems (OA/CRM/IoT) and scalable plugins.
6.  **Behavior Engine / 行为驱动引擎**: Includes must-dos, user behavior stats, time pressure index for immediate decision making.
7.  **Leader's View / 领导者视角**: Leader Summary panel showing efficiency, team status, and budget overview.
8.  **Narrative Card / 叙事控制卡**: Real-time display of current data mode and narrative script status.
9.  **Risk Thermometer / 风险温度计**: Dynamic Risk Thermometer (0-100), visually displaying real-time risk heat.
10. **Safety Streak / 安全连胜**: Display consecutive safe days at the bottom.
11. **Entropy Control / 熵控制**: **[NEW]** Real-time monitoring of $H(t)$ and 4 metabolism operators.

### 🆕 v1.3.0 RedRock Risk Engine (RRM-1.0)

Introduces the new **RedRock Risk Engine (RRM-1.0)** dynamic risk scoring model, replacing the original static simulation algorithm.
引入全新的 **RedRock Risk Engine (RRM-1.0)** 动态风险评分模型，取代了原有的静态模拟算法。

- **Core Algorithm / 核心算法**: Weighted Decay (WD-26)
- **Scoring Logic / 评分逻辑**:
  - Base Score: 100 / 基础分：100 分
  - Deduction Factors / 扣分因子:
    - **Data Volume (15%)**: Deducted based on file storage volume. / 基于文件存储存量进行扣分。
    - **PII Hits (35%)**: Dynamically deducted based on sensitive data hits. / 基于敏感数据命中量进行动态扣分。
    - **Active Alerts (50%)**: Heavily deducted based on unresolved high-risk alerts. / 基于未解决的高风险告警数量进行重度扣分。
- **Transparency / 透明化**: View current model weights and version metadata via API `GET /api/v1/risk-model`.
- **Global Effect / 全局生效**: Engine version (`RRM-1.0`) is injected into all core interface responses.

### 🔌 API List / API 接口列表

The system provides standard RESTful APIs for frontend and third-party system calls:
系统提供标准的 RESTful API 供前端与第三方系统调用：

- `GET /api/v1/entropy/*`: Entropy control related APIs (NEW) / 熵控制相关接口
- `GET /api/v1/narrative/*`: Narrative engine related APIs (NEW) / 叙事引擎相关接口
- `GET /api/v1/risk-model`: Get current risk scoring model metadata / 获取当前风险评分模型元数据
- `GET /api/v1/leader-summary`: Leader view summary / 领导视角摘要
- `GET /api/v1/risk-thermometer`: Risk thermometer data (Powered by RRM-1.0) / 风险温度计数据
- `GET /api/v1/streak`: Consecutive safe days / 连续安全天数
- `GET /api/v1/ticker`: Park info bus (Ticker items) / 园区信息总线
- `GET /api/v1/overview`: Core compliance metrics and stats (includes `engine_version`) / 核心合规指标与统计
- `GET /api/v1/briefing`: Daily operation briefing / 每日运营简报

### 🛠️ Troubleshooting / 常见问题

- **Port 8000 Occupied (`Address already in use`)**
  - **Phenomenon**: Port occupied prompt during startup.
  - **Solution**: Run `./scripts/run_park.sh` or `./scripts/smoke.sh`, the script will automatically clean up old processes.

- **Virtual Environment Not Activated (`ModuleNotFoundError`)**
  - **Phenomenon**: `fastapi` or `uvicorn` not found.
  - **Solution**: Ensure virtual environment is created (`python3 -m venv .venv`) and activated (`source .venv/bin/activate`).

- **ImportError (e.g., `cannot import name 'get_risk_model'`)**
  - **Phenomenon**: Code modified but not exported.
  - **Solution**: Check import paths in `product_api/__init__.py` or related modules, ensure function names are spelled correctly.

---

## Belongs to RedRock Constitution / 隶属于红岩宪章体系

This repository is part of the RedRock Constitution architecture framework.

Please start from the central governance hub:

https://github.com/joy7758/RedRock-Constitution

本仓库属于红岩宪章体系，请从总入口开始阅读与理解：

https://github.com/joy7758/RedRock-Constitution

---

## Standard Domain / 标准域

This repository implements Standard Domain `RR-pFDO` under the RedRock Constitution framework.

本仓库实现红岩宪章标准域：`RR-pFDO`

Central Governance Hub:
https://github.com/joy7758/RedRock-Constitution

## Onepager / 一页纸

- `RR-pFDO` Onepager / 一页纸：`docs/onepager/RR-pFDO_ONEPAGER_CN_EN.md`
- Hub / 总入口：https://github.com/joy7758/RedRock-Constitution
