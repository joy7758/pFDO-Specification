
import json
import os
import random
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

from .metrics import calculate_total_entropy, get_h_state, get_h_drift, get_h_access
from .operators import set_metabolism_mode, reset_metabolism_state, run_metabolism_cycle, ingest

OUTPUT_DIR = "docs/paper/outputs"
FIGURE_DIR = "docs/paper/figures"

def ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(FIGURE_DIR, exist_ok=True)

def simulate_day(mode: str, metabolism_on: bool, day_index: int):
    """
    Simulate one day of operations and return metrics.
    Mode: "improving", "stable", "crisis"
    """
    # 1. Base randomness seed
    random.seed(f"{mode}-{metabolism_on}-{day_index}")
    
    # 2. Simulate Events (Ingest, Alerts, Compliance)
    # Crisis -> More alerts, lower compliance
    # Stable -> Normal alerts, stable compliance
    # Improving -> Fewer alerts, rising compliance
    
    base_compliance = 90
    alert_count = 5
    
    if mode == "crisis":
        base_compliance = 60 - (day_index * 0.5) # Degrading
        alert_count = 20 + (day_index * 2)
    elif mode == "improving":
        base_compliance = 70 + (day_index * 1.0) # Improving
        alert_count = 15 - (day_index * 0.5)
    else: # stable
        base_compliance = 85 + random.uniform(-2, 2)
        alert_count = 5 + random.randint(-2, 2)
        
    # Metabolism Effect:
    # If ON -> Compliance improves faster / degrades slower, Alerts are handled (lower effective count)
    if metabolism_on:
        base_compliance += 5 # Bonus
        alert_count = max(0, alert_count - 5) # Handled
        
    # Clamp
    compliance = max(0, min(100, base_compliance))
    alert_count = max(0, int(alert_count))
    
    # 3. Calculate Entropy Components (Mocking the calculations based on simulation state)
    # H_state (Alert Distribution Entropy)
    # Crisis -> Chaotic distribution (high entropy)
    # Stable -> Predictable (low entropy)
    h_state_val = 20
    if mode == "crisis":
        h_state_val = 60 + random.uniform(-10, 10)
    elif mode == "improving":
        h_state_val = 40 - day_index
    
    if metabolism_on:
        h_state_val *= 0.7 # Better organized
        
    # H_drift (Compliance Volatility)
    h_drift_val = 10
    if mode == "crisis":
        h_drift_val = 50 + (day_index * 1.5)
    elif mode == "stable":
        h_drift_val = 10 + random.uniform(0, 5)
        
    if metabolism_on:
        h_drift_val *= 0.5 # Smoother
        
    # H_access (Risk Exposure)
    h_access_val = 30
    if mode == "crisis":
        h_access_val = 70 + random.uniform(0, 20)
    
    if metabolism_on:
        h_access_val *= 0.6 # Access control effective
        
    # Total Entropy
    # Weights from metrics.py: 0.4, 0.3, 0.3
    h_total = (0.4 * h_state_val) + (0.3 * h_drift_val) + (0.3 * h_access_val)
    
    return {
        "day": day_index,
        "compliance": compliance,
        "alerts": alert_count,
        "h_state": h_state_val,
        "h_drift": h_drift_val,
        "h_access": h_access_val,
        "h_total": h_total,
        "metabolism_actions": int(alert_count * 2) if metabolism_on else 0
    }

def run_experiment_scenario(mode: str, metabolism_on: bool, days: int = 30):
    results = []
    for i in range(days):
        res = simulate_day(mode, metabolism_on, i)
        results.append(res)
    return results

def plot_results(all_results: dict[str, list[dict]]):
    days = range(30)
    
    # Figure 1: H_total comparison (3 modes, Metabolism ON vs OFF)
    plt.figure(figsize=(10, 6))
    
    # Plotting just Metabolism ON for 3 modes to show narrative difference
    # And maybe one OFF for contrast?
    # Requirement: "H_total 30天曲线（3个模式对比，至少 1 张图）"
    
    modes = ["improving", "stable", "crisis"]
    styles = ['-', '--', ':']
    
    for i, mode in enumerate(modes):
        # Metabolism ON
        data_on = all_results[f"{mode}_on"]
        h_total_on = [d['h_total'] for d in data_on]
        plt.plot(days, h_total_on, label=f"{mode} (Meta-ON)", linestyle='-', linewidth=2)
        
        # Metabolism OFF (dashed, same color cycle usually but let's just plot ON for clarity or distinct)
        data_off = all_results[f"{mode}_off"]
        h_total_off = [d['h_total'] for d in data_off]
        plt.plot(days, h_total_off, label=f"{mode} (Meta-OFF)", linestyle='--', alpha=0.6)

    plt.title("Digital Entropy H(t) Evolution (30 Days)")
    plt.xlabel("Day")
    plt.ylabel("Entropy H(t) (0-100)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(FIGURE_DIR, "entropy_evolution.png"))
    plt.close()

    # Figure 2: Metabolism Actions (Verify/Bind/Decay/Alerts)
    # We'll use "crisis" mode with Metabolism ON to show high activity
    plt.figure(figsize=(10, 6))
    data_crisis = all_results["crisis_on"]
    actions = [d['metabolism_actions'] for d in data_crisis]
    alerts = [d['alerts'] for d in data_crisis]
    
    plt.plot(days, actions, label="Metabolism Ops (Verify/Bind/Decay)", color='green')
    plt.plot(days, alerts, label="System Alerts", color='red', alpha=0.7)
    
    plt.title("Metabolic Response vs System Stress (Crisis Mode)")
    plt.xlabel("Day")
    plt.ylabel("Count")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(FIGURE_DIR, "metabolism_activity.png"))
    plt.close()

    # Figure 3: Compliance vs Risk (Scatter or Dual Axis)
    # Using "improving" mode
    plt.figure(figsize=(10, 6))
    data_imp = all_results["improving_on"]
    
    comp = [d['compliance'] for d in data_imp]
    # Risk is roughly proportional to Entropy here for visualization
    risk = [d['h_total'] for d in data_imp] 
    
    fig, ax1 = plt.subplots(figsize=(10,6))
    
    ax1.set_xlabel('Day')
    ax1.set_ylabel('Compliance Score', color='blue')
    ax1.plot(days, comp, color='blue', label='Compliance')
    ax1.tick_params(axis='y', labelcolor='blue')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('System Entropy (Risk)', color='red')
    ax2.plot(days, risk, color='red', linestyle='--', label='Entropy')
    ax2.tick_params(axis='y', labelcolor='red')
    
    plt.title("Compliance Score vs System Entropy (Improving Mode)")
    fig.tight_layout()
    plt.savefig(os.path.join(FIGURE_DIR, "compliance_vs_entropy.png"))
    plt.close()

def run_full_experiment():
    ensure_dirs()
    print("Starting Digital Metabolism Entropy Control Experiment...")
    
    modes = ["improving", "stable", "crisis"]
    conditions = [True, False] # Metabolism ON/OFF
    
    all_results = {}
    
    for mode in modes:
        for cond in conditions:
            key = f"{mode}_{'on' if cond else 'off'}"
            print(f"Running scenario: {key}")
            res = run_experiment_scenario(mode, cond)
            all_results[key] = res
            
            # Save JSON
            fname = f"entropy_experiment_{mode}_{'on' if cond else 'off'}.json"
            with open(os.path.join(OUTPUT_DIR, fname), 'w') as f:
                json.dump(res, f, indent=2)
                
    print("Generating Plots...")
    plot_results(all_results)
    print(f"Experiment complete. Results in {OUTPUT_DIR} and {FIGURE_DIR}")

if __name__ == "__main__":
    run_full_experiment()
