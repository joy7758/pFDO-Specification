import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List

from .config import (
    get_simulation_mode, 
    get_demo_seed, 
    get_sim_start_date,
    get_simulation_label
)
from .context import get_simulation_mode_context

def _get_sim_seed() -> int:
    """基于 DATA_MODE 配置生成确定性种子"""
    base_seed = get_demo_seed()
    mode = get_simulation_mode()
    date_str = get_sim_start_date()
    # 混合种子，确保不同模式和日期产生不同结果
    raw = f"{base_seed}-{mode}-{date_str}"
    return int(hashlib.sha256(raw.encode('utf-8')).hexdigest()[:8], 16)

def _generate_value(day_idx: int, mode: str, metric: str, seed: int) -> float:
    """
    根据模式和天数生成数值 (确定性)
    day_idx: 0..29 (0 is 30 days ago, 29 is today)
    mode: improving | stable | crisis
    metric: score | alerts | hits | scans
    """
    random.seed(seed + day_idx * 100 + hash(metric))
    
    # 基础噪音
    noise = random.uniform(-1, 1)
    
    if metric == "score":
        # Score: 0-100 (Higher is Better/Safer)
        if mode == "stable":
            base = 92
            trend = 0
            noise_scale = 2
        elif mode == "improving":
            # 从 60 升到 95
            progress = day_idx / 29.0
            base = 60 + (35 * progress)
            trend = 0
            noise_scale = 3
        elif mode == "crisis":
            # 从 95 降到 45
            progress = day_idx / 29.0
            base = 95 - (50 * (progress ** 2)) # 加速恶化
            trend = 0
            noise_scale = 4
        else:
            base = 85
            trend = 0
            noise_scale = 5
            
        val = base + trend + (noise * noise_scale)
        return max(0, min(100, val))

    elif metric == "alerts":
        # Alerts: Count per day
        if mode == "stable":
            base = 2
            noise_scale = 2
        elif mode == "improving":
            # 15 -> 1
            progress = day_idx / 29.0
            base = 15 * (1 - progress)
            noise_scale = 3
        elif mode == "crisis":
            # 2 -> 30
            progress = day_idx / 29.0
            base = 2 + (28 * (progress ** 2))
            noise_scale = 5
        else:
            base = 5
            noise_scale = 3
            
        val = base + (noise * noise_scale)
        return max(0, int(val))

    elif metric == "hits":
        # Sensitive Data Hits
        if mode == "stable":
            base = 15
            noise_scale = 5
        elif mode == "improving":
            # 100 -> 10
            progress = day_idx / 29.0
            base = 100 * (1 - progress) + 10
            noise_scale = 10
        elif mode == "crisis":
            # 10 -> 200
            progress = day_idx / 29.0
            base = 10 + (190 * progress)
            noise_scale = 20
        else:
            base = 30
            noise_scale = 10
            
        val = base + (noise * noise_scale)
        return max(0, int(val))
        
    elif metric == "scans":
        # Scan Volume (Stable usually)
        base = 200 + (day_idx % 7) * 10 # Weekly pattern
        noise_scale = 30
        val = base + (noise * noise_scale)
        return max(50, int(val))
        
    return 0

def generate_trend_series(days: int = 30) -> Dict[str, List[Any]]:
    """生成 30 天趋势数据"""
    seed = _get_sim_seed()
    mode = get_simulation_mode()
    start_date_str = get_sim_start_date()
    end_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    
    dates = []
    scores = []
    alerts = []
    hits = []
    scans = []
    
    for i in range(days):
        day_idx = i
        current_date = end_date - timedelta(days=(days - 1 - i))
        dates.append(current_date.strftime("%m-%d"))
        
        scores.append(int(_generate_value(day_idx, mode, "score", seed)))
        alerts.append(int(_generate_value(day_idx, mode, "alerts", seed)))
        hits.append(int(_generate_value(day_idx, mode, "hits", seed)))
        scans.append(int(_generate_value(day_idx, mode, "scans", seed)))
        
    return {
        "dates": dates,
        "risk_scores": scores,
        "alerts_count": alerts,
        "pii_hits": hits,
        "scan_volume": scans
    }

def today_snapshot() -> Dict[str, Any]:
    """生成今日快照数据"""
    series = generate_trend_series(30)
    
    # Last day values
    score = series["risk_scores"][-1]
    alerts_today = series["alerts_count"][-1]
    hits_today = series["pii_hits"][-1]
    scans_today = series["scan_volume"][-1]
    
    # Calculate derived metrics
    temp = max(10, min(100, 100 - score + random.randint(-2, 2)))
    
    mode = get_simulation_mode()
    must_focus_count = 0
    top_drivers = []
    
    if mode == "stable":
        must_focus_count = random.randint(0, 1)
        top_drivers = [{"name": "历史文件积压", "contribution": 5}, {"name": "偶发敏感词", "contribution": 2}]
    elif mode == "improving":
        must_focus_count = 0
        top_drivers = [{"name": "残留日志", "contribution": 3}]
    elif mode == "crisis":
        must_focus_count = random.randint(5, 12)
        top_drivers = [
            {"name": "API 批量泄露", "contribution": 45}, 
            {"name": "异常 IP 暴增", "contribution": 30},
            {"name": "未授权访问", "contribution": 15}
        ]
        
    return {
        "risk_score": score,
        "temperature": temp,
        "must_focus_count": must_focus_count,
        "alerts_active": alerts_today,
        "hits_today": hits_today,
        "scans_today": scans_today,
        "top_drivers": top_drivers
    }

def narrative_summary() -> Dict[str, Any]:
    """生成叙事摘要"""
    mode = get_simulation_mode()
    label = get_simulation_label(mode)
    
    # 确定性数据源
    series = generate_trend_series(30)
    score_trend = series["risk_scores"]
    hits_trend = series["pii_hits"]
    alerts_trend = series["alerts_count"]
    
    start_score = score_trend[0]
    end_score = score_trend[-1]
    score_diff = end_score - start_score
    change_rate = (score_diff / start_score * 100.0) if start_score else 0.0

    avg_score = sum(score_trend) / len(score_trend)
    avg_hits = sum(hits_trend) / len(hits_trend)
    end_hits = hits_trend[-1]
    end_alerts = alerts_trend[-1]

    # 拐点检测：寻找斜率符号变化点，输出第一个最显著拐点
    turning_idx = 0
    max_turn_strength = -1
    for idx in range(1, len(score_trend) - 1):
        left = score_trend[idx] - score_trend[idx - 1]
        right = score_trend[idx + 1] - score_trend[idx]
        if left * right < 0:
            strength = abs(left) + abs(right)
            if strength > max_turn_strength:
                max_turn_strength = strength
                turning_idx = idx
    turning_date = series["dates"][turning_idx]
    turning_score = score_trend[turning_idx]
    
    evidence = []
    title = ""
    summary_text = ""
    actions = []
    level = "medium"

    if mode == "improving":
        title = f"合规指数显著提升 {score_diff} 点"
        summary_text = "得益于持续的合规治理行动，园区整体风险指数在过去 30 天内显著改善。敏感数据命中率大幅下降，高风险告警已全部清零。建议继续保持当前的自动化拦截策略，并逐步开展历史数据清洗工作。"
        evidence = [
            f"关键拐点出现在 {turning_date}，合规指数 {turning_score}",
            f"30日合规指数均值 {avg_score:.1f}，当前值 {end_score}",
            f"合规指数变化率 {change_rate:+.1f}%，敏感命中下降 {(1 - end_hits / avg_hits) * 100:.0f}%"
        ]
        actions = [
            {"id": "act_imp_1", "label": "固化当前策略"},
            {"id": "act_imp_2", "label": "归档月度报告"}
        ]
        level = "low"
        
    elif mode == "crisis":
        title = "检测到严重的数据泄露威胁"
        summary_text = "紧急状态：园区正面临严重的数据安全威胁！过去 72 小时内，API 接口遭到持续的异常爬取，敏感数据泄露风险激增。核心数据库检测到多起未授权访问尝试，合规指数已跌至历史低点。"
        evidence = [
            f"关键拐点出现在 {turning_date}，合规指数 {turning_score}",
            f"30日合规指数均值 {avg_score:.1f}，当前值 {end_score}",
            f"合规指数变化率 {change_rate:+.1f}%，实时高风险告警 {end_alerts} 起"
        ]
        actions = [
            {"id": "act_cri_1", "label": "立即熔断保护"},
            {"id": "act_cri_2", "label": "全量封禁异常IP"}
        ]
        level = "critical"
        
    else: # stable
        title = "系统整体运行平稳无异常"
        summary_text = "园区数据合规态势整体平稳，各项指标在预期范围内波动。偶发性敏感词命中主要集中在非结构化文档上传，未发现系统性风险。建议维持常态化监控，并关注即将到来的节假日流量高峰。"
        evidence = [
            f"关键拐点出现在 {turning_date}，合规指数 {turning_score}",
            f"30日合规指数均值 {avg_score:.1f}，当前值 {end_score}",
            f"合规指数变化率 {change_rate:+.1f}%，日均敏感命中 {int(avg_hits)} 条"
        ]
        actions = [
            {"id": "act_sta_1", "label": "执行例行巡检"},
            {"id": "act_sta_2", "label": "优化误报规则"}
        ]
        level = "medium"
        
    return {
        "mode": mode,
        "title": title,
        "summary": summary_text,
        "evidence": evidence,
        "actions": actions,
        "label": label,
        "level": level,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_narrative_status_data() -> Dict[str, Any]:
    ctx_source = "query_param" if get_simulation_mode_context() else "env_var"
    return {
        "effective_mode": get_simulation_mode(),
        "source": ctx_source,
        "start_date": get_sim_start_date(),
        "engine_version": "NSE-2.0"
    }
