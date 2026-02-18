import json
import os
import time
from typing import Any, Dict

STATE_PATH = os.path.join(os.path.dirname(__file__), ".ingest_state.json")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
DROPBOX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ingest_drop")


def _iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def _today_key() -> str:
    return time.strftime("%Y-%m-%d", time.localtime())


def _default_state() -> Dict[str, Any]:
    return {
        "config": {
            "watch_dir": UPLOADS_DIR,
            "demo_drop_dir": DROPBOX_DIR,
            "poll_seconds": 10
        },
        "runtime": {
            "last_scan_at": "",
            "last_ok_at": "",
            "running": False
        },
        "counters": {
            "seen": 0,
            "processed": 0,
            "failed": 0,
            "pii_hits": 0,
            "today_seen": 0,
            "today_processed": 0,
            "today_failed": 0,
            "today_pii_hits": 0,
            "day_key": _today_key()
        },
        "seen_ids": {},
        "recent": []
    }


def _ensure_dirs(state: Dict[str, Any]) -> None:
    cfg = state.get("config", {})
    os.makedirs(cfg.get("watch_dir", UPLOADS_DIR), exist_ok=True)
    os.makedirs(cfg.get("demo_drop_dir", DROPBOX_DIR), exist_ok=True)


def load_state() -> Dict[str, Any]:
    state = _default_state()
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                state.update({k: v for k, v in loaded.items() if k in state})
        except Exception:
            pass

    # merge nested keys defensively
    for section in ("config", "runtime", "counters"):
        incoming = state.get(section, {})
        defaults = _default_state()[section]
        if not isinstance(incoming, dict):
            incoming = {}
        merged = defaults.copy()
        merged.update(incoming)
        state[section] = merged

    if not isinstance(state.get("recent"), list):
        state["recent"] = []
    if not isinstance(state.get("seen_ids"), dict):
        state["seen_ids"] = {}

    _ensure_dirs(state)
    return state


def save_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    serializable = dict(state)
    # avoid unbounded growth from very old IDs
    seen_ids = serializable.get("seen_ids", {})
    if isinstance(seen_ids, dict) and len(seen_ids) > 5000:
        # keep latest by processed time string
        items = sorted(seen_ids.items(), key=lambda kv: str(kv[1]), reverse=True)[:2000]
        serializable["seen_ids"] = dict(items)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)


def mark_scan_started(state: Dict[str, Any]) -> None:
    state["runtime"]["running"] = True
    state["runtime"]["last_scan_at"] = _iso_now()


def mark_scan_finished(state: Dict[str, Any], ok: bool = True) -> None:
    state["runtime"]["running"] = False
    if ok:
        state["runtime"]["last_ok_at"] = _iso_now()


def ensure_today_counters(state: Dict[str, Any]) -> None:
    today = _today_key()
    counters = state["counters"]
    if counters.get("day_key") != today:
        counters["day_key"] = today
        counters["today_seen"] = 0
        counters["today_processed"] = 0
        counters["today_failed"] = 0
        counters["today_pii_hits"] = 0
