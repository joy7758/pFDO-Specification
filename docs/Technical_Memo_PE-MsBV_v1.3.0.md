# TECHNICAL MEMORANDUM
A-FDO v1.3.0-Industrial | Reference: `src/fdo_gate.py`, `docs/White_Paper.md`

**TO:** Peter Wittenburg  
**FROM:** FDO Project Team  
**DATE:** February 2025  
**SUBJECT:** Shadow Table Implementation and PE-MsBV Physical-Layer Determinism  
**REF:** v1.3.0-Industrial specification; `src/fdo_gate.py`; `docs/White_Paper.md`

---

**1. Purpose**

This memorandum explains (1) the **implementation of Shadow Tables** in the A-FDO v1.3.0-Industrial reference implementation and (2) how **PE-MsBV eliminates data-dependent branching** to ensure **physical-layer determinism**. All references are to the code in `src/fdo_gate.py` and the class `FDOGate`. It is intended for use as a technical attachment in support of evaluator sovereignty and auditability.

---

**2. Shadow Table Implementation**

Policy updates must not block in-flight validation or introduce read-write races. The **Shadow Table and Atomic Pointer Swap** is implemented by **`atomic_epoch_switch(self, new_epoch_config=None)`** in `fdo_gate.py`.

**Mechanism:** The gate maintains an active arbitration table (`self.msbv_table`) used by **`validate_segment`** for the Stage 3 PE-MsBV lookup. When a new policy set is to be applied, the caller supplies it as `new_epoch_config`. The method **atomically replaces** the active table with the new configuration (in the reference implementation, by assigning `self._active_msbv` and `self.msbv_table` to a new dictionary built from `new_epoch_config`). There is no mutex over the segment path: validation always reads from the current `self.msbv_table`, and the update is a single reference assignment, so no validation sees a half-updated table. **Zero downtime** is achieved because the swap is instantaneous and the execution path remains branch-entropy-free.

**Zero-jitter updates in high-rate environments:** The **atomic pointer swap** (single reference assignment) ensures that in a 100G (or higher) network environment, policy rollouts introduce **zero packet-time jitter**: no lock acquisition, no gradual migration, and no per-packet conditional logic. Every segment either observes the previous table or the new table in full; there is no intermediate state. Thus the design delivers **zero-jitter updates** at line rate, preserving constant latency and determinism across the transition.

**Consistency:** Reads (all three stages of `validate_segment`) and the write (assignment in `atomic_epoch_switch`) are disjoint in time at the level of the pointer swap; thus the design satisfies the requirement for Epoch-based shadow-table switch logic without locking the data path.

---

**3. PE-MsBV and Elimination of Data-Dependent Branching**

**Physical-layer determinism** means that the execution time and the sequence of operations for validating a segment do not depend on the *content* of the segment (beyond the fixed parsing and the fixed number of comparisons). PE-MsBV achieves this by **eliminating data-dependent branching** in the arbitration path.

**Stage 1 (Folded Checksum):** One call to **`calculate_folded_checksum(header_parts, payload_bytes[:2])`** and one comparison with `header['checksum']`. The checksum is a constant-depth XOR tree over a fixed number of inputs (five header components plus at most 2 bytes); the branch "match / mismatch" does not depend on policy count or payload length. Either the segment is discarded or it proceeds; the path length is fixed.

**Stage 2 (Epoch Sync):** The epoch difference is computed with fixed 32-bit arithmetic; one comparison against the ±2000 ms window. No loops; no branches that vary with policy or payload.

**Stage 3 (PE-MsBV Lookup):** A single membership test **`policy_id in self.msbv_table`**. In the reference implementation this is an O(1) dictionary lookup. The outcome (allow or reject) does not change the *number* of operations performed: one lookup, one conditional return. There are no cascaded conditionals or loops over the policy set. Thus the **branch entropy**—the variability of control flow that could leak information via timing—is eliminated: every segment undergoes exactly the same operation count and the same logical pipeline (Checksum → EpochSync → PE-MsBV), regardless of whether it passes or fails and regardless of policy ID or table size.

This design ensures that **determinism** holds at the physical layer (fixed cycle count in a hardware realization) and supports **evaluator sovereignty** (auditability and non-bypassability without vendor- or CPU-specific assumptions).

---

**4. Alignment with Reference Code**

| Concept | Implementation in `src/fdo_gate.py` |
|--------|--------------------------------------|
| Shadow Table & Atomic Pointer Swap | `atomic_epoch_switch(new_epoch_config)` assigns `self._active_msbv` and `self.msbv_table` |
| Stage 1 (12-bit RLCP integrity) | `calculate_folded_checksum(header_parts, payload_bytes[:2])` vs `header['checksum']` |
| Stage 2 (Epoch Sync ±2000 ms) | `abs(diff) > 2000` → reject |
| Stage 3 (PE-MsBV O(1) arbitration) | `policy_id in self.msbv_table` |
| Branch-entropy-free path | No loops or data-dependent branch depth in `validate_segment` |

---

**5. Closure**

This memorandum reflects the v1.3.0-Industrial architecture as implemented in `src/fdo_gate.py`. For full specification and terminology, see `docs/White_Paper.md` and the project root `.cursorrules`.

*Document classification: Technical attachment. Formal Technical English.*
