import time
import random
import os
import sys
import struct
import numpy as np

# Add server directory to path to import fdo_gate directly for stress testing
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "mcp-server"))

from fdo_gate import FDOGate

def stress_test_msbv(count=1000000):
    print(f">>> Starting MsBV Stress Test with {count} packets...")
    
    gate = FDOGate()
    
    # Pre-generate random Policy IDs
    # Most should be invalid (for stress testing rejection path)
    # Valid IDs: 0x01, 0x02, 0x03, 0x04
    # We will generate IDs in range 0x00 to 0xFF
    policy_ids = np.random.randint(0, 256, count, dtype=np.uint32)
    
    # Pre-generate valid packets components to minimize packet creation overhead 
    # during the timing loop, so we focus on the validation logic.
    # However, to simulate realistic traffic, we should probably use create_packet logic inside loop?
    # No, we want to test "Validation" speed primarily (Layer 5 MsBV lookup).
    # So we will pre-construct raw headers.
    
    headers = []
    print("Generating test vectors...")
    
    # Vectorized generation would be faster but let's stick to Python loop for simplicity 
    # as 1M is manageable.
    # Magic: 0xFD01
    # Seq: Random
    # TS: Current
    
    magic = 0xFD01
    current_ts = int(time.time() * 1e7) & 0xFFFFFFFF
    
    # We use a fixed payload for all
    payload = b"STRESS"
    
    valid_ids = {0x01, 0x02, 0x03, 0x04}
    
    start_gen = time.time()
    for pid in policy_ids:
        # Create packet using the internal helper logic manually to avoid function call overhead
        # during generation if possible, but let's use the class method for correctness.
        # Actually, let's pre-generate valid headers to test the GATE's processing speed.
        seq = random.randint(0, 0xFFFFFFFF)
        masked_pid = pid ^ seq
        
        # Calculate Checksum (we want checksum to be valid so we hit the MsBV check)
        # header_parts = (magic, seq, current_ts, masked_pid)
        # checksum = gate.calculate_folded_checksum(header_parts, payload[:2])
        
        # Optimization: To make generation faster, we can skip checksum calculation 
        # if we are ONLY testing MsBV? 
        # NO, the gate validates checksum FIRST. If checksum fails, MsBV is not reached.
        # So we MUST generate valid checksums.
        
        pkt = gate.create_packet(magic, seq, int(pid), payload)
        headers.append(pkt)
        
    end_gen = time.time()
    print(f"Generation took {end_gen - start_gen:.4f}s")
    
    print("Executing stress test (processing packets)...")
    start_time = time.time()
    
    blocked_count = 0
    passed_count = 0
    
    for pkt in headers:
        # We process the packet directly via the gate logic
        # We can call process_packet
        res = gate.process_packet(pkt)
        if res['status'] == 'dropped':
            blocked_count += 1
        else:
            passed_count += 1
            
    end_time = time.time()
    total_time = end_time - start_time
    avg_latency = (total_time / count) * 1e6 # in microseconds
    
    print(f"Stress Test Complete.")
    print(f"Total Time: {total_time:.4f}s")
    print(f"Average Latency per Packet: {avg_latency:.4f} μs")
    print(f"Throughput: {count / total_time:.0f} packets/sec")
    print(f"Blocked (Invalid Policy): {blocked_count}")
    print(f"Passed (Valid Policy): {passed_count}")
    
    # Save results
    with open("stress_test_results.txt", "w") as f:
        f.write(f"Count: {count}\n")
        f.write(f"Total Time: {total_time:.6f}s\n")
        f.write(f"Average Latency: {avg_latency:.6f} us\n")
        f.write(f"Throughput: {count / total_time:.2f} pps\n")
        f.write(f"Blocked: {blocked_count}\n")
        f.write(f"Passed: {passed_count}\n")

if __name__ == "__main__":
    stress_test_msbv()
