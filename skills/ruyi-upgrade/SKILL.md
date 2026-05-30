---
name: ruyi-upgrade
description: Use when a project already contains .ruyi or .ruyirc but its Ruyi document layout or schema version may be behind the installed skills.
---

# Ruyi Upgrade

## 1. 定位

`ruyi-upgrade` 将已接入项目的 Ruyi 协议结构升级到当前 schema。它不是重新 init，也不重新解释业务需求。

## 2. 硬边界

- 自动迁移覆盖固定结构、`.ruyirc`、`.gitignore`、`.ruyi/INDEX.md`、旧 baseline、旧 explain 审批和旧入口文件。
- 不把机械迁移伪装成业务确认；从旧 spec 迁移出的业务事实必须保留 `needs_review`。
- 废弃目录必须在用户确认后删除。
- 只在废弃目录已经删除后，才把 `.ruyirc` 标记为 `schema_version: 3`。

## 3. 执行流程

1. 运行预览和非破坏性迁移：

   ```powershell
   python skills/ruyi-upgrade/scripts/upgrade_project.py --project <path>
   ```

2. 报告自动更新项、待用户确认项和废弃目录。
3. 若结果含 `obsolete_dirs`，只询问一次是否删除这些废弃目录。
4. 用户确认后运行：

   ```powershell
   python skills/ruyi-upgrade/scripts/upgrade_project.py --project <path> --remove-obsolete
   ```

5. 确认结果 `completed: true`，输出升级总结，并回到用户原本请求的流程阶段。

## 4. 当前 Schema

- 当前版本：`schema_version: 3`。
- Git 正式资产：`contracts / plans / tests / spec / INDEX.md`。
- 本地按需资产：`tasks / spec-candidates`。
- 已废弃目录：`explain / workspace / spec-archive / spec-patches`。
- 旧 `frontend-baseline.md` 会拆分为 `development-baseline.md` 和 `coding-baseline.md` 后删除。
  - 开发过程动作进入 `development-baseline.md`。
  - 代码产物规则进入 `coding-baseline.md`。
- 旧 `spec/references/shared/INDEX.md` 与 `spec/references/modules/INDEX.md` 会合并到 `.ruyi/spec/INDEX.md` 后删除。
- 旧 explain 的审批状态会迁移到对应 test。

详细边界见 `references/upgrade-discipline.md`，脚本回退规则见 `references/script-runtime-protocol.md`。
