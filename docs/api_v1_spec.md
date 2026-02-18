# API v1 规范草案 (RRM-1.1)

> 版本：v1.1  
> 更新日期：2026-02-18  
> 状态：Draft

本文档定义了红岩园区数字合规平台 (RedRock Digital Compliance) 的核心 API 规范，特别是 RRM (RedRock Risk Engine) 相关的风险解释能力。

## 1. 基础约定

- **URL 前缀**: `/api/v1`
- **字符编码**: UTF-8
- **时间格式**: ISO 8601 (e.g. `2026-02-18T14:30:00`)
- **响应格式**: JSON

### 1.1 错误响应
所有错误返回统一结构：
```json
{
  "detail": "中文错误描述"
}
```

## 2. 风险引擎接口 (Risk Engine)

### 2.1 获取风险解释报告
`GET /api/v1/risk/explain`

返回基于 RRM-1.1 引擎的风险拆解与归因分析。

**响应示例**:
```json
{
  "engine_version": "RRM-1.1",
  "generated_at": "2026-02-18T15:00:00",
  "total_score": 85,
  "level": "中",
  "primary_driver": {
    "key": "pii_hit_rate",
    "name": "敏感信息命中",
    "contribution": 15,
    "ratio": 0.45
  },
  "factors": [
    {
      "key": "pii_hit_rate",
      "name": "敏感信息命中",
      "weight": 0.35,
      "raw": 128,
      "score": 60,
      "contribution": 15,
      "hint": "监测到多处敏感数据明文传输"
    },
    {
      "key": "alerts_24h",
      "name": "实时告警强度",
      "weight": 0.25,
      "raw": 3,
      "score": 80,
      "contribution": 8,
      "hint": "存在未处理的高风险告警"
    }
  ],
  "suggestions": [
    {
      "id": "act_scan",
      "title": "启动全园敏感扫描",
      "detail": "检测到高频敏感数据命中，建议立即对全量文件进行深度合规扫描。",
      "priority": "高"
    }
  ],
  "trend": {
    "direction": "稳定",
    "delta_7d": 0
  }
}
```

### 2.2 获取风险模型元数据
`GET /api/v1/risk/model`

返回当前生效的模型配置，用于标准化输出与审计。

**响应示例**:
```json
{
  "engine": "RedRock Risk Engine",
  "version": "RRM-1.1",
  "algorithm": "Weighted Decay (WD-26)",
  "last_updated": "2026-02-18 10:00:00",
  "factors": [
    {
      "name": "Data Volume",
      "weight": "15%",
      "desc": "Based on file storage count"
    },
    {
      "name": "PII Hits",
      "weight": "35%",
      "desc": "Sensitive data patterns found"
    }
  ]
}
```

## 3. 版本策略

- **RRM-1.0**: 基础静态模拟 + 简单扣分 (Deprecated)
- **RRM-1.1**: 动态权重 + 可解释性归因 (Current Stable)
- **RRM-1.2**: 计划加入外部威胁情报 (Threat Intel) 集成

## 4. 概览与叙事协议补充

### 4.1 概览接口口径
`GET /api/v1/overview`

`overview` 同时提供以下两个核心分值，且二者均为 `0-100`：

- `risk_score`: 风险分数，越高表示风险越高（越危险）
- `compliance_score`: 合规指数，越高表示合规状态越好

当前默认映射为：
`compliance_score = clamp(100 - risk_score, 0, 100)`  
（允许在引擎内部使用等价单调映射，但必须保持“合规指数越高越好”的口径不变）

### 4.2 叙事接口协议（NSE-1.0）

以下接口统一采用 `NSE-1.0` 协议扩展字段：

- `GET /api/v1/narrative/summary`
- `GET /api/v1/narrative/status`

响应需包含：

- `schema_version`: 固定为 `"NSE-1.0"`
- `generated_at`: ISO 8601 时间字符串
- `inputs`: 输入上下文对象，包含：
  - `data_mode`
  - `source`
  - `seed`（可选）
  - `sim`（可选）
