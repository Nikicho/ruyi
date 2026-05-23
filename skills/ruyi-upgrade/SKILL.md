---
name: ruyi-upgrade
description: Use when a project already contains .ruyi or .ruyirc but its Ruyi document layout or schema version may be behind the installed skills.
---

# Ruyi Upgrade

## 1. 定位

`ruyi-upgrade` 将已接入项目的 Ruyi 协议结构升级到当前 schema。它不是重新 init，也不重解释业务事实。

## 2. 硬边界

- 自动迁移仅覆盖固定结构、`.ruyirc`、`.gitignore` 与 `.ruyi/INDEX.md`。
- 不自动重写正式 spec、合并 contract 或解释旧审批结论。
- 旧 `derived_from` contract 与旧审批状态只列为人工审视项。
- 废弃目录只能在用户明确确认删除后清理。

## 3. 执行流程

1. 运行：

   ```powershell
   python skills/ruyi-upgrade/scripts/upgrade_project.py --project <path>
   ```

2. 报告自动更新项和人工审视项。
3. 若结果含 `obsolete_dirs`，只询问一次是否删除这些废弃目录。
4. 用户确认后运行：

   ```powershell
   python skills/ruyi-upgrade/scripts/upgrade_project.py --project <path> --remove-obsolete
   ```

5. 输出升级总结，并回到用户原本请求的流程阶段。

## 4. 当前 Schema

- 当前版本：`schema_version: 2`。
- Git 正式资产：`contracts / plans / tests / explain / spec`。
- 本地按需资产：`tasks / spec-candidates`。
- 已废弃目录：`workspace / spec-archive / spec-patches`。

详细边界见 `references/upgrade-discipline.md`，脚本回退规则见 `references/script-runtime-protocol.md`。
