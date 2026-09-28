# 恢复批准记录的一致性检查 / Recovery Approval Record Consistency Check

## 中文

### 范围

本说明仅收紧已有生命周期治理记录中**明确表示**从 `Recoverable` 转到 `Active` 的情况，不定义新的状态、审查权限或通用问责模型。依据是 [生命周期状态机](lifecycle-state-machine.md) 中“补救证据被接受、人工审查批准后恢复”，以及[符合性检查](lifecycle-conformance-checks.md)中的第 9 项和通过／失败示例。

当记录同时包含 `previous_lifecycle_state: "Recoverable"` 和 `lifecycle_state: "Active"` 时，[最小模式](../../schemas/behavior-lifecycle-governance.schema.json)要求：

1. `evidence_refs` 存在且至少包含一条非空字符串引用；
2. `remediation_status` 等于 `"accepted"`；
3. `review_approved` 等于 `true`。

这是针对**已表示的转移记录**的条件形状检查。没有声明前一状态的记录仍按原有最小模式校验；不能据此推断它从未经历恢复。证据引用和布尔批准值都是记录中的声明，单独通过模式校验不能证明证据可解析、内容真实、审批人身份或其授权。实际治理裁决仍按原有政策和审查流程执行。

### 可审查样例

| 输入 | 预期 |
|---|---|
| `Recoverable → Active`，非空证据引用、`accepted`、`review_approved: true` | 通过本条件检查 |
| 相同转移但 `review_approved: false` | 不通过 |
| 相同转移但缺少证据引用或引用数组为空 | 不通过 |
| 无 `previous_lifecycle_state` 的最小记录 | 不触发本条件检查 |

## English / 英文

### Scope / 范围

This note tightens only lifecycle governance records that **explicitly represent** a transition from `Recoverable` to `Active`. It defines no new state, reviewer authority, or general accountability model. Its basis is the accepted remediation evidence and manual review approval in the [lifecycle state machine](lifecycle-state-machine.md), together with assertion 9 and the pass/fail examples in the [conformance checks](lifecycle-conformance-checks.md).

When a record contains both `previous_lifecycle_state: "Recoverable"` and `lifecycle_state: "Active"`, the [minimal schema](../../schemas/behavior-lifecycle-governance.schema.json) requires:

1. `evidence_refs` to be present with at least one nonempty string reference;
2. `remediation_status` to equal `"accepted"`;
3. `review_approved` to equal `true`.

This is a conditional shape check for **represented transitions**. Records without a declared previous state retain the original minimal validation; that does not establish that recovery never occurred. Evidence references and the approval boolean are claims in the record. Passing schema validation alone does not prove that evidence resolves, that its contents are authentic, or that a reviewer exists and was authorized. Governance decisions remain subject to the existing policy and review process.

### Review cases / 可审查样例

| Input / 输入 | Expected / 预期 |
|---|---|
| `Recoverable → Active`, nonempty evidence reference, `accepted`, `review_approved: true` | Pass this conditional check / 通过 |
| Same transition with `review_approved: false` | Fail / 不通过 |
| Same transition with absent or empty evidence references | Fail / 不通过 |
| Minimal record without `previous_lifecycle_state` | Condition does not apply / 不触发条件 |
