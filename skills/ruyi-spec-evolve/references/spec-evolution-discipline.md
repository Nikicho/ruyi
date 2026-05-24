# Spec Evolution Discipline

## 1. 目标

spec-evolve 负责把 approved test 或 code observation 中可复用、长期有效的规则提炼为正式 spec 或本地 spec candidate。

它不是备份开发过程，也不是把 contract/test 原文搬进 spec。

## 2. 硬门禁

- 没有 approved test 或明确 code observation，不进入正式沉淀。
- approved test 必须能追溯 contract 和 plan；tiny 按流程约定处理。
- 不允许把 `contract / test / task / project-actions` 原样转成 spec。
- 不自动写入 team 层。

## 3. 流程

1. 读取 approved test 或 code observation。
2. 读取 `.ruyi/spec/INDEX.md` 和目标相关 spec。
3. 判断内容是否长期有效、跨场景复用、可被后续 agent 执行。
4. 用户当场确认时，直接更新正式 spec。
5. 用户延后审视或批量代码反推时，写入 `.ruyi/spec-candidates/`。

## 4. 反模式

| 反模式 | 正确处理 |
| --- | --- |
| 把 test 复制进 spec | 提炼规则，不搬运过程 |
| 把一次性需求写成项目规范 | 留在 contract/test，不进 spec |
| 没审批就沉淀交付结论 | 等待 approved test |
| 与正式 spec 冲突时采用 candidate | 正式 spec 胜出，candidate 待审 |
