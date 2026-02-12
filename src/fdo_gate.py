import struct
import hashlib
import time

class FDOGate:
    def __init__(self, policy_file="Policy_Dictionary.json"):
        # Simulated O(1) MsBV (Multistate Bit Vector) using a dictionary for constant time lookup
        # In a real hardware implementation, this would be a bit vector.
        self.msbv_table = {
            # Policy ID (int) -> Allowed Security Level (int)
            0x01: 0, # Public
            0x02: 1, # Restricted
            0x03: 2, # Confidential
            0x04: 3  # Top Secret
        }
        self.default_security_level = 0

    def parse_header(self, header_bytes):
        """
        Parses the 16-byte fixed header based on RFC 8200 alignment and Active Governance specs.
        
        Refined Structure (16 Bytes):
        [ Magic (2B) ]
        [ Sequence ID (4B) ]
        [ Timestamp (4B) - 100ns precision ]
        [ Masked Policy ID (4B) - XOR masked with Seq ID ]
        [ Checksum (2B) - Folded XOR ]
        """
        if len(header_bytes) != 16:
            raise ValueError("Header must be exactly 16 bytes")
        
        # Unpack: H (2 bytes), I (4 bytes), I (4 bytes), I (4 bytes), H (2 bytes)
        # Big-endian network byte order
        magic, seq, ts, masked_policy_id, checksum = struct.unpack('!HIIIH', header_bytes)
        
        # Dynamic Unmasking: XOR with Sequence ID
        policy_id = masked_policy_id ^ seq
        
        return {
            "magic": magic,
            "sequence": seq,
            "timestamp": ts,
            "masked_policy_id": masked_policy_id,
            "policy_id": policy_id,
            "checksum": checksum,
            "raw": header_bytes
        }

    def calculate_folded_checksum(self, header_parts, payload_head):
        """
        Folded Checksum: XOR of header fields and first 2 bytes of payload (if any).
        Returns a 16-bit unsigned integer.
        header_parts: tuple (magic, seq, ts, masked_policy_id)
        """
        magic, seq, ts, masked_policy_id = header_parts
        
        # Fold 32-bit fields into 16-bit chunks
        # Seq (32) -> High16 ^ Low16
        seq_fold = (seq >> 16) ^ (seq & 0xFFFF)
        ts_fold = (ts >> 16) ^ (ts & 0xFFFF)
        pid_fold = (masked_policy_id >> 16) ^ (masked_policy_id & 0xFFFF)
        
        # Initial XOR sum
        xor_sum = magic ^ seq_fold ^ ts_fold ^ pid_fold
        
        # Mix in payload head (first 2 bytes) if available
        if payload_head:
            payload_val = 0
            if len(payload_head) >= 2:
                payload_val = struct.unpack('!H', payload_head[:2])[0]
            elif len(payload_head) == 1:
                payload_val = payload_head[0] << 8
            
            xor_sum ^= payload_val
            
        return xor_sum & 0xFFFF

    def validate_segment(self, header_bytes, payload_bytes=b''):
        """
        O(1) Validation with Security Enhancements.
        """
        try:
            header = self.parse_header(header_bytes)
        except ValueError as e:
            return False, str(e)

        # 1. Folded Checksum Verification
        # Recalculate expected checksum
        header_parts = (header['magic'], header['sequence'], header['timestamp'], header['masked_policy_id'])
        expected_checksum = self.calculate_folded_checksum(header_parts, payload_bytes[:2])
        
        if expected_checksum != header['checksum']:
             return False, f"Checksum Mismatch: expected {expected_checksum:#06x}, got {header['checksum']:#06x}"

        # 2. Sliding Window Timestamp Check (100ns precision, +/- 2s window)
        # Current time in 100ns ticks
        current_time_ns = int(time.time() * 1e7)
        # The timestamp in header is 32-bit, so it wraps around.
        # Window size: 2 seconds = 20,000,000 ticks.
        # We need to handle wrap-around comparison.
        
        # Simple window check assuming 'timestamp' is the lower 32 bits of the epoch 100ns ticks
        # Calculate difference considering overflow
        # diff = (current - received) & 0xFFFFFFFF
        # This is tricky with raw modulo arithmetic. A better way for signed distance:
        
        current_ts_32 = current_time_ns & 0xFFFFFFFF
        received_ts_32 = header['timestamp']
        
        # Calculate signed difference for 32-bit wrapping arithmetic
        diff = (current_ts_32 - received_ts_32) & 0xFFFFFFFF
        if diff > 0x7FFFFFFF:
            diff -= 0x100000000 # Treat as negative difference (future timestamp)
            
        # Check if diff is within +/- 2 seconds (20,000,000 ticks)
        # Note: In a real system, you might want stricter checks for future timestamps.
        # Here we allow +/- 2s window.
        if abs(diff) > 20000000:
             return False, f"Timestamp Replay/Expired: diff {diff} ticks"

        # 3. MsBV O(1) Policy Lookup
        policy_id = header["policy_id"]
        
        if policy_id not in self.msbv_table:
            return False, f"Policy ID {policy_id:#0x} rejected by MsBV"

        return True, "Header Valid"

    def process_packet(self, packet_bytes):
        if len(packet_bytes) < 16:
            return {"status": "dropped", "reason": "Packet too short"}
        
        header_bytes = packet_bytes[:16]
        payload = packet_bytes[16:]
        
        is_valid, msg = self.validate_segment(header_bytes, payload)
        
        if is_valid:
            # Re-parse to get policy ID for return
            header = self.parse_header(header_bytes)
            return {
                "status": "forwarded", 
                "policy_id": header['policy_id'],
                "timestamp": header['timestamp']
            }
        else:
            return {"status": "dropped", "reason": msg}

    def create_packet(self, magic, sequence, policy_id, payload=b''):
        """
        Helper to create a valid packet for testing.
        """
        current_ts = int(time.time() * 1e7) & 0xFFFFFFFF
        masked_pid = policy_id ^ sequence
        
        # Calculate Checksum placeholder
        # Checksum is calculated over (Magic, Seq, TS, MaskedPID) ^ PayloadHead
        header_parts = (magic, sequence, current_ts, masked_pid)
        checksum = self.calculate_folded_checksum(header_parts, payload[:2])
        
        header = struct.pack('!HIIIH', magic, sequence, current_ts, masked_pid, checksum)
        return header + payload
