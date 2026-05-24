# Spec Merge Protocol

## 1. 定位

`ruyi-spec-merge` 是主流程外的人工动作，用于周期性处理本地 `.ruyi/spec-candidates/` 中的候选规范。

它不属于单次需求的主流程，不自动触发。

## 2. 合入规则

- 只处理 `status: pending` 的候选；旧版状态交给 `ruyi-upgrade` 报告审视。
- 合入前必须读取目标正式 spec，并展示候选会影响的内容。
- 合入必须由用户确认。
- `project` 层候选被接受时，直接更新 `.ruyi/spec/<target-spec>` 当前文件，之后删除 candidate。
- `team` 层候选不自动写入 `.ruyi-team`；由用户决定如何提升，再删除或保留待审 candidate。
- 拒绝或被更新提案取代的 candidate 直接删除。
- `.ruyi/spec-candidates/` 默认本地忽略，不提交给团队。

## 3. 正式更新规则

- 只把 candidate 中经确认可长期复用的规则或事实写入正式 spec。
- 正式 spec 不按日期生成新版本；合入后修改当前唯一正确文件，历史由 git 保留。

## 4. 禁止行为

- 不自动批量合入。
- 不在用户未确认前修改正式 spec。
- 不把候选原文全文搬进 spec。
- 不把单次需求细节沉淀为长期规范。
- 不把本地 candidate 提交给 git。
