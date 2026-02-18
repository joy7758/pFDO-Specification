import hashlib
import os
import threading
import time
from typing import Any, Dict, List

from .parser import parse_csv, parse_json
from .pii import scan_records
from .record_model import Record
from .ingest_store import (
    load_state,
    save_state,
    mark_scan_started,
    mark_scan_finished,
    ensure_today_counters,
)

_state_lock = threading.Lock()
_poller_thread: threading.Thread = None  # type: ignore
_poller_started = False


def _poll_seconds() -> int:
    raw = os.getenv("INGEST_POLL_SECONDS", "10").strip()
    try:
        val = int(raw)
        return max(1, val)
    except ValueError:
        return 10


def _iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def _file_id(path: str, stat_obj: os.stat_result) -> str:
    raw = f"{path}|{int(stat_obj.st_mtime)}|{stat_obj.st_size}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def _iter_watch_dirs(state: Dict[str, Any]) -> List[str]:
    cfg = state.get("config", {})
    dirs = [cfg.get("watch_dir", ""), cfg.get("demo_drop_dir", "")]
    return [d for d in dirs if d]


def _to_records(path: str, ext: str) -> List[Record]:
    filename = os.path.basename(path)
    if ext == ".csv":
        return parse_csv(path, filename)
    if ext == ".json":
        return parse_json(path, filename)
    if ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return [
            Record(
                source_type="txt",
                record_id=f"ing-{int(time.time() * 1000)}",
                content=content,
                metadata={"filename": filename},
            )
        ]
    raise ValueError("不支持的文件类型")


def _append_recent(state: Dict[str, Any], item: Dict[str, Any]) -> None:
    recent = state.setdefault("recent", [])
    recent.insert(0, item)
    del recent[50:]


def _scan_one_file(state: Dict[str, Any], path: str, stat_obj: os.stat_result) -> None:
    counters = state["counters"]
    filename = os.path.basename(path)
    ext = os.path.splitext(filename)[1].lower()
    file_id = _file_id(path, stat_obj)
    seen_ids = state.setdefault("seen_ids", {})

    if file_id in seen_ids:
        return

    counters["seen"] += 1
    counters["today_seen"] += 1

    item = {
        "file_id": file_id,
        "filename": filename,
        "ext": ext,
        "size": int(stat_obj.st_size),
        "mtime": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(stat_obj.st_mtime)),
        "processed_at": _iso_now(),
        "ok": False,
        "pii_summary": {"phones_found": 0, "emails_found": 0, "id18_found": 0, "records_with_pii": 0},
        "error": "",
    }

    try:
        if ext not in (".txt", ".json", ".csv"):
            raise ValueError("仅支持 .txt/.json/.csv 文件")
        records = _to_records(path, ext)
        payload = [r.model_dump() for r in records]
        result = scan_records(payload)
        summary = result.get("summary", {})
        pii_total = int(summary.get("phones_found", 0)) + int(summary.get("emails_found", 0)) + int(summary.get("id18_found", 0))

        item["ok"] = True
        item["pii_summary"] = {
            "phones_found": int(summary.get("phones_found", 0)),
            "emails_found": int(summary.get("emails_found", 0)),
            "id18_found": int(summary.get("id18_found", 0)),
            "records_with_pii": int(summary.get("records_with_pii", 0)),
        }
        counters["processed"] += 1
        counters["today_processed"] += 1
        counters["pii_hits"] += pii_total
        counters["today_pii_hits"] += pii_total
    except Exception as exc:
        item["error"] = str(exc)
        counters["failed"] += 1
        counters["today_failed"] += 1
    finally:
        seen_ids[file_id] = item["processed_at"]
        _append_recent(state, item)


def scan_watch_dir(state: Dict[str, Any]) -> Dict[str, Any]:
    ensure_today_counters(state)
    state["config"]["poll_seconds"] = _poll_seconds()

    for watch_dir in _iter_watch_dirs(state):
        if not os.path.isdir(watch_dir):
            continue
        try:
            names = sorted(os.listdir(watch_dir))
        except Exception:
            continue
        for name in names:
            full_path = os.path.join(watch_dir, name)
            if not os.path.isfile(full_path):
                continue
            try:
                st = os.stat(full_path)
            except Exception:
                continue
            _scan_one_file(state, full_path, st)
    return state


def get_status() -> Dict[str, Any]:
    with _state_lock:
        state = load_state()
        state["config"]["poll_seconds"] = _poll_seconds()
        save_state(state)
        return {
            "config": state["config"],
            "runtime": state["runtime"],
            "counters": state["counters"],
            "watch_dir": state["config"].get("watch_dir", ""),
            "recent_count": len(state.get("recent", [])),
        }


def get_recent(limit: int = 20) -> Dict[str, Any]:
    if limit < 1 or limit > 50:
        raise ValueError("limit 必须在 1-50 之间")
    with _state_lock:
        state = load_state()
        return {"recent": state.get("recent", [])[:limit]}


def scan_now() -> Dict[str, Any]:
    with _state_lock:
        state = load_state()
        mark_scan_started(state)
        save_state(state)
        ok = True
        try:
            scan_watch_dir(state)
        except Exception:
            ok = False
        mark_scan_finished(state, ok=ok)
        save_state(state)
        return {
            "ok": ok,
            "message": "立即扫描已完成" if ok else "立即扫描执行完成（存在失败项）",
            "runtime": state["runtime"],
            "counters": state["counters"],
        }


def demo_dropfile() -> Dict[str, Any]:
    with _state_lock:
        state = load_state()
        drop_dir = state["config"].get("demo_drop_dir", "")
        if not drop_dir:
            return {"ok": False, "message": "未配置演示投递目录"}
        os.makedirs(drop_dir, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        filename = f"ingest_demo_{ts}.txt"
        full_path = os.path.join(drop_dir, filename)
        sample = (
            "这是一份抄送样本文件。\n"
            "联系人：张三，手机号：13812345678。\n"
            "邮箱：demo.secure@example.com。\n"
            "身份证：110101199001011234。\n"
        )
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(sample)

    return {
        "ok": True,
        "message": "示例文件已写入并触发扫描",
        "file": filename,
        "scan": scan_now(),
    }


def _poll_loop() -> None:
    while True:
        try:
            scan_now()
        except Exception:
            pass
        time.sleep(_poll_seconds())


def start_background_poller() -> Dict[str, Any]:
    global _poller_thread, _poller_started
    with _state_lock:
        if _poller_started and _poller_thread and _poller_thread.is_alive():
            return {"started": True, "already_running": True}
        _poller_thread = threading.Thread(target=_poll_loop, daemon=True, name="ingest-poller")
        _poller_thread.start()
        _poller_started = True
        return {"started": True, "already_running": False}
