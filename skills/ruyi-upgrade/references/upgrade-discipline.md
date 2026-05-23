# Upgrade Discipline

## 1. 目的

升级只让旧项目的 Ruyi 文档结构符合当前 skills 约束，不把机械迁移伪装成业务审查。

## 2. 自动允许项

- 为 `.ruyirc` 写入当前 `schema_version`。
- 更新 Ruyi 管理的本地目录 `.gitignore` 规则。
- 重建 `.ruyi/INDEX.md`。
- 在用户确认后删除废弃目录。

## 3. 禁止自动判断项

- 旧 `derived_from` 是否应改为同一 contract 的 `reopened`。
- 旧 `conditionally-approved` 或 `rejected` 应落到什么新结论。
- 正式 spec、baseline contract 或历史事实的业务内容。

这些项目必须输出到 `manual_review`，留给用户审视。

## 4. 删除确认

`.ruyi/workspace/`、`.ruyi/spec-archive/`、`.ruyi/spec-patches/` 不再被新流程读取或写入。升级首先报告存在的废弃目录；只有用户确认后才删除。
