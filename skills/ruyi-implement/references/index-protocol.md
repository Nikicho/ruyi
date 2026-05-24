# Ruyi Index Protocol

## 1. 定位

`.ruyi/INDEX.md` 是自动生成的跨需求索引，帮助 agent 快速判断当前项目有哪些历史交付、每个 feature 处于什么阶段，以及下一步应读取哪个正式产物。

它是团队共享知识，应提交到 git；它不是临时 workspace，也不是 spec 入口。

`.ruyi/spec/INDEX.md` 是唯一正式 spec 检索入口，负责索引顶层 baseline、`references/shared/` 和 `references/modules/` 下的细分规范。

## 2. 根 INDEX 规则

- `.ruyi/INDEX.md` 可以由脚本重建。
- 不建议人工编辑 `.ruyi/INDEX.md`。
- `.ruyi/INDEX.md` 只索引 `contracts / plans / tests`。
- 不索引 `.ruyi/tasks/`、`.ruyi/spec-candidates/`、`.ruyi/explain/` 或废弃目录。
- agent 查询历史需求时，先读 `.ruyi/INDEX.md`；只有路由确定到具体 feature 后，才读取对应 contract、plan 或 test 正文。
- Ritual 阶段禁止为“了解背景”读取多个 feature 的 contract / plan / test 正文。
- INDEX 失同步时，以 `.ruyi/` 下正式产物为准并重建。

## 3. Spec INDEX 规则

- 需要项目规范时，先读 `.ruyi/spec/INDEX.md`。
- 读取顶层 baseline 后，必须继续按 baseline 或 spec INDEX 的链接读取相关 references。
- `references/shared/` 和 `references/modules/` 不维护二级 INDEX。
- 本地 `.ruyi/spec-candidates/` 可按目标相关性读取，但不能覆盖正式 spec。

## 4. 根 INDEX 结构

```md
# Ruyi Index

## 模块：board

### card-status-filter

- 业务目标：看板按卡片状态筛选
- 类型：new-feature
- 需求状态：confirmed
- 验证状态：passed-with-notes
- 审批状态：approved
- 2026-04-28 contract / plan / test

### copy-tweak

- 业务目标：调整看板按钮文案
- 类型：change, size: tiny
- 需求状态：confirmed
- 验证状态：passed
- 审批状态：不适用
- 2026-04-28 contract / test
```

`业务目标` 优先来自 contract frontmatter 或 `## 业务规则` 中的业务目标；抽取不到时，使用 `## 用户故事` 第一行；仍抽取不到时写 `待补充` 并在重建脚本输出 warning。
