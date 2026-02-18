# product_api/risk_explainer.py
# 风险解释引擎 (RRM-1.1)
# 负责拆解风险因子，提供可解释的归因分析与行动建议

import time
import random
from datetime import datetime
from typing import Dict, Any, List

# 复用 dashboard 数据源
from .dashboard import (
    calculate_dynamic_risk_score,
    get_overview_stats,
    get_alerts_data,
    get_integrations_status,
    get_time_pressure
)

ENGINE_VERSION = "RRM-1.1"

def explain_risk() -> Dict[str, Any]:
    """生成风险解释报告"""
    
    # 1. 获取各项指标
    risk_calc = calculate_dynamic_risk_score()
    alerts = get_alerts_data()
    integrations = get_integrations_status()
    pressure = get_time_pressure()
    
    total_score = risk_calc['score']
    factors = risk_calc.get('factors', {})
    
    # 2. 评级判定
    if total_score >= 90:
        level = "低"
    elif total_score >= 70:
        level = "中"
    elif total_score >= 50:
        level = "高"
    else:
        level = "严重"
        
    # 3. 计算贡献因子详情
    # 这里的贡献是指“扣分贡献”，即导致分数降低的原因
    # 基础分 100，当前分 total_score，总扣分 = 100 - total_score
    # 各项 penalty 之和约等于总扣分
    
    # 获取原始扣分值
    p_file = factors.get('file_penalty', 0)
    p_hits = factors.get('hits_penalty', 0)
    p_alert = factors.get('alert_penalty', 0)
    
    # 模拟其他两项 (Integration gap & Time pressure) 
    # 为了演示效果，我们假设模型内部还有这两项隐性扣分，或者将其映射到已有 penalty
    # 这里简单起见，我们重新构造一个归一化的贡献表
    
    # 构造因子列表
    factor_list = []
    
    # 3.1 敏感命中 (PII Hits)
    # 假设 hits_penalty 对应 PII Hits
    factor_list.append({
        "key": "pii_hit_rate",
        "name": "敏感信息命中",
        "weight": 0.35,
        "raw": risk_calc.get('hits_today', 0),
        "score": 100 - (p_hits * 5), # 估算分数
        "contribution": p_hits,
        "hint": "监测到多处敏感数据明文传输"
    })
    
    # 3.2 告警强度 (Alerts)
    factor_list.append({
        "key": "alerts_24h",
        "name": "实时告警强度",
        "weight": 0.25,
        "raw": risk_calc.get('alerts_active', 0),
        "score": 100 - (p_alert * 3),
        "contribution": p_alert,
        "hint": "存在未处理的高风险告警"
    })
    
    # 3.3 数据存量 (Data Volume) -> 映射为“未修复风险”概念的一部分
    factor_list.append({
        "key": "data_volume",
        "name": "数据存量风险",
        "weight": 0.15,
        "raw": risk_calc.get('file_count', 0),
        "score": 100 - (p_file * 6),
        "contribution": p_file,
        "hint": "文件存量过大增加暴露面"
    })
    
    # 3.4 接入缺口 (Integrations) - 模拟计算
    systems_total = len(integrations.get('systems', [])) + len(integrations.get('available_plugins', []))
    systems_active = len(integrations.get('systems', []))
    gap = systems_total - systems_active
    # 假设每个缺口扣 2 分
    p_integ = min(10, gap * 2)
    factor_list.append({
        "key": "integrations_gap",
        "name": "系统接入缺口",
        "weight": 0.10,
        "raw": gap,
        "score": 100 - (p_integ * 10),
        "contribution": p_integ,
        "hint": "部分核心系统尚未接入监管"
    })
    
    # 3.5 时间压力 (Time Pressure)
    p_time = 0
    if pressure.get('level') == 'high':
        p_time = 15
    elif pressure.get('level') == 'medium':
        p_time = 8
    else:
        p_time = 2
    factor_list.append({
        "key": "time_pressure",
        "name": "运维时间压力",
        "weight": 0.15,
        "raw": pressure.get('pending_tasks', 0),
        "score": pressure.get('pressure_score', 80), # 反向，高分好
        "contribution": p_time,
        "hint": "任务积压导致响应迟缓"
    })
    
    # 4. 识别主因 (Primary Driver)
    # 按 contribution 降序
    factor_list.sort(key=lambda x: x['contribution'], reverse=True)
    top_driver = factor_list[0]
    
    # 计算 contribution 占比
    total_penalty = sum(f['contribution'] for f in factor_list)
    if total_penalty == 0: total_penalty = 1 # Avoid div by zero
    
    primary_driver = {
        "key": top_driver['key'],
        "name": top_driver['name'],
        "contribution": top_driver['contribution'],
        "ratio": round(top_driver['contribution'] / total_penalty, 2)
    }
    
    # 5. 生成建议 (Suggestions)
    suggestions = []
    
    # 针对 Top 1
    if top_driver['key'] == 'pii_hit_rate':
        suggestions.append({
            "id": "act_scan",
            "title": "启动全园敏感扫描",
            "detail": "检测到高频敏感数据命中，建议立即对全量文件进行深度合规扫描。",
            "priority": "高"
        })
    elif top_driver['key'] == 'alerts_24h':
        suggestions.append({
            "id": "act_triage",
            "title": "告警清零行动",
            "detail": "实时告警积压较多，建议优先处理 High 级别告警，并调整误报规则。",
            "priority": "高"
        })
    elif top_driver['key'] == 'data_volume':
        suggestions.append({
            "id": "act_clean",
            "title": "过期数据清理",
            "detail": "存储数据量超过阈值，建议归档 3 年以上历史数据。",
            "priority": "中"
        })
    elif top_driver['key'] == 'time_pressure':
        suggestions.append({
            "id": "act_assist",
            "title": "启用自动化辅助",
            "detail": "检测到运维压力过大，建议开启自动阻断策略以减轻人工负担。",
            "priority": "中"
        })
    else:
        suggestions.append({
            "id": "act_review",
            "title": "系统接入复核",
            "detail": "建议尽快接入剩余子系统，消除监控盲区。",
            "priority": "低"
        })
        
    # 通用建议 (凑够2条)
    if len(suggestions) < 2:
        suggestions.append({
            "id": "act_report",
            "title": "生成合规周报",
            "detail": "汇总当前风险态势，向管理层发送整改建议书。",
            "priority": "低"
        })
        
    # 6. 趋势 (Trend)
    # 模拟数据
    trend = {
        "direction": random.choice(["稳定", "上升", "下降"]),
        "delta_7d": random.randint(-5, 5)
    }
    
    return {
        "engine_version": ENGINE_VERSION,
        "generated_at": datetime.now().isoformat(),
        "total_score": total_score,
        "level": level,
        "primary_driver": primary_driver,
        "factors": factor_list,
        "suggestions": suggestions,
        "trend": trend
    }
