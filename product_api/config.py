import os
import datetime

def get_data_mode() -> str:
    """
    获取数据模式
    - random: 纯随机 (默认 for dev)
    - demo: 演示模式 (基于 seed 的确定性随机)
    - simulation: 叙事模拟模式 (基于 narrative engine)
    """
    return os.getenv("DATA_MODE", "demo").lower()

def get_simulation_mode() -> str:
    """
    获取叙事模拟模式 (仅在 DATA_MODE=simulation 时生效)
    - improving: 改善叙事 (风险下降)
    - stable: 稳定叙事 (平稳波动)
    - crisis: 危机叙事 (风险上升)
    """
    return os.getenv("SIMULATION_MODE", "stable").lower()

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
