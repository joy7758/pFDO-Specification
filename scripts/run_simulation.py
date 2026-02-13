import subprocess
import json
import time
import os
import sys

def send_request(proc, method, params=None, req_id=1):
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "id": req_id
    }
    if params:
        request["params"] = params
    
    json_req = json.dumps(request)
    print(f"DEBUG SEND: {json_req}") # Uncomment for debug
    proc.stdin.write(json_req + "\n")
    proc.stdin.flush()
    
    response_line = proc.stdout.readline()
    print(f"DEBUG RECV: {response_line}") # Uncomment for debug
    if not response_line:
        raise Exception("Server closed connection")
    
    return json.loads(response_line)

def run_simulation():
    print(">>> Starting Active FDO Defense Simulation (MCP Mode)...")
    
    server_script = "mcp_server.py"
    # Use path relative to this script file to ensure it works from any working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # The new location is FDO_Project/src
    server_dir = os.path.abspath(os.path.join(script_dir, "../src"))
    
    # Ensure server directory exists
    if not os.path.exists(server_dir):
         print(f"Error: Server directory not found at {server_dir}")
         return

    # Start the MCP Server process
    proc = subprocess.Popen(
        [sys.executable, server_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr, # Pass stderr through to see logs
        text=True,
        cwd=server_dir # Run in server dir
    )
    
    try:
        # 1. Initialize
        print("\n[1] Initializing MCP Server Connection...")
        resp = send_request(proc, "initialize", req_id=1)
        print(f"Server Info: {json.dumps(resp['result']['serverInfo'], indent=2)}")
        
        # 2. List Tools
        print("\n[2] Discovering Defense Capabilities (Tools)...")
        resp = send_request(proc, "tools/list", req_id=2)
        tools = [t['name'] for t in resp['result']['tools']]
        print(f"Available Tools: {tools}")
        
        # 3. Valid Traffic Simulation
        print("\n[3] Simulating Legitimate Traffic (Policy: Public)...")
        # Create a valid packet
        create_args = {
            "name": "create_packet",
            "arguments": {
                "magic": 0xFD01,
                "sequence": 1001,
                "policy_id": 0x01, # Public
                "payload_hex": "48656c6c6f" # "Hello"
            }
        }
        resp = send_request(proc, "tools/call", params=create_args, req_id=3)
        
        if 'error' in resp:
            print(f"Error in create_packet: {resp['error']}")
            return

        # The result content text is just the hex string, NOT a JSON string.
        packet_hex = resp['result']['content'][0]['text']
        print(f"Generated Packet: {packet_hex[:32]}...")
        
        # Validate it
        header_hex = packet_hex[:32] # 16 bytes = 32 hex chars
        payload_hex = packet_hex[32:]
        
        validate_args = {
            "name": "validate_segment",
            "arguments": {
                "header_hex": header_hex,
                "payload_hex": payload_hex
            }
        }
        resp = send_request(proc, "tools/call", params=validate_args, req_id=4)
        result = json.loads(resp['result']['content'][0]['text'])
        print(f"Defense Result: {result}")
        if result['valid']:
            print("✅ Legitimate traffic passed.")
        else:
            print("❌ Legitimate traffic failed!")

        # 4. Tampering Attack Simulation
        print("\n[4] Simulating Man-in-the-Middle Tampering Attack...")
        # Modify the payload
        tampered_payload_hex = payload_hex.replace("48", "49", 1) # Change 'H' to 'I'
        print(f"Tampered Payload: {tampered_payload_hex}")
        
        validate_args['arguments']['payload_hex'] = tampered_payload_hex
        resp = send_request(proc, "tools/call", params=validate_args, req_id=5)
        result = json.loads(resp['result']['content'][0]['text'])
        print(f"Defense Result: {result}")
        if not result['valid'] and "Checksum Mismatch" in result['message']:
             print("🛡️ Attack Blocked: Tampering detected via Folded Checksum.")
        else:
             print("❌ Attack Failed to be blocked!")

        # 5. Policy Violation Simulation
        print("\n[5] Simulating Unauthorized Access (Policy Violation)...")
        # Create packet with Top Secret policy (0x04) but using Public credentials (simulated by just generating it, but let's see if we can trigger MSBV rejection if we use an invalid ID not in table)
        
        # The current gate implementation accepts 0x01-0x04. Let's use 0x05 (Unknown/Illegal)
        create_args['arguments']['policy_id'] = 0x05
        # We need to manually construct this because create_packet might just create it.
        # But wait, create_packet doesn't validate policy existence, it just packs it.
        # So we create a packet with ID 0x05
        resp = send_request(proc, "tools/call", params=create_args, req_id=6)
        bad_packet_hex = resp['result']['content'][0]['text']
        
        header_hex = bad_packet_hex[:32]
        payload_hex = bad_packet_hex[32:]
        
        validate_args['arguments']['header_hex'] = header_hex
        validate_args['arguments']['payload_hex'] = payload_hex
        
        resp = send_request(proc, "tools/call", params=validate_args, req_id=7)
        result = json.loads(resp['result']['content'][0]['text'])
        print(f"Defense Result: {result}")
        if not result['valid'] and "rejected by MsBV" in result['message']:
            print("🛡️ Attack Blocked: Unknown Policy ID rejected by Priority Arbitration Pipeline (MsBV+).")
        else:
             print("❌ Policy check failed!")

    except Exception as e:
        print(f"Simulation Error: {e}")
    finally:
        proc.stdin.close()
        proc.terminate()
        proc.wait()
        print("\n>>> Simulation Complete.")

if __name__ == "__main__":
    run_simulation()
