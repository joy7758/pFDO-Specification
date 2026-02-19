import hashlib
import json
import time
from typing import Any, Optional
from datetime import datetime, timedelta

# Mock state storage for demo purposes
METABOLISM_STATE = {
    "ingested_count": 0,
    "verified_count": 0,
    "verify_fail_count": 0,
    "bound_count": 0,
    "decayed_count": 0,
    "records": {}  # id -> {data, hash, policy, timestamp, ttl}
}

METABOLISM_MODE = False

def set_metabolism_mode(mode: bool):
    global METABOLISM_MODE
    METABOLISM_MODE = mode

def get_metabolism_mode() -> bool:
    return METABOLISM_MODE

def reset_metabolism_state():
    global METABOLISM_STATE
    METABOLISM_STATE = {
        "ingested_count": 0,
        "verified_count": 0,
        "verify_fail_count": 0,
        "bound_count": 0,
        "decayed_count": 0,
        "records": {}
    }

# --- Operators ---

def ingest(record_id: str, content: Any, source: str = "unknown") -> dict[str, Any]:
    """
    Ingest operator: Accepts data into the metabolic cycle.
    """
    METABOLISM_STATE["ingested_count"] += 1
    
    # Basic record structure
    record = {
        "id": record_id,
        "content": content,
        "source": source,
        "ingested_at": time.time(),
        "status": "ingested"
    }
    
    METABOLISM_STATE["records"][record_id] = record
    return record

def verify(record_id: str) -> bool:
    """
    Verify operator: Schema check + Hash.
    If metabolism is OFF, verification might be skipped or always pass without check.
    """
    if not METABOLISM_MODE:
        return True # Pass through if metabolism is off (or strictly speaking, no verification happens)
        
    record = METABOLISM_STATE["records"].get(record_id)
    if not record:
        return False
        
    # 1. Schema Check (Mock: just check if content is not empty)
    if not record["content"]:
        METABOLISM_STATE["verify_fail_count"] += 1
        record["status"] = "verify_failed"
        return False
        
    # 2. Hash Calculation
    content_str = str(record["content"])
    record["hash"] = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
    
    METABOLISM_STATE["verified_count"] += 1
    record["status"] = "verified"
    return True

def bind(record_id: str) -> str:
    """
    Bind operator: Assign policy tag.
    """
    if not METABOLISM_MODE:
        return "none"
        
    record = METABOLISM_STATE["records"].get(record_id)
    if not record or record["status"] != "verified":
        return "none"
        
    # Mock Policy Logic
    content_str = str(record["content"])
    if "secret" in content_str or "private" in content_str:
        tag = "INTERNAL_ONLY"
        ttl = 3600 # 1 hour
    elif "public" in content_str:
        tag = "PUBLIC"
        ttl = 86400 # 24 hours
    else:
        tag = "AUDIT_REQUIRED"
        ttl = 7200 # 2 hours
        
    record["policy_tag"] = tag
    record["ttl"] = ttl
    METABOLISM_STATE["bound_count"] += 1
    record["status"] = "bound"
    
    return tag

def decay(record_id: str) -> bool:
    """
    Decay operator: Check TTL and mark as decayed if expired.
    """
    if not METABOLISM_MODE:
        return False
        
    record = METABOLISM_STATE["records"].get(record_id)
    if not record or "ttl" not in record:
        return False
        
    age = time.time() - record["ingested_at"]
    if age > record["ttl"]:
        record["status"] = "decayed"
        METABOLISM_STATE["decayed_count"] += 1
        return True
        
    return False

def get_metabolism_stats() -> dict[str, Any]:
    return {
        "mode": "ON" if METABOLISM_MODE else "OFF",
        "ingested": METABOLISM_STATE["ingested_count"],
        "verified": METABOLISM_STATE["verified_count"],
        "verify_failures": METABOLISM_STATE["verify_fail_count"],
        "bound": METABOLISM_STATE["bound_count"],
        "decayed": METABOLISM_STATE["decayed_count"],
        "active_records": len(METABOLISM_STATE["records"]) - METABOLISM_STATE["decayed_count"]
    }

def run_metabolism_cycle():
    """
    Simulate a full cycle run on all active records.
    """
    if not METABOLISM_MODE:
        return
        
    # Iterate over copy of keys
    for rid in list(METABOLISM_STATE["records"].keys()):
        record = METABOLISM_STATE["records"][rid]
        
        if record["status"] == "ingested":
            verify(rid)
            
        if record["status"] == "verified":
            bind(rid)
            
        if record["status"] == "bound":
            decay(rid)
