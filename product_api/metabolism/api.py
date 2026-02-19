from fastapi import APIRouter, Query
from typing import Any
from datetime import datetime, timedelta

from ..dashboard import is_simulation_mode, get_simulation_mode, get_simulation_label
from .metrics import calculate_total_entropy, get_entropy_series
from .operators import get_metabolism_mode, set_metabolism_mode, get_metabolism_stats

router = APIRouter(prefix="/api/v1/entropy", tags=["Entropy"])

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
    
    return {
        "effective_mode": sim_label,
        "metabolism_mode": "ON" if get_metabolism_mode() else "OFF",
        "today_entropy": entropy_data["total"],
        "avg_7d": round(avg_7d, 2),
        "drivers": {
            "state_entropy": entropy_data["h_state"],
            "drift_entropy": entropy_data["h_drift"],
            "access_entropy": entropy_data["h_access"]
        },
        "description": "系统熵反映了数字代谢的健康程度 (0-100)，越低越稳定。"
    }

@router.get("/series")
def get_entropy_series_api(days: int = 30) -> dict[str, Any]:
    """
    获取最近 N 天的熵值趋势
    """
    data = get_entropy_series(days=days)
    return {
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
        
    return {
        "title": "数字代谢熵控制报告",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status_text,
        "analysis": reason_text,
        "suggestions": actions,
        "metrics": {
            "current_entropy": total,
            "metabolism_status": "Active" if get_metabolism_mode() else "Inactive"
        }
    }
