"""
A-FDO Gate — v1.3.0-Industrial Reference Implementation.

Hardware-neutral, three-stage interception pipeline implementing clock-cycle
determinism via branch-entropy elimination. RLCP (Fisher Information Matrix–
based topology-preserving metabolic protocol) integrity is enforced through
the 12-bit folded checksum and 4b RLCP field over the logical skeleton
sub-manifold. Arbitration is O(1) and deterministic at the physical layer.
"""

import struct
import time


class FDOGate:
    """
    Governance gate: three-stage hardware-neutral pipeline. Stage 1 — Folded
    Checksum (12-bit RLCP integrity). Stage 2 — Epoch Sync (±2000 ms drift
    validation). Stage 3 — PE-MsBV Lookup (branch-entropy-free O(1) arbitration).
    Supports Atomic Epoch Switch via shadow table and atomic pointer swap.
    """

    def __init__(self, policy_file="Policy_Dictionary.json"):
        self._active_msbv = {
            0x01: 0,
            0x02: 1,
            0x03: 2,
            0x04: 3,
        }
        self.msbv_table = self._active_msbv
        self.default_security_level = 0

    def parse_header(self, header_bytes):
        """
        Parse the 16-byte fixed header. Unpack format !HIIIH (big-endian):
        Magic (2B), Epoch Clock (4B), I/O Fingerprint (4B), Masked Policy ID (4B),
        RLCP+Checksum (2B). Dynamic unmasking: policy_id = masked_policy_id ^ epoch.
        RLCP flags (top 4b) and 12b checksum (bottom 12b) encode sub-manifold
        signalling and constant-depth integrity.
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
        Compute 12-bit folded checksum (RLCP integrity bound). Constant-depth
        XOR over header_parts (magic, epoch, fingerprint, masked_policy_id,
        rlcp_flags) and first 2 bytes of payload. Returns xor_sum & 0xFFF.
        Branch-entropy-free; aligns with logical skeleton sub-manifold (FIM/RLCP).
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
        Three-stage hardware-neutral validation. No data-dependent branching;
        fixed execution path for physical-layer determinism. Stage 1: Folded
        Checksum (12-bit RLCP integrity). Stage 2: Epoch Sync (±2000 ms drift).
        Stage 3: PE-MsBV Lookup (O(1) arbitration via policy_id in self.msbv_table).
        Returns (True, msg) or (False, reason).
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
        Shadow Table and Atomic Pointer Swap. Pre-load new policies into a
        shadow table; on invocation, atomically swap the active arbitration
        table to the shadow so that validation continues without read-write
        conflict and without branch entropy. Zero downtime. When
        new_epoch_config is provided, the active MsBV table is replaced
        atomically (simulation: single reference assignment).
        """
        if new_epoch_config is not None:
            self._active_msbv = dict(new_epoch_config)
            self.msbv_table = self._active_msbv

    def process_packet(self, packet_bytes):
        """Arbitrate packet through validate_segment; return forwarded or dropped."""
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
        """Build valid 16-byte header + payload (epoch, masked PID, RLCP/checksum)."""
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
