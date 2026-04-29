# Ruyi Index Protocol

## 1. 定位

`.ruyi/INDEX.md` 是自动生成的跨需求索引，帮助 agent 快速回答“上次为什么这么做”“某模块有哪些历史需求”等问题。

它是团队共享知识，应提交到 git；它不是临时 workspace。

## 2. 规则

- INDEX 可以由脚本重建。
- 不建议人工编辑 INDEX。
- agent 查询历史需求时，先读 INDEX；只有路由确定到具体 feature 后，才读取对应 contract、explain 或 spec-candidate。
- Ritual 阶段禁止为“了解背景”读取多个 feature 的 contract / plan / explain 正文。
- INDEX 失同步时，以 `.ruyi/` 下正式产物为准并重建。
- 每个 feature 至少包含一句话业务目标、类型、状态和日期产物列表。

## 3. 结构

```md
# Ruyi Index

## 模块：board

### card-status-filter

- 业务目标：看板按卡片状态筛选
- 类型：new-feature
- 状态：approved
- 2026-04-28 contract / plan / test / explain

### copy-tweak

- 业务目标：调整看板按钮文案
- 类型：change, size: tiny
- 状态：completed
- 2026-04-28 contract / test
```

`业务目标` 优先来自 contract frontmatter 或 `## 业务规则` 中的业务目标；抽取不到时，使用 `## 用户故事` 第一行；仍抽取不到时写 `待补充` 并在重建脚本输出 warning。
