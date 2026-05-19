# Spec Merge Protocol

## 1. 定位

`ruyi-spec-merge` 是主流程外的人工动作，用于周期性处理本地 `.ruyi/spec-candidates/` 中的候选规范。

它不属于单次需求的主流程，不自动触发，也不直接修改正式 spec。

## 2. 合入规则

- 只处理 `status: pending` 或旧版 `status: candidate` 的候选。
- 合入前必须读取目标正式 spec，并展示候选会影响的内容。
- 合入必须由用户确认。
- `merged` 不直接写正式 spec，而是生成 `.ruyi/spec-patches/...patch.md`。
- `project` 层候选的 patch 目标是 `.ruyi/spec/<target-spec>`。
- `team` 层候选只归档为候选处理结果，不自动写入 `.ruyi-team`。
- `merged`、`rejected`、`superseded` 后，候选归档到 `.ruyi/spec-archive/<status>/...`。
- `.ruyi/spec-candidates/`、`.ruyi/spec-archive/` 和 `.ruyi/spec-patches/` 默认本地忽略，不提交给团队。

## 3. patch 规则

- patch 只包含 candidate 中的“沉淀建议”。
- patch 必须保留来源 candidate、目标层级、目标 spec 和处理原因。
- patch 是人工合入依据，不是自动执行脚本。
- 用户或维护者合入正式 spec 时，应只保留可长期复用的规则或事实。
- 正式 spec 不按日期生成新版本；合入后修改当前唯一正确文件，历史由 git 保留。

## 4. 禁止行为

- 不自动批量合入。
- 不由脚本直接修改正式 spec。
- 不把候选原文全文搬进 spec。
- 不把单次需求细节沉淀为长期规范。
- 不把本地 candidate、archive 或 patch 提交给 git。
