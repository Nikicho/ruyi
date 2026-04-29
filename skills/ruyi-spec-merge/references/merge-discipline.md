# Merge Discipline

## 1. 核心规则

- spec merge 是周期性人工动作，不进入单次需求主流程。
- 没有用户确认，不写正式 spec。
- 合入只提炼建议，不搬运完整候选。
- team 层候选不自动写入 `.ruyi-team`。
- `superseded` 表示候选被更新版本取代，只归档，不写正式 spec。

## 2. 反模式

### ❌ 看到 pending candidate 就全部合入

**触发场景**：候选很多，用户说“整理一下”。

**你想做的事**：批量写入 spec。

**为什么错**：候选不是正式规范，必须逐条确认。

**正确做法**：列出候选，逐条展示 diff，等待用户确认。

### ❌ 把 candidate 原文复制到 spec

**触发场景**：候选内容已经写得很完整。

**你想做的事**：整段复制。

**为什么错**：spec 是长期规则，不是过程记录。

**正确做法**：只合入“沉淀建议”中的可复用规则。

### ❌ 候选被新版本取代但只能 rejected

**触发场景**：同一规范有一条旧 candidate 和一条更新后的 candidate，旧 candidate 不该合入但也不是错误建议。

**为什么错**：`rejected` 表示不采纳，无法表达“被更新版本取代”的历史关系。

**正确做法**：把旧 candidate 标为 `superseded` 并归档到 `.ruyi/spec-archive/superseded/`，再继续评审新 candidate。
