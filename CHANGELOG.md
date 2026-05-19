# Changelog

## 1.0.1 - 2026-05-19

### Init 与成熟项目接入

- `ruyi-init` 支持成熟项目接入分流：快速开始只启用 Ruyi 流程，完整迁移才进行文档蒸馏和关键问题澄清。
- 外部文档蒸馏改为推荐使用本地浏览器工具读取；没有浏览器工具时，要求用户提供 agent 易读的 Markdown 或纯文本导出文件。
- 本地导出的文档只作为蒸馏输入，不写入可提交 spec，也不保存本地路径。

### 轻量维护流程

- `using-ruyi` 新增 `maintain` 意图，覆盖代码优化、代码微重构、去重复、类型收紧、lint 整理等无行为变化维护。
- 轻量维护统一路由到 `ruyi-implement`，不要求创建 contract、plan 或 task。
- 若维护会改变用户可感知行为、业务规则、接口语义、状态语义、权限、路由或验收标准，必须回到 `ruyi-contract`。

### Spec 结构调整

- 正式 spec 不再按日期区分版本；`.ruyi/spec/` 只表示当前应遵守的项目事实和规则。
- `frontend-baseline.md` 拆分为 `development-baseline.md` 和 `coding-baseline.md`。
- API 入口从 `spec/api/README.md` 调整为顶层 `api.md`。
- 新增 `spec/INDEX.md`、`spec/references/shared/` 和 `spec/references/modules/`，详细规则按 shared/module 归档。
- 同一功能或公共组件应放在同一个目录下，再按主题拆分，例如 `table/simple-usage.md`、`table/columns.md`。

### 本地候选与反推规范

- `spec-candidates` 调整为本地临时层，默认加入 `.gitignore`，避免提交后误导团队。
- `spec-archive` 和 `spec-patches` 同样作为本地处理产物默认忽略。
- candidate 路径改为跟随目标 spec：`.ruyi/spec-candidates/<target-layer>/<target-spec-path>`，不再按 contract 日期建版本目录。
- agent 读取 spec 时可以按需读取相关本地 candidates，但 candidate 只能作为待确认信号，不能覆盖正式 spec。
- 新增 `ruyi-spec-discover`，用于从现有代码反推本地 spec candidate，不直接写正式 spec。
