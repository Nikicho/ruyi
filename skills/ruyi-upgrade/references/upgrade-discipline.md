# Upgrade Discipline

## 1. 目的

升级只让旧项目的 Ruyi 文档结构符合当前 skills 约束，不把机械迁移伪装成业务审查。

## 2. 自动允许项

- 创建 schema v3 必要目录。
- 更新 Ruyi 管理的本地目录 `.gitignore` 规则。
- 创建 `.ruyi/spec/INDEX.md`。
- 拆分旧 `frontend-baseline.md` 为 `development-baseline.md` 和 `coding-baseline.md`，并删除旧文件。
  - `development-baseline.md` 只放开发过程动作，例如运行命令、验证步骤、提交前检查、CI/浏览器验证。
  - `coding-baseline.md` 放代码产物规则，例如组件边界、props/slots/events、状态管理、样式、类型、目录结构、错误处理。
  - 同一行同时出现组件/代码主题和“运行/执行/命令/提交前”等动作时，按动作性质进入 development；否则优先保留为 coding。
- 合并旧 `references/shared/INDEX.md`、`references/modules/INDEX.md` 到 `.ruyi/spec/INDEX.md`，并删除旧二级 INDEX。
- 将旧 explain 的审批状态迁移到对应 test。
- 重建 `.ruyi/INDEX.md`。
- 在用户确认后删除废弃目录。
- 废弃目录清理完成后，为 `.ruyirc` 写入当前 `schema_version`。

## 3. 禁止自动判断项

- 旧 `derived_from` 是否应改为同一 contract 的 `reopened`。
- 旧 `conditionally-approved` 或 `rejected` 应落到什么新结论。
- 从旧 spec 检出的业务事实是否已经完全可信。
- 无法按“过程动作 vs 代码产物规则”判断的长期规范该进入 `development-baseline.md`、`coding-baseline.md` 还是 `open-questions.md`。

这些项目必须输出到 `needs_user_decision`，留给用户审视。

## 4. 删除确认

`.ruyi/explain/`、`.ruyi/workspace/`、`.ruyi/spec-archive/`、`.ruyi/spec-patches/` 不再被新流程读取或写入。

升级首先报告存在的废弃目录；只有用户确认后才删除。删除前不得把项目标为完整 schema v3。

## 5. 完成条件

只有同时满足以下条件，upgrade 才能返回 `completed: true`：

- `.ruyirc` 已写入 `schema_version: 3`。
- `.ruyi/explain/` 已迁移并删除。
- 旧 `frontend-baseline.md` 已删除。
- 旧二级 spec INDEX 已删除。
- 根 `.ruyi/INDEX.md` 已按当前正式产物重建。
