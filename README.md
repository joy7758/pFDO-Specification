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

### 访问入口
| 页面/接口 | 路径 | 说明 |
| :--- | :--- | :--- |
| **产品首页** | `http://127.0.0.1:8000/` | 极简风格门户，包含所有功能入口 |
| **园区大屏** | `http://127.0.0.1:8000/park` | 实时合规态势与风险预警 (Dashboard) |
| **企业检测** | `http://127.0.0.1:8000/demo` | 隐私数据扫描交互式演示 |
| **接口文档** | `http://127.0.0.1:8000/docs-cn` | 自定义中文 API 文档 |

### 📊 园区大屏模块说明 (/park)

大屏旨在成为园区管理者“每天离不开的总控台”，集成以下核心模块：

1.  **环境感知**: 实时天气、体感温度、风速、空气质量 (AQI) 及健康建议。
2.  **时间服务**: 公历/农历双显，节气提醒，以及法定节假日倒计时。
3.  **合规总览**: 实时 PII 扫描量、敏感信息命中数、实时告警流 (Alerts Stream)。
4.  **趋势分析**: 7 日数据合规指数与风险事件趋势图 (SVG 渲染)。
5.  **生态集成**: 展示已接入的子系统（OA/CRM/IoT）与可扩展插件（门禁/能耗/视频）。

### 🔌 API 接口列表

系统提供标准的 RESTful API 供前端与第三方系统调用：

- `GET /api/v1/overview`: 核心合规指标与统计
- `GET /api/v1/weather`: 天气实况与预报 (模拟)
- `GET /api/v1/air`: 空气质量数据 (模拟)
- `GET /api/v1/calendar`: 农历、节气与假期、黄历宜忌与冲煞
  - 返回示例：`{"almanac": {"yi": ["理发",...], "chong": "冲马"}, "display_line": "宜 理发..."}`
- `GET /api/v1/briefing`: 每日运营简报
  - 返回示例：
    ```json
    {
      "title": "每日运营简报",
      "date": "2026年02月18日",
      "summary": "今日合规评分 92，累计扫描 1,284 次...",
      "suggestion": "✅ 园区数据安全状况良好...",
      "status_level": "low",
      "kpis": [{"label": "合规评分", "value": 92, "unit": "分", "color": "green"}],
      "links": [{"text": "查看趋势", "url": "/park#trends"}]
    }
    ```
- `GET /api/v1/ticker`: 顶部公告栏 (Ticker) 数据
  - 返回示例：
    ```json
    {
      "items": [
        {
          "type": "briefing",
          "priority": 95,
          "title": "园区日报",
          "summary": "今日战报：合规评分 92｜扫描 1,284｜敏感命中 23｜实时告警 2｜AQI 良｜体感 -1℃",
          "link": "/park",
          "source": "运营指挥部"
        },
        {
          "type": "alert",
          "level": "RED",
          "title": "紧急告警",
          "summary": "财务系统 发现 未脱敏手机号，请立即处置！"
        },
        {
          "type": "system",
          "level": "INFO",
          "title": "系统状态",
          "summary": "OA办公系统 当前状态：ONLINE (更新于 1分钟前)"
        }
      ]
    }
    ```
- `GET /api/v1/trends`: 7日风险趋势数据
- `GET /api/v1/alerts`: 实时风险告警流
- `GET /api/v1/integrations`: 系统接入状态与插件列表
- `POST /scan/pii`: 敏感数据检测接口

### 🛠️ 常见问题 (Troubleshooting)

**Q: 遇到 Connection Refused 或端口冲突怎么办？**

如果你发现服务无法启动，或提示 `Address already in use`，请按以下步骤操作：

1. **检查端口占用**：查看是否有残留进程占用 8000 端口。
   ```bash
   lsof -i :8000
   ```

2. **强制清理**：杀掉占用进程。
   ```bash
   kill -9 <PID>
   # 或者直接运行我们的清理脚本，它会自动处理
   ./scripts/run_park.sh
   ```

3. **重新启动**：再次运行启动脚本。
   ```bash
   ./scripts/run_park.sh
   ```

**Q: 为什么必须用 run_park.sh？**
我们建议所有运行操作统一通过 `./scripts/run_park.sh` 入口。该脚本集成了环境激活、端口自动释放、日志监控等逻辑，能保证服务“永不掉线”且易于调试。

### 手动启动 (不推荐)
```bash
python -m uvicorn product_api.app:app --reload --host 127.0.0.1 --port 8000
```
