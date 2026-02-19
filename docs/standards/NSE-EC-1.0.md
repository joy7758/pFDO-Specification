# NSE-EC-1.0 标准草案（最小可提交版）

## 1. 标准定位
**NSE-EC-1.0（Narrative Simulation Entropy Control）**定义“数字代谢熵控制”的最小工程标准，用于形成合规治理证据链。  
本标准聚焦三类能力：可计算（指标可量化）、可解释（口径一致）、可复现（脚本可重放）。

## 2. 核心概念与术语
- **H(t)**：数字熵总量，范围归一化为 0-100，值越高表示系统越无序。
- **operators**：代谢算子，包含 Ingest / Verify / Bind / Decay。
- **compliance_score（越高越好）**：合规水平指标，越高表示规则执行质量越高。
- **risk_score（越高越危险）**：风险暴露指标，越高表示事故概率或影响更高。
- **evidence path**：证据路径，指“API 输出 + 实验脚本 + 图表结果 + 文档解释”的闭环链路。

## 3. 数据协议（JSON Schema 级描述）

### 3.1 `GET /api/v1/entropy/status`
- `schema_version`: string，标准版本，示例 `NSE-EC-1.0`
- `generated_at`: string，生成时间（本地时区字符串）
- `inputs`: object，输入上下文（模式、参数、权重）
- `metrics`: object，核心指标（today_entropy、avg_7d、drivers）
- `interpretation`: object，解释层（summary、why、leader_line）

推荐扩展字段（兼容已有实现）：
- `effective_mode`, `metabolism_mode`, `today_entropy`, `avg_7d`, `drivers`

### 3.2 `GET /api/v1/entropy/series`
- `schema_version`: string
- `generated_at`: string
- `inputs`: object（days、metabolism_mode）
- `metrics`: object（series_length、entropy_total_avg、max/min）
- `interpretation`: object（summary、why）

序列字段：
- `dates[]`, `entropy_total[]`, `entropy_state[]`, `entropy_drift[]`, `entropy_access[]`, `metabolism_actions[]`

### 3.3 `GET /api/v1/entropy/report`
- `schema_version`: string
- `generated_at`: string
- `inputs`: object（模式、阈值）
- `metrics`: object（current_entropy、sub_entropy）
- `interpretation`: object（leader_line、engineer_line、suggestions）

报告字段：
- `title`, `status`, `analysis`, `suggestions`

## 4. 评审可复现流程
执行命令：
```bash
bash scripts/run_entropy_experiment.sh
```
预期输出：
- `docs/paper/outputs/entropy_experiment_{mode}_{metabolism}.json`（本地可再生产物）
- `docs/paper/figures/entropy_evolution.png`
- `docs/paper/figures/compliance_vs_entropy.png`
- `docs/paper/figures/metabolism_activity.png`（可选代表图）

## 5. 合规解释口径
- **给领导的一句话**：系统熵 H(t) 持续下降，表示治理动作有效、系统趋于有序，合规可控性提升。  
- **给工程师的量化解释**：当 `H(t)=ws*H_state+wd*H_drift+wa*H_access` 连续上行，且 `risk_score` 同步升高、`compliance_score` 下行时，应提高 Verify/Bind/Decay 强度并复核输入质量。

## 6. 兼容与扩展（Hooks）
- **真实数据源 Hook**：允许将模拟输入替换为园区真实日志、审计流、告警流。
- **第三方插件 Hook**：支持外部规则引擎或风控插件写入 `inputs/metrics`。
- **既有系统接入 Hook**：支持 OA/CRM/IoT 系统通过统一字段映射接入证据链。
- **版本兼容 Hook**：新增字段应遵循“向后兼容”，保留 `schema_version/generated_at/inputs/metrics/interpretation` 五元骨架。

---

# NSE-EC-1.0 Draft Standard (Minimal Submission Version)

## 1. Positioning
**NSE-EC-1.0 (Narrative Simulation Entropy Control)** defines a minimum engineering standard for Digital Metabolism Entropy Control, focused on compliance governance evidence paths.  
The standard targets three capabilities: computable metrics, consistent interpretation, and reproducible experiments.

## 2. Core Concepts and Terms
- **H(t)**: total digital entropy normalized to 0-100; higher means more disorder.
- **operators**: metabolism operators, including Ingest / Verify / Bind / Decay.
- **compliance_score (higher is better)**: governance quality indicator.
- **risk_score (higher is more dangerous)**: risk exposure indicator.
- **evidence path**: closed loop of API outputs, scripts, figures, and textual interpretation.

## 3. Data Protocol (Schema-level Description)

### 3.1 `GET /api/v1/entropy/status`
Required fields:
- `schema_version` (string)
- `generated_at` (string)
- `inputs` (object)
- `metrics` (object)
- `interpretation` (object)

### 3.2 `GET /api/v1/entropy/series`
Required fields:
- `schema_version` (string)
- `generated_at` (string)
- `inputs` (object)
- `metrics` (object)
- `interpretation` (object)

Series payload:
- `dates[]`, `entropy_total[]`, `entropy_state[]`, `entropy_drift[]`, `entropy_access[]`, `metabolism_actions[]`

### 3.3 `GET /api/v1/entropy/report`
Required fields:
- `schema_version` (string)
- `generated_at` (string)
- `inputs` (object)
- `metrics` (object)
- `interpretation` (object)

## 4. Reproducible Review Procedure
Run:
```bash
bash scripts/run_entropy_experiment.sh
```
Expected outputs:
- JSON experiment outputs in `docs/paper/outputs/`
- representative figures in `docs/paper/figures/`

## 5. Compliance Interpretation
- **Executive one-liner**: decreasing H(t) indicates effective governance and improved controllability.
- **Engineering quantitative line**: if H(t) trends upward while `risk_score` rises and `compliance_score` drops, increase Verify/Bind/Decay intensity and review ingest quality.

## 6. Compatibility and Extension
- Hooks for real data sources, third-party plugins, and legacy park systems.
- Forward evolution must keep the five-field backbone:
`schema_version`, `generated_at`, `inputs`, `metrics`, `interpretation`.
