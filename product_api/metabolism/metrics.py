import math
import random
from datetime import datetime, timedelta
from typing import Any
from ..dashboard import get_alerts_data, calculate_dynamic_risk_score, get_trends_data, is_simulation_mode

# Weights
WS = 0.4  # State weight
WD = 0.3  # Drift weight
WA = 0.3  # Access weight

def calculate_shannon_entropy(distribution: list[float]) -> float:
    """Calculate Shannon entropy for a given probability distribution."""
    entropy = 0.0
    total = sum(distribution)
    if total == 0:
        return 0.0
    
    for count in distribution:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy

def normalize_score(value: float, min_val: float, max_val: float) -> float:
    """Normalize value to 0-100 range."""
    if max_val <= min_val:
        return 0.0
    normalized = (value - min_val) / (max_val - min_val) * 100
    return max(0.0, min(100.0, normalized))

def get_h_state() -> dict[str, Any]:
    """
    Calculate H_state: Based on alerts classification distribution.
    """
    alerts_data = get_alerts_data()
    alerts = alerts_data.get('alerts', [])
    
    # Group by type
    type_counts = {}
    for alert in alerts:
        t = alert.get('type', 'unknown')
        type_counts[t] = type_counts.get(t, 0) + 1
    
    if not type_counts:
        # Fallback distribution
        type_counts = {"mock_a": 5, "mock_b": 3, "mock_c": 2}

    entropy_val = calculate_shannon_entropy(list(type_counts.values()))
    
    # Max entropy for ~6 types is log2(6) ~= 2.58
    # Normalize to 0-100
    normalized_val = normalize_score(entropy_val, 0, 3.0)
    
    return {
        "value": normalized_val,
        "raw_entropy": entropy_val,
        "description": "告警分布熵 (基于Shannon Entropy)"
    }

def get_h_drift() -> dict[str, Any]:
    """
    Calculate H_drift: Volatility of compliance score + abnormal jumps.
    """
    # Get trends (last 30 days)
    trends = get_trends_data()
    scores = trends.get('risk_scores', [])
    
    if len(scores) < 2:
        return {"value": 0, "description": "数据不足"}
    
    # Calculate daily differences
    diffs = []
    jumps = 0
    threshold = 10 # Jump threshold
    
    for i in range(1, len(scores)):
        diff = abs(scores[i] - scores[i-1])
        diffs.append(diff)
        if diff > threshold:
            jumps += 1
            
    avg_diff = sum(diffs) / len(diffs) if diffs else 0
    
    # Drift score: avg volatility + penalty for jumps
    raw_drift = avg_diff + (jumps * 5)
    
    # Normalize (Assuming max reasonable drift ~20 per day + jumps)
    normalized_val = normalize_score(raw_drift, 0, 30)
    
    return {
        "value": normalized_val,
        "raw_drift": raw_drift,
        "jumps": jumps,
        "description": "合规漂移熵 (波动率 + 突变计数)"
    }

def get_h_access() -> dict[str, Any]:
    """
    Calculate H_access: Weighted sum of PII hits + unaudited files + high-risk alerts.
    """
    risk_data = calculate_dynamic_risk_score()
    
    pii_hits = risk_data.get('hits_today', 0)
    # Using 'file_count' as proxy for potentially unaudited files in this context
    # In a real system, we'd filter for 'unaudited' tag
    unaudited_files = risk_data.get('file_count', 0) * 0.1 # Assume 10% are unaudited
    active_alerts = risk_data.get('alerts_active', 0)
    
    # Weighted sum
    # PII hits are bad (weight 1)
    # Unaudited files are potential risk (weight 0.5)
    # Active alerts are realized risk (weight 2)
    raw_access = (pii_hits * 1.0) + (unaudited_files * 0.5) + (active_alerts * 2.0)
    
    # Normalize (Assuming max reasonable raw access ~100)
    normalized_val = normalize_score(raw_access, 0, 100)
    
    return {
        "value": normalized_val,
        "raw_access": raw_access,
        "details": {
            "pii_hits": pii_hits,
            "unaudited_files_est": unaudited_files,
            "active_alerts": active_alerts
        },
        "description": "访问熵 (PII命中 + 未审计文件 + 高风险告警)"
    }

def calculate_total_entropy() -> dict[str, Any]:
    """
    Calculate Total Entropy H(t) = ws*H_state + wd*H_drift + wa*H_access
    """
    h_state = get_h_state()
    h_drift = get_h_drift()
    h_access = get_h_access()
    
    total = (WS * h_state['value']) + (WD * h_drift['value']) + (WA * h_access['value'])
    
    return {
        "total": round(total, 2),
        "h_state": h_state,
        "h_drift": h_drift,
        "h_access": h_access,
        "weights": {"ws": WS, "wd": WD, "wa": WA}
    }

def get_entropy_series(days: int = 30) -> dict[str, Any]:
    """
    Generate entropy series for the last N days.
    """
    # Since we don't have historical data for all components, we'll simulate history
    # based on the current mode or a seed.
    
    dates = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(days-1, -1, -1)]
    
    # Base simulation on trends data to be somewhat consistent
    trends = get_trends_data() # Gets 30 days
    risk_scores = trends.get('risk_scores', [])
    # Adjust length if needed
    if len(risk_scores) > days:
        risk_scores = risk_scores[-days:]
    elif len(risk_scores) < days:
        risk_scores = [90] * (days - len(risk_scores)) + risk_scores
        
    entropy_total = []
    entropy_state = []
    entropy_drift = []
    entropy_access = []
    metabolism_actions = []
    
    # Simulate variations based on risk score (Lower risk score -> Higher entropy typically)
    for score in risk_scores:
        # Base inverse relation
        base_entropy = 100 - score 
        
        # Add noise
        e_state = max(0, min(100, base_entropy * 0.8 + random.uniform(-5, 15)))
        e_drift = max(0, min(100, base_entropy * 1.2 + random.uniform(-5, 15)))
        e_access = max(0, min(100, base_entropy + random.uniform(-10, 20)))
        
        e_total = (WS * e_state) + (WD * e_drift) + (WA * e_access)
        
        entropy_total.append(round(e_total, 2))
        entropy_state.append(round(e_state, 2))
        entropy_drift.append(round(e_drift, 2))
        entropy_access.append(round(e_access, 2))
        
        # Metabolism actions (Inverse to entropy - higher entropy needs more metabolism)
        actions_count = int(e_total * random.uniform(0.5, 1.5))
        metabolism_actions.append(actions_count)

    return {
        "dates": dates,
        "entropy_total": entropy_total,
        "entropy_state": entropy_state,
        "entropy_drift": entropy_drift,
        "entropy_access": entropy_access,
        "metabolism_actions": metabolism_actions
    }
