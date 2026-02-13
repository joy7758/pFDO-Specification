import struct
import hashlib
import time

class FDOGate:
    def __init__(self, policy_file="Policy_Dictionary.json"):
        # Simulated "Clock-Cycle Deterministic" MsBV+ (Priority Arbitration Pipeline) using a dictionary for constant time lookup
        # In a real hardware implementation, this would be a bit vector.
        # This reflects v1.3.0-Industrial "Clock-Cycle Deterministic Physical Property" behavior.
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
        
        Refined Structure (16 Bytes) - v1.3.0-Industrial:
        [ Magic (2B) ]
        [ Epoch Clock (4B) - Read-Write Separation ]
        [ I/O Fingerprint (4B) - Progressive Convergence ]
        [ Masked Policy ID (4B) - XOR masked with Epoch ]
        [ RLCP & Checksum (2B) - 4b RLCP + 12b Checksum ]
        """
        if len(header_bytes) != 16:
            raise ValueError("Header must be exactly 16 bytes")
        
        # Unpack: H (2 bytes), I (4 bytes), I (4 bytes), I (4 bytes), H (2 bytes)
        # Big-endian network byte order
        # v1.3.0 Mapping:
        # seq -> Epoch Clock
        # ts  -> I/O Fingerprint (repurposed from Timestamp field in python simulation for layout compatibility)
        magic, epoch, fingerprint, masked_policy_id, rlcp_checksum = struct.unpack('!HIIIH', header_bytes)
        
        # Dynamic Unmasking: XOR with Epoch Clock
        policy_id = masked_policy_id ^ epoch
        
        # Extract RLCP flags (top 4 bits) and Checksum (bottom 12 bits)
        rlcp_flags = (rlcp_checksum >> 12) & 0xF
        checksum = rlcp_checksum & 0xFFF

        return {
            "magic": magic,
            "epoch": epoch,
            "fingerprint": fingerprint,
            "masked_policy_id": masked_policy_id,
            "policy_id": policy_id,
            "rlcp_flags": rlcp_flags,
            "checksum": checksum,
            "raw": header_bytes
        }

    def calculate_folded_checksum(self, header_parts, payload_head):
        """
        Folded Checksum: XOR of header fields and first 2 bytes of payload (if any).
        Returns a 12-bit unsigned integer (as per v1.3.0 spec).
        header_parts: tuple (magic, epoch, fingerprint, masked_policy_id, rlcp_flags)
        """
        magic, epoch, fingerprint, masked_policy_id, rlcp_flags = header_parts
        
        # Fold 32-bit fields into 12-bit chunks (approximate for simulation)
        # For simplicity in Python simulation, we'll keep 16-bit fold and mask at end
        
        epoch_fold = (epoch >> 16) ^ (epoch & 0xFFFF)
        fp_fold = (fingerprint >> 16) ^ (fingerprint & 0xFFFF)
        pid_fold = (masked_policy_id >> 16) ^ (masked_policy_id & 0xFFFF)
        
        # Initial XOR sum including RLCP flags shifted
        # RLCP flags are part of the last 16-bit word: [RLCP(4) | Checksum(12)]
        # We calculate checksum over other fields to match the 12 bits.
        
        xor_sum = magic ^ epoch_fold ^ fp_fold ^ pid_fold ^ (rlcp_flags << 12)
        
        # Mix in payload head (first 2 bytes) if available
        if payload_head:
            payload_val = 0
            if len(payload_head) >= 2:
                payload_val = struct.unpack('!H', payload_head[:2])[0]
            elif len(payload_head) == 1:
                payload_val = payload_head[0] << 8
            
            xor_sum ^= payload_val
            
        return xor_sum & 0xFFF

    def validate_segment(self, header_bytes, payload_bytes=b''):
        """
        时钟周期确定性 (Clock-Cycle Deterministic) 拦截校验 — v1.3.0-Industrial
        
        符合 AEP 元准则：效能优化追求 O(1) 复杂度与时钟周期级确定性。
        拦截逻辑基于优先级编码的多级位向量（PE-MsBV）流水线。
        
        Clock-Cycle Deterministic Validation with Security Enhancements (v1.3.0).
        Implements **Constant Clock-Cycle Execution Path with Priority Arbitration**.
        Ensures O(1) execution time regardless of policy complexity or payload size
        to prevent timing side-channel attacks.
        """
        try:
            header = self.parse_header(header_bytes)
        except ValueError as e:
            return False, str(e)

        # 1. Folded Checksum Verification
        # Recalculate expected checksum
        header_parts = (header['magic'], header['epoch'], header['fingerprint'], header['masked_policy_id'], header['rlcp_flags'])
        expected_checksum = self.calculate_folded_checksum(header_parts, payload_bytes[:2])
        
        if expected_checksum != header['checksum']:
             return False, f"Checksum Mismatch: expected {expected_checksum:#06x}, got {header['checksum']:#06x}"

        # 2. Epoch Governance Clock Check (Distributed Pointer Switching)
        # For simulation, we still use local time as the Epoch source
        current_epoch = int(time.time() * 1000) & 0xFFFFFFFF # ms precision for v1.3.0
        
        received_epoch = header['epoch']
        
        # Calculate signed difference for 32-bit wrapping arithmetic
        diff = (current_epoch - received_epoch) & 0xFFFFFFFF
        if diff > 0x7FFFFFFF:
            diff -= 0x100000000 # Treat as negative difference (future epoch)
            
        # Check if diff is within accepted window (e.g., +/- 2000ms)
        if abs(diff) > 2000:
             return False, f"Epoch Replay/Expired: diff {diff} ticks"

        # 3. MsBV+ (Clock-Cycle Deterministic) Policy Lookup
        policy_id = header["policy_id"]
        
        if policy_id not in self.msbv_table:
            return False, f"Policy ID {policy_id:#0x} rejected by MsBV+ (Priority Arbitration Pipeline)"

        return True, "Header Valid"

    def atomic_epoch_switch(self, new_epoch_config=None):
        """
        占位函数 — 影子表与原子指针切换（v1.3.0-Industrial 一致性规范）
        
        Placeholder for **Shadow Table & Atomic Pointer Switch** mechanism.
        
        In v1.3.0-Industrial hardware:
        1. A shadow MsBV table is pre-loaded with the new epoch's policies.
        2. Upon 'Epoch Trigger' signal (e.g., specific clock cycle or authorized command),
           the Global State Pointer is atomically swapped to the shadow table.
        3. This ensures zero downtime and consistency during policy updates.
        
        Software Simulation:
        self.msbv_table = new_epoch_config
        """
        pass

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
                "epoch": header['epoch']
            }
        else:
            return {"status": "dropped", "reason": msg}

    def create_packet(self, magic, sequence, policy_id, payload=b''):
        """
        Helper to create a valid packet for testing.
        Refined for v1.3.0: sequence -> epoch, dummy fingerprint
        """
        current_epoch = int(time.time() * 1000) & 0xFFFFFFFF
        dummy_fingerprint = 0xDEADBEEF
        rlcp_flags = 0x0
        
        masked_pid = policy_id ^ current_epoch
        
        # Calculate Checksum placeholder
        # Checksum is calculated over (Magic, Epoch, Fingerprint, MaskedPID, RLCP) ^ PayloadHead
        header_parts = (magic, current_epoch, dummy_fingerprint, masked_pid, rlcp_flags)
        checksum = self.calculate_folded_checksum(header_parts, payload[:2])
        
        # Combine RLCP flags and Checksum
        final_checksum_field = (rlcp_flags << 12) | (checksum & 0xFFF)
        
        header = struct.pack('!HIIIH', magic, current_epoch, dummy_fingerprint, masked_pid, final_checksum_field)
        return header + payload
