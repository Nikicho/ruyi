# Ruyi Index Protocol

## 1. 定位

`.ruyi/INDEX.md` 是自动生成的跨需求索引，帮助 agent 快速回答“上次为什么这么做”“某模块有哪些历史需求”等问题。

它是团队共享知识，应提交到 git；它不是临时 workspace。

## 2. 规则

- INDEX 可以由脚本重建。
- 不建议人工编辑 INDEX。
- agent 查询历史需求时，先读 INDEX，再按链接读取 contract、explain 或 spec-candidate。
- INDEX 失同步时，以 `.ruyi/` 下正式产物为准并重建。

## 3. 结构

```md
# Ruyi Index

## 模块：board

### card-status-filter
- 2026-04-28 contract
- 2026-04-28 explain
- 2026-04-28 spec-candidate
```
