# Explain Discipline

`ruyi-explain` 已在 schema v3 主流程中退役。

正式交付不再生成 explain，不再 lint explain，也不通过 explain 进入 approve。

如果旧项目存在 `.ruyi/explain/`，使用 `ruyi-upgrade` 将审批状态迁移到对应 test 后删除旧目录。
