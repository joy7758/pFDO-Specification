from fastapi import APIRouter, Query
from typing import Any
from datetime import datetime

from ..dashboard import is_simulation_mode, get_simulation_mode, get_simulation_label
from .metrics import calculate_total_entropy, get_entropy_series
from .operators import get_metabolism_mode, set_metabolism_mode, get_metabolism_stats

router = APIRouter(prefix="/api/v1/entropy", tags=["Entropy"])
SCHEMA_VERSION = "NSE-EC-1.0"

@router.get("/status")
def get_entropy_status(metabolism: str = Query(None, description="Set metabolism mode (on/off)")) -> dict[str, Any]:
    """
    获取当前系统熵状态
    """
    # Handle toggle
    if metabolism:
        set_metabolism_mode(metabolism.lower() == "on")
        
    # Get mode info
    sim_mode = get_simulation_mode() if is_simulation_mode() else "stable"
    sim_label = get_simulation_label(sim_mode) if is_simulation_mode() else "常态运行"
    
    # Calculate metrics
    entropy_data = calculate_total_entropy()
    series_data = get_entropy_series(days=7)
    avg_7d = sum(series_data['entropy_total']) / len(series_data['entropy_total']) if series_data['entropy_total'] else 0
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metabolism_mode = "ON" if get_metabolism_mode() else "OFF"
    inputs = {
        "effective_mode": sim_mode,
        "effective_mode_label": sim_label,
        "metabolism_mode_query": metabolism if metabolism else "default",
        "weights": entropy_data.get("weights", {})
    }
    metrics = {
        "today_entropy": entropy_data["total"],
        "avg_7d": round(avg_7d, 2),
        "drivers": {
            "state_entropy": entropy_data["h_state"],
            "drift_entropy": entropy_data["h_drift"],
            "access_entropy": entropy_data["h_access"]
        }
    }
    interpretation = {
        "summary": "系统熵反映数字代谢健康程度（0-100），越低越稳定。",
        "why": [
            "H_state 体现告警分布离散度",
            "H_drift 体现合规波动和异常跳变",
            "H_access 体现访问暴露与敏感触达风险"
        ],
        "leader_line": "当前系统熵可控，建议持续关注三子熵变化。"
    }
    
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "inputs": inputs,
        "metrics": metrics,
        "interpretation": interpretation,
        "effective_mode": sim_label,
        "metabolism_mode": metabolism_mode,
        "today_entropy": entropy_data["total"],
        "avg_7d": round(avg_7d, 2),
        "drivers": metrics["drivers"],
        "description": "系统熵反映了数字代谢的健康程度 (0-100)，越低越稳定。"
    }

@router.get("/series")
def get_entropy_series_api(days: int = 30) -> dict[str, Any]:
    """
    获取最近 N 天的熵值趋势
    """
    data = get_entropy_series(days=days)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inputs = {
        "days": days,
        "metabolism_mode": "ON" if get_metabolism_mode() else "OFF"
    }
    metrics = {
        "series_length": len(data["dates"]),
        "entropy_total_avg": round(sum(data["entropy_total"]) / max(1, len(data["entropy_total"])), 2),
        "entropy_total_max": round(max(data["entropy_total"]) if data["entropy_total"] else 0, 2),
        "entropy_total_min": round(min(data["entropy_total"]) if data["entropy_total"] else 0, 2)
    }
    interpretation = {
        "summary": "序列可用于观察熵趋势、波动区间与代谢动作强度。",
        "why": "当总熵上行且代谢动作不足时，通常意味着风险暴露正在积累。"
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "inputs": inputs,
        "metrics": metrics,
        "interpretation": interpretation,
        "dates": data["dates"],
        "entropy_total": data["entropy_total"],
        "entropy_state": data["entropy_state"],
        "entropy_drift": data["entropy_drift"],
        "entropy_access": data["entropy_access"],
        "metabolism_actions": data["metabolism_actions"],
        "unit": "Entropy Score (0-100)"
    }

@router.get("/report")
def get_entropy_report() -> dict[str, Any]:
    """
    获取系统熵与代谢健康度报告 (给领导看)
    """
    entropy_data = calculate_total_entropy()
    total = entropy_data["total"]
    
    # Generate narrative
    status_text = "系统运行平稳"
    reason_text = "各项指标均在可控范围内，代谢算子工作正常。"
    actions = []
    
    if total > 70:
        status_text = "系统熵值过高 (CRITICAL)"
        reason_text = "合规漂移加剧，且存在大量未审计的外部访问。代谢机制响应滞后。"
        actions = [
            "立即开启全量 Verify 算子进行数据清洗",
            "收紧 Bind 策略，限制外部访问 TTL",
            "执行强制 Decay，清理过期影子数据"
        ]
    elif total > 40:
        status_text = "系统熵值上升 (WARNING)"
        reason_text = "告警分布呈现离散化趋势，部分数据节点出现合规漂移。"
        actions = [
            "检查 Ingest 管道的元数据质量",
            "增加 Verify 算子的采样率",
            "关注高频访问对象的 Policy 标签"
        ]
    else:
        status_text = "系统处于低熵有序状态 (HEALTHY)"
        reason_text = "数字代谢机制有效抑制了无序度增长，数据全生命周期闭环良好。"
        actions = [
            "维持当前代谢策略",
            "定期复查 7 日熵均值趋势",
            "优化 Decay 算子的存储回收效率"
        ]
        
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inputs = {
        "metabolism_mode": "ON" if get_metabolism_mode() else "OFF",
        "thresholds": {"healthy": 40, "warning": 70}
    }
    metrics = {
        "current_entropy": total,
        "sub_entropy": {
            "state": entropy_data["h_state"]["value"],
            "drift": entropy_data["h_drift"]["value"],
            "access": entropy_data["h_access"]["value"]
        }
    }
    interpretation = {
        "leader_line": f"当前系统熵为 {round(total, 2)}，{status_text}。",
        "engineer_line": "当 H(t)=ws*H_state+wd*H_drift+wa*H_access 持续上行时，应提高 Verify/Bind/Decay 强度。",
        "suggestions": actions
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "inputs": inputs,
        "metrics": metrics,
        "interpretation": interpretation,
        "title": "数字代谢熵控制报告",
        "timestamp": generated_at,
        "status": status_text,
        "analysis": reason_text,
        "suggestions": actions,
        "metrics": {
            "current_entropy": total,
            "metabolism_status": "Active" if get_metabolism_mode() else "Inactive"
        }
    }
