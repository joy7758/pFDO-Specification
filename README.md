# pFDO-Specification: Physical FAIR Digital Objects for the 1.6Tbps Era

## 🌐 愿景：物理层治理的既成事实
在 1.6Tbps (IEEE 802.3dj) 时代，传统的软件定义治理（Software-Defined Governance）正面临物理时延的失效。pFDO-Specification 旨在将 **FAIR 原则** 直接下沉至物理比特流（Physical Layer），构建全球首个具备“物理确定性”的自治数据治理标准。

## 核心技术支柱 (OMAP 架构)

### 1. MBS (Medical Bit-sequence)
定义了 1.6T 线速下的医疗级物理帧结构。通过硬件级的策略匹配，确保高价值医疗数据在传输过程中具备不可篡改的“自治属性”。

### 2. Clinical Epoch Clock (CEC)
为远程全自动手术设计的“临床纪元时钟”。利用物理层隐写技术（IPG/Idle Steganography），实现纳秒级的物理同步，解决 1.6T 环境下 RS-FEC 带来的时延抖动。

### 3. A-pFDO 审计内核
基于 Q-LUT 的硬件级 AI 逻辑审计。当 AI 决策发生逻辑漂移时，系统在物理层触发“安全悬停（Safety Hover）”，确保生命体征的绝对安全。

## ⚖️ 治理与许可
- **协议层 (Governance Plane)**: 遵循开放标准，旨在成为 FDO 国际工作组的物理参考实现。
- **硬件加速层 (Data Plane)**: 保留特定私有 IP 核授权，确保生态的商业可持续性与技术主权。

---
*“碳基领航，硅基锚定。在 1.6T 的荒原上，我们定义规则。”*

## 🔴 红岩 · 园区数字合规共建平台 (RedRock Digital Compliance)

本项目包含一个企业级合规审计平台 (`product_api`)，提供实时敏感数据扫描与园区态势感知能力。

### 🚀 一键启动 (推荐)
```bash
# 自动处理环境与端口，直接启动大屏服务
./scripts/run_park.sh
```

### 🆕 P0 抄送接入（无痛进入）

该能力采用“旁路抄送”方式接入，不侵入现网业务路径，适合离线演示与渐进上线。当前默认扫描目录：

- 主抄送目录：`./product_api/uploads`
- 模拟抄送箱：`./ingest_drop`

演示步骤：

1. 启动服务：`./scripts/run_park.sh`
2. 打开大屏：`http://127.0.0.1:8000/park`
3. 在“数据接入（旁路抄送）”区域点击“写入示例文件并扫描”
4. 在“最近接入文件”中观察新文件与敏感命中结果

说明：该接入方式为非侵入式 P0 方案，后续可无缝升级为 webhook 触发或旁路镜像接入。

### ✅ 发布前必跑清单 (3分钟)

每次代码提交或演示前，请务必执行以下步骤确保质量：

1. **进入仓库根目录**
   ```bash
   cd ~/pFDO-Specification
   ```

2. **执行健康检查 (Health Check)**
   确保所有核心接口返回 200 OK，且无报错。
   ```bash
   ./scripts/healthcheck.sh
   ```

3. **执行冒烟测试 (Smoke Test)**
   模拟冷启动流程，验证从环境激活到服务就绪的全链路。
   ```bash
   ./scripts/smoke.sh
   ```

### 访问入口
| 页面/接口 | 路径 | 说明 |
| :--- | :--- | :--- |
| **产品首页** | `http://127.0.0.1:8000/` | 极简风格门户，包含所有功能入口 |
| **园区大屏** | `http://127.0.0.1:8000/park` | 实时合规态势与风险预警 (Dashboard) |
| **企业检测** | `http://127.0.0.1:8000/demo` | 隐私数据扫描交互式演示 |
| **接口文档** | `http://127.0.0.1:8000/docs-cn` | 自定义中文 API 文档 |

### 📖 叙事模拟引擎 (Narrative Simulation Engine)

v2.0 引入了确定性叙事模拟引擎，用于生成一致的、可解释的趋势数据，支持演示与演练场景。

#### 环境变量控制
可以通过设置环境变量 `DATA_MODE` 和 `SIMULATION_MODE` 来切换不同的叙事剧本。三种模式中文名固定如下：

- `improving` => `持续改善`
- `stable` => `平稳运行`
- `crisis` => `风险上升`

**1. 危机叙事 (Crisis Mode)**
风险急剧上升，告警激增，模拟严重的数据泄露事件。
```bash
DATA_MODE=simulation SIMULATION_MODE=crisis ./scripts/run_park.sh
```

**2. 改善叙事 (Improving Mode)**
风险逐步下降，合规治理初见成效，模拟整改后的恢复期。
```bash
DATA_MODE=simulation SIMULATION_MODE=improving ./scripts/run_park.sh
```

**3. 稳定叙事 (Stable Mode - 默认)**
系统平稳运行，偶发小波动。
```bash
DATA_MODE=simulation SIMULATION_MODE=stable ./scripts/run_park.sh
```

#### 大屏只读切换（不修改环境变量）
可直接访问下列 URL 在前端演示不同叙事宇宙：

```bash
http://127.0.0.1:8000/park?sim=improving
http://127.0.0.1:8000/park?sim=stable
http://127.0.0.1:8000/park?sim=crisis
```

接口 `GET /api/v1/narrative/status` 会返回：

- `effective_mode`：最终生效模式
- `source`：模式来源（`query_param` 或 `env_var`）

#### API 示例
验证叙事引擎状态与输出：

```bash
# 获取当前引擎状态
curl -s http://127.0.0.1:8000/api/v1/narrative/status

# 获取生成的叙事摘要
curl -s http://127.0.0.1:8000/api/v1/narrative/summary

# 获取 30 天确定性趋势数据
curl -s http://127.0.0.1:8000/api/v1/narrative/series
```

### 📊 园区大屏模块说明 (/park)

大屏旨在成为园区管理者“每天离不开的总控台”，集成以下核心模块：

1.  **环境感知**: 实时天气、体感温度、风速、空气质量 (AQI) 及健康建议。
2.  **时间服务**: 公历/农历双显，节气提醒，以及法定节假日倒计时。
3.  **合规总览**: 实时 PII 扫描量、敏感信息命中数、实时告警流 (Alerts Stream)。
4.  **趋势分析**: **30 日**合规指数与风险事件趋势图 (SVG 渲染)，支持叙事标注。
5.  **生态集成**: 展示已接入的子系统（OA/CRM/IoT）与可扩展插件（门禁/能耗/视频）。
6.  **行为驱动引擎**: 包含必须关注事项、用户行为统计、时间压力指数，辅助即时决策。
7.  **领导者视角**: 右上角 Leader Summary 面板，展示效率、团队状态与预算概况。
8.  **叙事控制卡**: 实时显示当前数据模式与叙事剧本状态。
9.  **风险温度计**: 左侧动态 Risk Thermometer（0-100，越高越危险），直观展示实时风险热度。
10. **安全连胜**: 底部展示连续安全天数 (Streak Stats)。

### 🆕 v1.3.0 RedRock Risk Engine (RRM-1.0)

引入全新的 **RedRock Risk Engine (RRM-1.0)** 动态风险评分模型，取代了原有的静态模拟算法。

- **核心算法**: Weighted Decay (WD-26)
- **评分逻辑**: 
  - 基础分：100 分
  - 扣分因子：
    - **Data Volume (15%)**: 基于文件存储存量进行扣分。
    - **PII Hits (35%)**: 基于敏感数据命中量进行动态扣分。
    - **Active Alerts (50%)**: 基于未解决的高风险告警数量进行重度扣分。
- **透明化**: 通过 API `GET /api/v1/risk-model` 可查看当前生效的模型权重与版本元数据。
- **全局生效**: 该引擎版本号 (`RRM-1.0`) 已注入所有核心接口响应中，确保前端展示的一致性。

### 🔌 API 接口列表

系统提供标准的 RESTful API 供前端与第三方系统调用：

- `GET /api/v1/narrative/*`: 叙事引擎相关接口 (NEW)
- `GET /api/v1/risk-model`: 获取当前风险评分模型元数据
- `GET /api/v1/leader-summary`: 领导视角摘要
- `GET /api/v1/risk-thermometer`: 风险温度计数据 (Powered by RRM-1.0)
- `GET /api/v1/streak`: 连续安全天数
- `GET /api/v1/ticker`: 园区信息总线 (Ticker items)
- `GET /api/v1/overview`: 核心合规指标与统计 (含 `engine_version`)
- `GET /api/v1/briefing`: 每日运营简报
- ... (其他原有接口)

### 🛠️ 常见问题 (Troubleshooting)

- **8000 端口占用 (`Address already in use`)**
  - **现象**: 启动时提示端口被占用。
  - **解决**: 运行 `./scripts/run_park.sh` 或 `./scripts/smoke.sh`，脚本会自动清理旧进程。

- **未激活虚拟环境 (`ModuleNotFoundError`)**
  - **现象**: 提示找不到 `fastapi` 或 `uvicorn`。
  - **解决**: 确保已创建虚拟环境 (`python3 -m venv .venv`) 并激活 (`source .venv/bin/activate`)。

- **ImportError (如 `cannot import name 'get_risk_model'`)**
  - **现象**: 修改了代码但未同步导出。
  - **解决**: 检查 `product_api/__init__.py` 或相关模块的导入路径，确保函数名拼写正确。
