# Spec Merge Protocol

## 1. 定位

`ruyi-spec-merge` 是主流程外的人工动作，用于周期性处理 `.ruyi/spec-candidates/` 中的候选规范。

它不属于单次需求的 8 阶段主流程，不自动触发。

## 2. 合入规则

- 只处理 `status: pending` 或旧版 `status: candidate` 的候选。
- 合入前必须读取目标 spec。
- 合入必须由用户确认。
- `project` 层候选可以写入 `.ruyi/spec/<target-spec>`。
- `team` 层候选只归档为候选处理结果，不自动写入 `.ruyi-team`。
- 合入或拒绝后，候选归档到 `.ruyi/spec-archive/<status>/...`。

## 3. 禁止行为

- 不自动批量合入。
- 不在没有用户确认时修改正式 spec。
- 不把候选原文全文搬进 spec，应只写入沉淀建议。
