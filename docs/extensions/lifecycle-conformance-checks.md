# Minimal Conformance Checks for Evidence-Driven Lifecycle Governance

## 1. Purpose

This document is not a complete test suite. It defines only the minimum verifiable assertions needed to evaluate record structure, vocabulary validity, and basic lifecycle consistency for Evidence-Driven Lifecycle Adjustment profiles.

## 2. Conformance Targets

- **state vocabulary validity:** lifecycle states use the defined minimal vocabulary.
- **remediation status validity:** remediation outcomes use the defined minimal vocabulary.
- **required timestamp format:** review timestamps are serializable in a standard machine-readable form.
- **allowed transition path checks:** represented transitions follow the bounded minimal state model.
- **evidence reference shape checks:** evidence references preserve a minimally reviewable string form.

## 3. Minimal Assertions

1. A lifecycle governance record MUST contain `object_id`.
2. A lifecycle governance record MUST contain `lifecycle_state`.
3. `lifecycle_state` MUST be one of `Declared`, `Active`, `Restricted`, `Suspended`, `Recoverable`, or `Retired`.
4. `remediation_status`, when present, MUST be one of `none`, `pending`, `accepted`, or `rejected`.
5. `last_reviewed_at`, when present, MUST be RFC 3339 compatible.
6. Each entry in `evidence_refs`, when present, MUST be a string.
7. A represented transition from `Declared` to `Active` SHOULD be accompanied by sufficient verified evidence.
8. A represented transition from `Active` to `Restricted` or `Suspended` SHOULD be associated with policy deviation, integrity failure, or missing evidence.
9. A represented transition from `Recoverable` to `Active` SHOULD be accompanied by accepted remediation evidence and review approval.
10. A record in `Retired` state SHOULD NOT advertise active privileges through `policy_flags`.
11. Conformance checks MUST distinguish structural validation from governance adjudication and MUST NOT be treated as a substitute for policy review.

## 4. Transition Integrity Notes

Not every lifecycle transition can or should be automated. Automated evidence evaluation and manual review authority must remain distinguishable where both are represented. These conformance checks verify record structure and minimum transition coherence only; they do not authorize actions, override governance policy, or replace lifecycle decisions made by responsible reviewers.

## 5. Example Pass/Fail Cases

The fixture files in `examples/lifecycle-governance/` may be used as minimal reference inputs for schema validation and conformance-oriented review.

### Pass 1

```json
{
  "object_id": "pFDO:example:101",
  "lifecycle_state": "Active",
  "evidence_refs": [
    "aro-audit://bundle/1001"
  ],
  "policy_flags": [
    "baseline-verified"
  ],
  "remediation_status": "none",
  "last_reviewed_at": "2026-03-12T09:30:00Z"
}
```

This passes the minimal schema shape and uses a valid lifecycle vocabulary.

### Pass 2

```json
{
  "object_id": "pFDO:example:102",
  "previous_lifecycle_state": "Recoverable",
  "lifecycle_state": "Active",
  "evidence_refs": [
    "aro-audit://bundle/2001"
  ],
  "policy_flags": [
    "reinstatement-approved"
  ],
  "remediation_status": "accepted",
  "review_approved": true,
  "last_reviewed_at": "2026-03-12T10:00:00Z"
}
```

This passes because the represented recovery path is consistent with accepted remediation and explicit review approval.

### Fail 1

```json
{
  "object_id": "pFDO:example:103",
  "lifecycle_state": "Enabled",
  "evidence_refs": [
    7
  ],
  "policy_flags": [],
  "remediation_status": "done",
  "last_reviewed_at": "03/12/2026"
}
```

This fails because the state vocabulary, evidence reference item type, remediation status, and timestamp format are invalid.

### Fail 2

```json
{
  "object_id": "pFDO:example:104",
  "previous_lifecycle_state": "Recoverable",
  "lifecycle_state": "Active",
  "evidence_refs": [
    "aro-audit://bundle/3001"
  ],
  "policy_flags": [
    "full-access"
  ],
  "remediation_status": "pending",
  "review_approved": false,
  "last_reviewed_at": "2026-03-12T11:00:00Z"
}
```

This fails the minimal transition expectation because a recovery-to-active representation is missing accepted remediation and review approval.

## 6. Boundary Clarification

These checks validate object-specific lifecycle records only. They do not produce a general personality score, a cross-domain permanent reputation value, or a universal trust ranking. A lifecycle state is not a universal reputation score, and conformance results do not replace human governance responsibility.
