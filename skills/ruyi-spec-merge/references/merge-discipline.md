# Merge Discipline

## 1. 核心规则

- spec merge 是周期性人工动作，不进入单次需求主流程。
- 没有用户确认，不处理 candidate。
- `merged` 只表示“候选通过评审，已生成手动合入 patch”，不表示脚本已修改正式 spec。
- `merge_apply.py` 不直接写 `.ruyi/spec/` 或 `.ruyi-team/`。
- team 层候选不自动写入 `.ruyi-team`。
- `superseded` 表示候选被更新版本取代，只归档，不写正式 spec。

## 2. 反模式

### 看到 pending candidate 就全部合入

触发场景：候选很多，用户说“整理一下”。

为什么错：候选不是正式规范，必须逐条确认。

正确做法：列出候选，逐条展示 diff 或 patch 预览，等待用户确认。

### 把 candidate 原文复制到 spec

触发场景：候选内容已经写得很完整。

为什么错：spec 是长期规则，不是过程记录。

正确做法：只提取“沉淀建议”中可长期复用的规则或事实，并通过 patch 交给用户人工合入。

### 把被新版本取代的 candidate 标记为 rejected

触发场景：同一目标 spec 有旧 candidate 和更新后的 candidate。

为什么错：`rejected` 表示不采纳，无法表达“被更新版本取代”的历史关系。

正确做法：把旧 candidate 标记为 `superseded` 并归档到 `.ruyi/spec-archive/superseded/`，继续评审新 candidate。
