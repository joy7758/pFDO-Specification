from contextvars import ContextVar
from typing import Optional

# ContextVar to store the current simulation mode for the request
_simulation_mode_ctx: ContextVar[Optional[str]] = ContextVar("simulation_mode_ctx", default=None)

def set_simulation_mode_context(mode: Optional[str]):
    _simulation_mode_ctx.set(mode)

def get_simulation_mode_context() -> Optional[str]:
    return _simulation_mode_ctx.get()
