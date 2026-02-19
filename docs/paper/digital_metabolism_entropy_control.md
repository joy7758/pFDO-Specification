# 数字代谢熵控制 (Digital Metabolism Entropy Control)

## 1. 概述

本研究提出了一种基于“数字代谢”的系统熵控制方法，旨在解决长期运行的信息系统因数据累积和规则腐化导致的无序度增长问题。通过引入“代谢熵 $H(t)$”作为核心度量，并定义 Ingest/Verify/Bind/Decay 四大算子，实现系统自适应的健康度维持。

## 2. 熵定义与度量体系

我们将系统总熵定义为三个子熵的加权和：

$$H(t) = w_s H_{state} + w_d H_{drift} + w_a H_{access}$$

其中权重设定为 $w_s=0.4, w_d=0.3, w_a=0.3$。

### 2.1 状态熵 ($H_{state}$)
基于告警分类分布的 Shannon Entropy。反映了系统异常状态的离散程度。
- 计算：对各类 Alert 的分布 $P(x)$ 计算 $-\sum P(x) \log_2 P(x)$。
- 归一化：映射至 0-100 区间。

### 2.2 漂移熵 ($H_{drift}$)
基于合规分数 (Compliance Score) 的日差分波动率及异常跳变计数。反映了系统合规基线的稳定性。
- 计算：$Volatility = \text{avg}(|\Delta Score|) + 5 \times \text{Jumps}$。

### 2.3 访问熵 ($H_{access}$)
基于敏感数据命中 (PII Hits)、未审计文件数及高风险告警数的加权风险暴露度。
- 计算：$Raw = 1.0 \times \text{PII} + 0.5 \times \text{Unaudited} + 2.0 \times \text{HighRisk}$。

## 3. 代谢算子

系统引入四个代谢算子来对抗熵增：

1.  **Ingest (摄入)**：规范化数据摄入管道，标记来源与初始元数据。
2.  **Verify (校验)**：执行 Schema 校验与内容 Hash (SHA256)，过滤劣质数据。
3.  **Bind (绑定)**：为数据对象绑定 Policy Tag (如 Internal/Public) 及 TTL。
4.  **Decay (衰减)**：基于 TTL 自动识别并标记“腐烂”数据，使其不可访问或归档。

## 4. 实验设计与复现

### 4.1 实验场景
我们模拟了三种典型的系统演进叙事模式，每种模式下分别对比开启/关闭代谢机制的效果：
1.  **Improving (持续改善)**：合规性逐步提升，告警减少。
2.  **Stable (平稳运行)**：各项指标在基线附近微小波动。
3.  **Crisis (风险上升)**：合规性恶化，告警激增，面临熵增危机。

### 4.2 复现步骤

执行以下命令即可一键运行实验并生成图表：

```bash
./scripts/run_entropy_experiment.sh
```

### 4.3 实验输出
- **数据文件**：`docs/paper/outputs/entropy_experiment_*.json`
- **图表文件**：
    - `docs/paper/figures/entropy_evolution.png`: H(t) 30天演变对比
    - `docs/paper/figures/metabolism_activity.png`: 代谢算子活跃度
    - `docs/paper/figures/compliance_vs_entropy.png`: 合规分与熵值的关系

## 5. API 接口

系统新增了一组 API 用于实时监控熵值：

- `GET /api/v1/entropy/status`: 获取当前熵值状态及代谢模式。
- `GET /api/v1/entropy/series`: 获取 30 天熵值趋势序列。
- `GET /api/v1/entropy/report`: 获取自然语言分析报告。

所有 API 均支持中文返回，便于大屏展示。

## 6. 结论

实验表明，开启数字代谢机制 (Metabolism ON) 能显著抑制 $H(t)$ 的增长，特别是在 Crisis 模式下，能有效防止系统进入混沌状态，维持合规基线的稳定性。

---

# Digital Metabolism Entropy Control

## 1. Overview

This study proposes a digital-metabolism-based entropy control method to address disorder growth in long-running information systems caused by data accumulation and rule erosion. By introducing metabolism entropy $H(t)$ as the core metric and defining four operators (Ingest/Verify/Bind/Decay), the system can maintain adaptive health over time.

## 2. Entropy Definition and Measurement Framework

We define total system entropy as the weighted sum of three sub-entropies:

$$H(t) = w_s H_{state} + w_d H_{drift} + w_a H_{access}$$

with weights set to $w_s=0.4, w_d=0.3, w_a=0.3$.

### 2.1 State Entropy ($H_{state}$)
Based on Shannon entropy of alert category distribution, reflecting the dispersion of abnormal system states.
- Computation: calculate $-\sum P(x) \log_2 P(x)$ from alert distribution $P(x)$.
- Normalization: map to the 0-100 interval.

### 2.2 Drift Entropy ($H_{drift}$)
Based on day-to-day differential volatility of Compliance Score and abnormal jump counts, reflecting compliance baseline stability.
- Computation: $Volatility = \text{avg}(|\Delta Score|) + 5 \times \text{Jumps}$.

### 2.3 Access Entropy ($H_{access}$)
Based on weighted risk exposure of sensitive-data hits (PII Hits), unaudited file counts, and high-risk alert counts.
- Computation: $Raw = 1.0 \times \text{PII} + 0.5 \times \text{Unaudited} + 2.0 \times \text{HighRisk}$.

## 3. Metabolism Operators

The system introduces four metabolism operators to resist entropy growth:

1. **Ingest**: normalize data ingestion pipelines and mark source and initial metadata.
2. **Verify**: execute schema validation and content hash verification (SHA256) to filter low-quality data.
3. **Bind**: bind policy tags (e.g., Internal/Public) and TTL to data objects.
4. **Decay**: automatically identify and mark rotten data by TTL, then block access or archive it.

## 4. Experiment Design and Reproduction

### 4.1 Experiment Scenarios
We simulate three typical system evolution narratives and compare metabolism ON/OFF behavior for each:
1. **Improving**: compliance gradually improves and alerts decrease.
2. **Stable**: all indicators fluctuate slightly around baseline.
3. **Crisis**: compliance deteriorates and alerts surge, approaching entropy escalation.

### 4.2 Reproduction Steps

Run the following command to execute the experiment and generate figures:

```bash
./scripts/run_entropy_experiment.sh
```

### 4.3 Experiment Outputs
- **Data files**: `docs/paper/outputs/entropy_experiment_*.json`
- **Figure files**:
    - `docs/paper/figures/entropy_evolution.png`: 30-day H(t) evolution comparison
    - `docs/paper/figures/metabolism_activity.png`: metabolism operator activity
    - `docs/paper/figures/compliance_vs_entropy.png`: compliance vs entropy relationship

## 5. API Interfaces

The system adds a set of APIs for real-time entropy monitoring:

- `GET /api/v1/entropy/status`: current entropy state and metabolism mode.
- `GET /api/v1/entropy/series`: 30-day entropy trend series.
- `GET /api/v1/entropy/report`: natural-language analysis report.

All APIs support Chinese outputs for dashboard presentation.

## 6. Conclusion

Experimental results show that enabling digital metabolism (Metabolism ON) significantly suppresses H(t) growth. This is especially evident in Crisis mode, where the mechanism prevents system transition into chaotic conditions and stabilizes the compliance baseline.
