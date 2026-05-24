# Spec Candidate Schema

## 1. 定位

`.ruyi/spec-candidates/` 是本地临时待审层，默认不提交 git。

candidate 路径跟随目标 spec 路径，不使用日期做版本目录。日期只作为来源 test 或 code observation 的锚点。

## 2. 路径

```text
.ruyi/spec-candidates/project/coding-baseline.md
.ruyi/spec-candidates/project/references/shared/table/columns.md
.ruyi/spec-candidates/project/references/modules/orders/search.md
.ruyi/spec-candidates/team/references/shared/table/columns.md
```

## 3. Frontmatter

```yaml
source_test: .ruyi/tests/<module>/<feature>/<date>.md
source_kind: approved-test | code-observation
module: <module>
feature: <feature>
date: <YYYY-MM-DD>
target_layer: project | team
target_spec: <spec path>
local_only: true
status: pending | superseded
```

## 4. 规则

- approved-test 来源必须锚定已审批通过的 test。
- test 来源必须能追溯到 contract 和 plan；tiny 按流程约定处理。
- code-observation 来源必须明确标记 `source_kind: code-observation`。
- 不允许把 contract、test 或 task 原文搬运进候选。
- candidate 与正式 spec 冲突时，正式 spec 胜出。
