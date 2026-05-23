# Merge Discipline

## 1. 核心规则

- spec merge 是周期性人工动作，不进入单次需求主流程。
- 没有用户确认，不处理 candidate。
- 项目层候选被接受时，先直接更新正式 spec，再删除 candidate。
- `merge_apply.py` 只清理已处理 candidate，不判断正式规则内容是否正确。
- team 层候选不自动写入 `.ruyi-team`。

## 2. 反模式

### 看到 pending candidate 就全部合入

触发场景：候选很多，用户说“整理一下”。

为什么错：候选不是正式规范，必须逐条确认。

正确做法：列出候选，逐条展示预览，等待用户确认。

### 把 candidate 原文复制到 spec

触发场景：候选内容已经写得很完整。

为什么错：spec 是长期规则，不是过程记录。

正确做法：只提取“沉淀建议”中可长期复用的规则或事实，用户确认后直接写入当前正式 spec。

### 为被替代的 candidate 保留本地归档

触发场景：同一目标 spec 有旧 candidate 和更新后的 candidate。

为什么错：candidate 是本地待审信号，不是团队历史资产；保留垃圾目录增加后续误读风险。

正确做法：确认新候选覆盖旧提案后删除旧 candidate，继续评审当前内容。
