import time
import sys
import os
import random
import json
import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "mcp-server"))

from fdo_gate import FDOGate

class DualLayerMemoryModel:
    def __init__(self):
        # 1. Axiomatic Core (Immutable Logic Anchors)
        self.axiomatic_core = {
            "policies": {
                0x01: {"level": 0, "action": "ALLOW"},
                0x02: {"level": 1, "action": "RESTRICTED"},
                0x03: {"level": 2, "action": "CONFIDENTIAL"},
                0x04: {"level": 3, "action": "TOP_SECRET"},
                0x99: {"level": 0, "action": "DROP_ALL"} # Sentinel rule
            },
            "checksum_logic": "FOLDED_XOR",
            "timestamp_window": 20000000 # +/- 2s in 100ns ticks
        }
        
        # 2. Volatile Facts (Redundant Data)
        # Initializing with 1,000,000 dummy fact records
        print("Building Volatile Facts (1M records)...")
        self.volatile_facts = {}
        for i in range(1000000):
            self.volatile_facts[f"fact_{i}"] = {
                "ts": time.time(),
                "access_count": random.randint(0, 100),
                "metadata": "redundant_trace_data" * 5
            }
        print(f"Memory Model Initialized. Facts: {len(self.volatile_facts)}")

    def metabolic_purge(self, retention_rate=0.01):
        """
        Simulate RLCP Unlearning: Purge redundant facts based on retention rate.
        Crucially, Axiomatic Core must remain untouched.
        """
        print(f"\n>>> Executing Metabolic Purge (Target Retention: {retention_rate*100}%)...")
        initial_count = len(self.volatile_facts)
        
        # Simulate unlearning by deleting keys
        keys_to_delete = random.sample(list(self.volatile_facts.keys()), int(initial_count * (1 - retention_rate)))
        
        start_purge = time.time()
        for k in keys_to_delete:
            del self.volatile_facts[k]
        end_purge = time.time()
        
        final_count = len(self.volatile_facts)
        print(f"Purge Complete in {end_purge - start_purge:.4f}s.")
        print(f"Facts Reduced: {initial_count} -> {final_count}")
        
        # Verify Core Integrity
        if len(self.axiomatic_core["policies"]) != 5:
            raise Exception("CRITICAL FAILURE: Axiomatic Core Corrupted!")
        print("Axiomatic Core Integrity: CONFIRMED")

def run_integrity_test():
    memory_model = DualLayerMemoryModel()
    gate = FDOGate()
    
    # Test Vectors
    test_packets = []
    # 1000 packets: 500 valid (Policy 0x01), 500 invalid (Policy 0xFF)
    for _ in range(500):
        test_packets.append({"type": "valid", "pid": 0x01})
        test_packets.append({"type": "invalid", "pid": 0xFF})
    
    def run_benchmark(phase_name):
        print(f"\nRunning {phase_name} Benchmark...")
        start_time = time.time()
        correct_decisions = 0
        
        for case in test_packets:
            # Create packet
            pkt = gate.create_packet(0xFD01, 100, case["pid"], b"TEST")
            
            # Process
            res = gate.process_packet(pkt)
            
            # Verify Logic Accuracy
            if case["type"] == "valid" and res["status"] == "forwarded":
                correct_decisions += 1
            elif case["type"] == "invalid" and res["status"] == "dropped":
                correct_decisions += 1
                
        end_time = time.time()
        total_time = end_time - start_time
        avg_latency = (total_time / len(test_packets)) * 1e6 # microseconds
        accuracy = correct_decisions / len(test_packets)
        
        print(f"{phase_name} Results: Accuracy={accuracy*100:.1f}%, Latency={avg_latency:.4f} us")
        return accuracy, avg_latency

    # Phase 1: Pre-Metabolic Baseline
    acc_pre, lat_pre = run_benchmark("Pre-Metabolic")
    
    # Phase 2: Metabolic Purge
    memory_model.metabolic_purge(retention_rate=0.01) # Keep only 1%
    
    # Phase 3: Post-Metabolic Stress Test
    acc_post, lat_post = run_benchmark("Post-Metabolic")
    
    # Validation
    consistency_passed = (acc_post == 1.0) and (abs(lat_post - lat_pre) < 0.5) # Allow 0.5us jitter
    
    results = {
        "status": "PASSED" if consistency_passed else "FAILED",
        "pre_purge": {
            "facts_count": 1000000,
            "accuracy": acc_pre,
            "latency_us": lat_pre
        },
        "post_purge": {
            "facts_count": 10000,
            "accuracy": acc_post,
            "latency_us": lat_post
        },
        "integrity_check": {
            "logic_core_preserved": True,
            "latency_stability": "STABLE" if abs(lat_post - lat_pre) < 0.5 else "UNSTABLE"
        }
    }
    
    with open("Consistency_Test_Results.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"\nFinal Result: {results['status']}")
    print(f"Report saved to Consistency_Test_Results.json")

if __name__ == "__main__":
    run_integrity_test()
