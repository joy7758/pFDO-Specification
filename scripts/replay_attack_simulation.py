import time
import sys
import os
import struct

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_dir, "mcp-server"))

from fdo_gate import FDOGate

def replay_attack_sim():
    print(">>> Starting Replay Attack Simulation...")
    gate = FDOGate()
    
    # 1. Generate a valid packet at current time
    magic = 0xFD01
    seq = 1001
    pid = 0x01 # Valid Policy
    payload = b"REPLAY_DATA"
    
    print("Generating legitimate packet at T=0...")
    valid_packet = gate.create_packet(magic, seq, pid, payload)
    
    # Verify it passes first
    res = gate.process_packet(valid_packet)
    print(f"T=0 Check: {res['status']}")
    if res['status'] != 'forwarded':
        print("Error: Valid packet failed initial check!")
        return

    # 2. Wait for 2.5 seconds (simulated)
    # Since we can't easily wait 2.5s in unit test without sleep, and we want to control the time check logic,
    # let's modify the timestamp in the packet to be 2.5s OLDER than current time.
    # The gate checks `abs(current - received) > 2s`.
    
    # Extract header
    header = valid_packet[:16]
    # Unpack
    magic, seq, ts, mpid, cksum = struct.unpack('!HIIIH', header)
    
    # Set TS to 3 seconds ago (30,000,000 ticks)
    # Ticks are 100ns units. 3s = 3 * 10^7 ticks.
    old_ts = (ts - 30000000) & 0xFFFFFFFF
    
    print("Modifying packet timestamp to T-3s (Replay Attempt)...")
    
    # We must recalculate checksum because we changed TS
    # If we don't, it will fail on Checksum, not Timestamp.
    # The attacker would recompute checksum if they were modifying the packet, 
    # BUT a replay attack implies re-sending the EXACT same captured packet at a later time.
    
    # SCENARIO A: Strict Replay (Exact same bits)
    # If we wait 3 seconds real time, the gate's `time.time()` will advance.
    # Let's try to actually sleep? 3s is short enough.
    print("Sleeping for 3 seconds to simulate network delay/replay window expiry...")
    time.sleep(3.0)
    
    print("Replaying original packet at T+3s...")
    # Process the ORIGINAL packet again
    res_replay = gate.process_packet(valid_packet)
    
    print(f"Replay Result: {res_replay}")
    
    success = False
    if res_replay['status'] == 'dropped' and "Timestamp Replay/Expired" in res_replay['reason']:
        print("✅ SUCCESS: Replay attack blocked by Sliding Window Timestamp.")
        success = True
    else:
        print(f"❌ FAILURE: Replay attack was NOT blocked correctly! Reason: {res_replay.get('reason', 'N/A')}")

    # Save results
    with open("replay_attack_results.txt", "w") as f:
        f.write(f"Replay Attack Test\n")
        f.write(f"Status: {'BLOCKED' if success else 'FAILED'}\n")
        f.write(f"Reason: {res_replay.get('reason', 'N/A')}\n")

if __name__ == "__main__":
    replay_attack_sim()
