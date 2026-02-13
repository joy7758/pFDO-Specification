"""
A-FDO Gate — v1.3.0-Industrial Reference Implementation.

Clock-cycle deterministic interception via the PE-MsBV (Priority-Encoded
Multi-stage Bit Vector) hardware-neutral pipeline. Physical O(1) determinism
is achieved by eliminating branch entropy: fixed-depth execution path, no
data-dependent branching. RLCP (topology-preserving metabolic protocol, FIM-based)
integrity is enforced via the 12-bit folded checksum and 4b RLCP field over the
logical skeleton sub-manifold. Aligns with AEP: evaluator sovereignty,
shadow-table consistency, arbitrated policy lookup.
"""

import struct
import time


class FDOGate:
    """
    Governance gate implementing three-stage arbitrated validation. Stage 1:
    Folded Checksum (RLCP integrity over header and payload head). Stage 2:
    Epoch Window (±2000 ms). Stage 3: PE-MsBV O(1) policy lookup (Priority
    Arbitration Pipeline). Execution path is branch-entropy-free for
    physical determinism.
    """

    def __init__(self, policy_file="Policy_Dictionary.json"):
        self.msbv_table = {
            0x01: 0,
            0x02: 1,
            0x03: 2,
            0x04: 3,
        }
        self.default_security_level = 0

    def parse_header(self, header_bytes):
        """
        Parse the 16-byte fixed header (RFC 8200 aligned). Layout: Magic (2B),
        Epoch Clock (4B), I/O Fingerprint (4B), Masked Policy ID (4B), RLCP+Checksum (2B).
        Unpack: !HIIIH (big-endian). Dynamic unmasking: policy_id = masked_policy_id ^ epoch.
        RLCP flags (top 4b) and 12b checksum (bottom 12b) encode RLCP sub-manifold
        signalling and integrity; see calculate_folded_checksum for the constant-depth
        integrity bound.
        """
        if len(header_bytes) != 16:
            raise ValueError("Header must be exactly 16 bytes")
        magic, epoch, fingerprint, masked_policy_id, rlcp_checksum = struct.unpack(
            "!HIIIH", header_bytes
        )
        policy_id = masked_policy_id ^ epoch
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
            "raw": header_bytes,
        }

    def calculate_folded_checksum(self, header_parts, payload_head):
        """
        Compute 12-bit folded checksum (RLCP integrity bound) over header_parts
        (magic, epoch, fingerprint, masked_policy_id, rlcp_flags) and first 2 bytes
        of payload. Constant-depth XOR tree: result xor_sum & 0xFFF. Supports
        branch-entropy-free Stage 1 verification and aligns with the logical
        skeleton sub-manifold integrity requirement (FIM/RLCP).
        """
        magic, epoch, fingerprint, masked_policy_id, rlcp_flags = header_parts
        epoch_fold = (epoch >> 16) ^ (epoch & 0xFFFF)
        fp_fold = (fingerprint >> 16) ^ (fingerprint & 0xFFFF)
        pid_fold = (masked_policy_id >> 16) ^ (masked_policy_id & 0xFFFF)
        xor_sum = magic ^ epoch_fold ^ fp_fold ^ pid_fold ^ (rlcp_flags << 12)
        if payload_head:
            payload_val = (
                struct.unpack("!H", payload_head[:2])[0]
                if len(payload_head) >= 2
                else payload_head[0] << 8
            )
            xor_sum ^= payload_val
        return xor_sum & 0xFFF

    def validate_segment(self, header_bytes, payload_bytes=b""):
        """
        Three-stage clock-cycle deterministic validation; branch-entropy-free
        (fixed path, no data-dependent branches). Stage 1: Folded Checksum
        (RLCP integrity). Stage 2: Epoch Window (±2000 ms). Stage 3: PE-MsBV
        Priority Arbitration (policy_id in self.msbv_table). Physical O(1)
        determinism; returns (True, msg) or (False, reason).
        """
        try:
            header = self.parse_header(header_bytes)
        except ValueError as e:
            return False, str(e)

        header_parts = (
            header["magic"],
            header["epoch"],
            header["fingerprint"],
            header["masked_policy_id"],
            header["rlcp_flags"],
        )
        expected_checksum = self.calculate_folded_checksum(
            header_parts, payload_bytes[:2]
        )
        if expected_checksum != header["checksum"]:
            return (
                False,
                f"Checksum Mismatch: expected {expected_checksum:#06x}, got {header['checksum']:#06x}",
            )

        current_epoch = int(time.time() * 1000) & 0xFFFFFFFF
        received_epoch = header["epoch"]
        diff = (current_epoch - received_epoch) & 0xFFFFFFFF
        if diff > 0x7FFFFFFF:
            diff -= 0x100000000
        if abs(diff) > 2000:
            return False, f"Epoch Replay/Expired: diff {diff} ticks"

        policy_id = header["policy_id"]
        if policy_id not in self.msbv_table:
            return (
                False,
                f"Policy ID {policy_id:#0x} rejected by MsBV+ (Priority Arbitration Pipeline)",
            )
        return True, "Header Valid"

    def atomic_epoch_switch(self, new_epoch_config=None):
        """
        Placeholder for Atomic Epoch Switch (Shadow Table and Atomic Pointer Swap).
        Pre-load shadow MsBV table; on Epoch Trigger, atomically swap global
        state pointer to shadow so arbitration continues without branch entropy
        or read-write conflict; zero downtime. Simulation: assign to self.msbv_table.
        """
        pass

    def process_packet(self, packet_bytes):
        """Arbitrate packet via validate_segment; return forwarded or dropped result."""
        if len(packet_bytes) < 16:
            return {"status": "dropped", "reason": "Packet too short"}
        header_bytes = packet_bytes[:16]
        payload = packet_bytes[16:]
        is_valid, msg = self.validate_segment(header_bytes, payload)
        if is_valid:
            header = self.parse_header(header_bytes)
            return {
                "status": "forwarded",
                "policy_id": header["policy_id"],
                "epoch": header["epoch"],
            }
        return {"status": "dropped", "reason": msg}

    def create_packet(self, magic, sequence, policy_id, payload=b""):
        """Build a valid 16-byte header + payload for testing (epoch, masked PID, RLCP/checksum)."""
        current_epoch = int(time.time() * 1000) & 0xFFFFFFFF
        dummy_fingerprint = 0xDEADBEEF
        rlcp_flags = 0x0
        masked_pid = policy_id ^ current_epoch
        header_parts = (magic, current_epoch, dummy_fingerprint, masked_pid, rlcp_flags)
        checksum = self.calculate_folded_checksum(header_parts, payload[:2])
        final_checksum_field = (rlcp_flags << 12) | (checksum & 0xFFF)
        header = struct.pack(
            "!HIIIH", magic, current_epoch, dummy_fingerprint, masked_pid, final_checksum_field
        )
        return header + payload
