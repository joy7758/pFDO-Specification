import os
import datetime
from .context import get_simulation_mode_context

def get_data_mode() -> str:
    """
    获取数据模式
    - random: 纯随机 (默认 for dev)
    - demo: 演示模式 (基于 seed 的确定性随机)
    - simulation: 叙事模拟模式 (基于 narrative engine)
    """
    # Context override if set (e.g., from sim query param, implies simulation mode)
    if get_simulation_mode_context():
        return "simulation"
    return os.getenv("DATA_MODE", "demo").lower()

def get_simulation_mode() -> str:
    """
    获取叙事模拟模式 (仅在 DATA_MODE=simulation 时生效)
    - improving: 持续改善
    - stable: 平稳运行
    - crisis: 风险上升
    """
    # Context override
    ctx_mode = get_simulation_mode_context()
    if ctx_mode and ctx_mode in ("improving", "stable", "crisis"):
        return ctx_mode

    return os.getenv("SIMULATION_MODE", "stable").lower()

def get_simulation_label(mode: str) -> str:
    """获取中文标签"""
    labels = {
        "improving": "持续改善",
        "stable": "平稳运行",
        "crisis": "风险上升"
    }
    return labels.get(mode, "未知模式")

def get_demo_seed() -> int:
    """获取演示模式种子"""
    try:
        return int(os.getenv("DEMO_SEED", "2026"))
    except ValueError:
        return 2026

def get_sim_start_date() -> str:
    """
    获取模拟开始日期 (YYYY-MM-DD)
    默认为今天
    """
    default_date = datetime.date.today().strftime("%Y-%m-%d")
    return os.getenv("SIM_START_DATE", default_date)

def is_demo_mode() -> bool:
    """检查是否处于演示锁定模式 (兼容旧代码)"""
    return get_data_mode() == "demo" or os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")

def is_simulation_mode() -> bool:
    """检查是否处于叙事模拟模式"""
    return get_data_mode() == "simulation"
