# Technical Memorandum

**To:** Technical Stakeholders  
**From:** FDO Project Team  
**Date:** February 2025  
**Subject:** PE-MsBV Pipelined O(1) Interception & I/O Fingerprint Convergence  
**Ref:** v1.3.0-Industrial, `docs/White_Paper.md`, `src/fdo_gate.py`

---

## 1. Purpose

This memo summarizes the v1.3.0-Industrial implementation of the **PE-MsBV** (Priority-Encoded Multi-stage Bit Vector) interception pipeline, the **12-bit Folded Checksum** and its physical meaning, and the **Epoch Switch** shadow-table logic. All descriptions are aligned with the reference implementation in `src/fdo_gate.py` and the class `FDOGate`.

---

## 2. PE-MsBV Three-Stage Pipeline

The interception pipeline is implemented in `src/fdo_gate.py` by the method **`validate_segment(self, header_bytes, payload_bytes=b'')`**. It executes exactly three stages in sequence; each stage is O(1), so the overall validation is **clock-cycle deterministic** and independent of policy count and payload size.

### Stage 1 — Folded Checksum Verification

- The gate recomputes the expected checksum by calling **`calculate_folded_checksum(self, header_parts, payload_head)`** with `header_parts` built from the parsed header (`magic`, `epoch`, `fingerprint`, `masked_policy_id`, `rlcp_flags`) and `payload_head` set to `payload_bytes[:2]`.
- The result is compared to `header['checksum']`. On mismatch, `validate_segment` returns `(False, "Checksum Mismatch: ...")` and the segment is discarded.

### Stage 2 — Epoch Window Validation

- The gate computes the signed difference `diff` between the current epoch (`int(time.time() * 1000) & 0xFFFFFFFF`) and `header['epoch']`, with 32-bit wrapping handled for overflow.
- If `abs(diff) > 2000`, the segment is treated as replay or expired; `validate_segment` returns `(False, "Epoch Replay/Expired: ...")`. Otherwise the segment is within the ±2000 ms window and proceeds to Stage 3.

### Stage 3 — PE-MsBV Policy Lookup

- The gate obtains `policy_id` from `header["policy_id"]` (after dynamic unmasking in **`parse_header(self, header_bytes)`**: `policy_id = masked_policy_id ^ epoch`).
- A single O(1) lookup is performed: **`policy_id in self.msbv_table`**. The table is the MsBV+ (Priority Arbitration Pipeline); in `fdo_gate.py` it is implemented as a dictionary. If the policy ID is not present, `validate_segment` returns `(False, "...rejected by MsBV+ (Priority Arbitration Pipeline)")`; otherwise it returns `(True, "Header Valid")`.

Entry to the pipeline is via **`process_packet(self, packet_bytes)`**, which extracts the 16-byte header, calls `validate_segment(header_bytes, payload)`, and returns either a forwarded result (with `policy_id` and `epoch`) or a dropped result with reason.

---

## 3. 12-bit Folded Checksum — Physical Meaning

The **12-bit Folded Checksum** is computed by **`calculate_folded_checksum(self, header_parts, payload_head)`** in `src/fdo_gate.py`. Its role is integrity and binding of the header to the leading bytes of the payload.

- **Inputs:** `header_parts` is a tuple `(magic, epoch, fingerprint, masked_policy_id, rlcp_flags)`; `payload_head` is the first 2 bytes of the segment payload (or empty).
- **Algorithm:** 32-bit fields are folded (e.g. `epoch_fold = (epoch >> 16) ^ (epoch & 0xFFFF)`), then combined with `magic` and shifted `rlcp_flags` into an XOR sum. The first 2 bytes of the payload (if present) are mixed in. The final value is **`xor_sum & 0xFFF`**, i.e. a 12-bit unsigned integer.
- **Physical meaning:** The checksum binds the fixed-length header and the start of the payload in a single, fixed-width value. It is stored in the bottom 12 bits of the last 16-bit word of the header (the top 4 bits hold RLCP flags). In hardware, this design supports a **constant-depth XOR tree**: the same number of operations regardless of policy set or payload length, preserving O(1) determinism and avoiding timing side channels. Verification is a single recompute-and-compare step in Stage 1.

---

## 4. Epoch Switch — Shadow-Table Logic

The **Atomic Epoch Switch** is specified as a shadow-table and atomic pointer swap. In `src/fdo_gate.py` it is represented by the placeholder **`atomic_epoch_switch(self, new_epoch_config=None)`** on the class `FDOGate`.

- **Shadow table:** A second MsBV table (in hardware or in simulation) is pre-loaded with the new epoch’s policies. The active table (e.g. `self.msbv_table`) continues to serve read traffic (packet validation via `validate_segment`) until the switch.
- **Atomic pointer swap:** On an Epoch Trigger (e.g. a specific clock cycle or an authorized command), the global state pointer is atomically switched from the current active table to the shadow table. The previous shadow becomes the new active table.
- **Consistency:** Read operations (validation) and write operations (policy load) are disjoint: updates apply only to the inactive shadow, so there is no race between validation and policy rollouts. Zero downtime is achieved by the single atomic swap. In the current software placeholder, the intended behavior is to assign the new configuration to `self.msbv_table` when the function is implemented (e.g. `self.msbv_table = new_epoch_config` or a copy thereof).

---

## 5. I/O Fingerprint Convergence

The header includes a 4-byte **I/O Fingerprint** field, supporting the AEP requirement for a **Progressive Convergence I/O Fingerprint**. The test script **`scripts/test_io_fingerprint.py`** validates that under simulated noisy conditions, the system exhibits convergence (e.g. bounded variance, noise below threshold). This aligns with the white paper and with the use of the fingerprint field in the 16-byte layout parsed by **`parse_header`** in `fdo_gate.py`.

---

## 6. File and Symbol Alignment

| Concept | File / Symbol in `src/fdo_gate.py` |
|--------|------------------------------------|
| Gate class | `FDOGate` |
| 16-byte header parsing | `parse_header(self, header_bytes)` |
| 12-bit folded checksum | `calculate_folded_checksum(self, header_parts, payload_head)` |
| Three-stage validation | `validate_segment(self, header_bytes, payload_bytes=b'')` |
| PE-MsBV table | `self.msbv_table` |
| Atomic Epoch Switch | `atomic_epoch_switch(self, new_epoch_config=None)` |
| Packet entry point | `process_packet(self, packet_bytes)` |
| Test packet construction | `create_packet(self, magic, sequence, policy_id, payload=b'')` |

---

*This memo is consistent with `docs/White_Paper.md` and the v1.3.0-Industrial codebase in `src/fdo_gate.py`.*
