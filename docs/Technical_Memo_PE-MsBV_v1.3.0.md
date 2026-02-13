# Technical Memorandum

**To:** Peter Wittenburg  
**From:** FDO Project Team  
**Date:** February 2025  
**Subject:** PE-MsBV O(1) Implementation and Shadow Table Switch Logic (v1.3.0-Industrial)  
**Ref:** `src/fdo_gate.py`, `docs/White_Paper.md`

---

## 1. Purpose

This memo summarizes the **O(1) implementation** of the PE-MsBV (Priority-Encoded Multi-stage Bit Vector) interception pipeline and the **Shadow Table** (Atomic Epoch Switch) logic in the A-FDO v1.3.0-Industrial reference implementation. All references are to the code in `src/fdo_gate.py` and the class `FDOGate`.

---

## 2. O(1) Implementation Principle

Validation is performed by **`validate_segment(self, header_bytes, payload_bytes=b'')`**. It runs exactly three stages in sequence; each stage has constant time and fixed logic path:

- **Stage 1 (Checksum):** One call to **`calculate_folded_checksum(self, header_parts, payload_head)`** and one comparison. No loops; input size is fixed (header_parts tuple and at most 2 bytes of payload).
- **Stage 2 (Epoch):** Epoch difference is computed with fixed 32-bit arithmetic; one comparison against the ±2000 ms window. No dependency on policy count or payload length.
- **Stage 3 (PE-MsBV):** One dictionary membership test: **`policy_id in self.msbv_table`**. In the reference implementation this is O(1); in hardware the same would be a fixed-depth bit-vector or table lookup.

The total execution path length is therefore independent of the number of policies and the payload size. This satisfies the AEP requirement for **clock-cycle-level determinism** and mitigates timing side-channel leakage.

---

## 3. Shadow Table (Atomic Epoch Switch) Logic

Policy updates must not block or stall in-flight validation. The **Atomic Epoch Switch** is modeled by the placeholder **`atomic_epoch_switch(self, new_epoch_config=None)`** in `fdo_gate.py`:

1. **Shadow table:** A second MsBV table (shadow) is prepared with the new epoch’s policy set. The active table (e.g. `self.msbv_table`) continues to serve all read traffic (calls to `validate_segment` and thus `policy_id in self.msbv_table`) until the switch.
2. **Atomic pointer swap:** On an Epoch Trigger (e.g. clock cycle or authorized command), the global state pointer is switched in a single atomic step from the current active table to the shadow table. The previous shadow becomes the new active table; the old active table can be retired or reused as the next shadow.
3. **Consistency:** Writes (loading new policies) apply only to the inactive shadow. Reads (validation) use only the active table. Thus read and write sets are disjoint at any time; no locks or blocking are required for consistency, and **zero downtime** is achieved at the moment of the swap.

In the current software placeholder, the intended simulation is to assign the new configuration to the active table when the function is implemented (e.g. `self.msbv_table = new_epoch_config` or a copy thereof), possibly after validation of the new config.

---

## 4. Alignment with Reference Code

| Concept | Implementation in `src/fdo_gate.py` |
|--------|--------------------------------------|
| Three-stage validation | `validate_segment(header_bytes, payload_bytes)` |
| Stage 1 | `calculate_folded_checksum(header_parts, payload_bytes[:2])` vs `header['checksum']` |
| Stage 2 | `abs(diff) > 2000` → reject |
| Stage 3 | `policy_id in self.msbv_table` |
| PE-MsBV table | `self.msbv_table` |
| Atomic Epoch Switch | `atomic_epoch_switch(new_epoch_config=None)` |

---

*This memo reflects the v1.3.0-Industrial architecture as implemented in `src/fdo_gate.py`.*
