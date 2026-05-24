---
name: ruyi-init
description: Use when an existing frontend project needs to be initialized for Ruyi, including mature brownfield projects. Common triggers: "接入Ruyi", "初始化Ruyi", "启用Ruyi", "init Ruyi", "setup Ruyi". Creates .ruyi, .ruyirc, confidence-marked project spec anchors, split baselines, spec INDEX, docs-registry/interview-bank for full migration, INDEX, CLAUDE.md reminder, Claude Code hook, and /ruyi fallback command.
---

# Ruyi Init

## 1. 适用场景

- 用户要把已有前端项目接入 Ruyi。
- 用户要求初始化 `.ruyi/`。
- 用户要求创建 `.ruyirc`。

## 2. 硬门禁

- 当前仅支持前端项目：Vue、Vite、React、Webpack 及其常见 JS/TS 组合。
- 已初始化且结构完整时，停止，不重复执行。
- 已初始化但结构不完整时，只提示缺失项，不自动补齐。
- 不做部分初始化。
- 不覆盖已有文件。

## 3. 执行原则

- 白名单读取项目事实。
- 成熟项目接入不批量倒灌历史交付 contract，但完整迁移可以生成模块级 baseline contract。
- 用户选择“快速开始”时，不生成 `docs-registry.md`、`interview-bank.md`、`init-evaluation-notes.md`。
- 用户选择“完整迁移”时，蒸馏现有文档并澄清关键问题；模块业务事实写入 baseline contract，不写入正式 spec。
- 所有 spec 内容必须带 confidence。
- 保守写入。
- `spec` 采用空白占位加部分自动内容。
- 不为追求完整而猜测。
- 不读取 team 层基线来决定初始化内容；team 层只在协作开发过程中参与规则注入。
- 未明确选择 `quick-start` 或 `full-migration` 前，禁止运行 `init_write.py`，禁止写入 `.ruyi/`。
- 初始化过程遵守 `references/init-discipline.md`。

## 4. 主流程

1. 判断支持范围。
2. 判断初始化状态。
3. 让用户选择接入方式；未选择前必须停住：
   - 快速开始：只启用 Ruyi 流程，历史知识后续按需补。
   - 完整迁移：蒸馏现有文档并澄清关键问题，建立项目知识基线。
4. 读取项目事实；完整迁移时同时读取候选文档源和 brownfield 必问问卷。
5. 生成 `.ruyirc`。
6. 生成 `.ruyi/spec/` 基础锚点、拆分后的 baseline、`api.md`、`references/shared/`、`references/modules/` 和 `.ruyi/spec/INDEX.md`；spec 只放长期规则、索引和跨模块约束。
7. 完整迁移时生成 `docs-registry.md`、`interview-bank.md`，并把蒸馏/代码反推的模块业务事实写入 `.ruyi/contracts/<module>/_baseline/current.md` 或 `.ruyi/contracts/<module>/<feature>/baseline.md`。
8. 创建正式共享目录 `contracts / plans / tests`；`tasks / spec-candidates` 仅在后续本地需要时按需创建。
9. 生成 `.ruyi/project-actions.md`。
10. 生成 `.ruyi/INDEX.md` 新格式占位。
11. 写入或合并 `.claude/settings.json` 的入口保护 hook。
12. 创建或追加 `CLAUDE.md` 的 Ruyi 主流程激活段。
13. 创建 `.claude/commands/ruyi.md` 手动兜底命令。
14. 更新 `.gitignore`。
15. 输出结果。

## 5. 完整迁移向导

完整迁移必须先引导，再写入。

### 5.1 文档分流

对候选文档逐个确认：

```text
<path>：保留入口 / 蒸馏关键事实 / 不录入？
```

- 保留入口：写入 `docs-registry.md`。
- 蒸馏关键事实：抽取 10-20 条，按模块写入 baseline contract。
- 不录入：不写入项目产物。

### 5.2 外部文档读取

遇到 Confluence、Notion、Apifox、语雀、飞书、内网知识库等外部文档时，先判断本地是否有可用浏览器工具，例如 `agent-browser`、`fast-browser`、`bb-browser`。

- 有浏览器工具：推荐用户授权通过这些工具查看文档，再做蒸馏。
- 没有浏览器工具：要求用户先把外部文档统一转换成 agent 易读的文本文件，例如 Markdown 或纯文本；只蒸馏，不保存外部文档地址。
- 本地导出文件只作为蒸馏输入，不写入 `docs-registry.md`，也不把本地路径写进可提交 spec。
- PDF、docx、HTML 不直接读取；用户应先转换成文本类文件再交给 agent。
- 不采用复制粘贴长文方式。

### 5.3 蒸馏确认

蒸馏内容必须先展示：

```text
从 <path> 蒸馏：
- <fact>
- <fact>
确认写入 <target-baseline-contract>？
```

未确认的蒸馏内容只能标 `confidence: distilled` 和 `needs_review: true`。

蒸馏时应参考现有代码进行交叉校验：

- 文档声称且代码能观察到的事实，写入 baseline contract 的 `## 当前业务事实` 和 `## 代码观察`。
- 文档声称但代码无法确认的事实，仍可写入 baseline contract，但必须保持 `status: draft`、`needs_review: true`。
- 代码观察到但文档没有覆盖的稳定业务事实，也可以写入对应 baseline contract，来源标为代码观察。
- 不确定内容写入 baseline contract 的 `## 已知不确定项`，不写入正式 spec。

### 5.4 关键问题澄清

一次只问一个：

```text
鉴权方式：JWT / Session / OAuth / 其它 / 不知道？
```

优先主题：

- 鉴权流程
- 错误处理
- 路由约定
- 接口对接
- 状态管理
- 测试约定

用户答“不知道”时写入 `open`，不继续追问同一主题细节。

### 5.5 写入预览

写入前必须展示：

```text
将生成：
- docs-registry.md：<n> 个入口
- interview-bank.md：<n> 条确认答案
- <target-baseline-contract>：<n> 条蒸馏事实
确认写入？
```

用户确认后才运行 `init_write.py`。

## 6. 脚本调用

推荐执行顺序：

1. 运行 `scripts/init_detect.py --project <path>`。
2. 如果 `supported=false`，直接拒绝初始化。
3. 如果 `initialized=true` 且 `complete=true`，停止，不重复初始化。
4. 如果 `initialized=true` 且 `complete=false`，停止，只报告缺失项，不自动补齐。
5. 如果未初始化且支持，运行 `scripts/init_read.py --project <path>`。
6. 按用户选择写入 `facts.brownfield.mode`；如果用户还没选，停止并询问，不得继续：
   - `quick-start`
   - `full-migration`
7. 完整迁移时，先让用户确认文档分流和问卷答案，再写入 facts。
8. 运行 `scripts/init_write.py --project <path> --facts <facts.json>`。
9. 运行 `scripts/init_report.py --detect <detect.json> --write <write.json>` 输出最终报告。

脚本职责：

- `scripts/init_detect.py`：输出项目是否支持、是否初始化、结构是否完整、缺失项。
- `scripts/init_read.py`：按白名单读取前端项目事实，扫描候选文档源，输出 brownfield 问卷题库和 facts JSON。
- `scripts/init_write.py`：按接入方式保守写入 `.ruyirc`、`.ruyi/` 固定结构、confidence 标记和 brownfield 产物，不覆盖已有文件。
- `scripts/init_report.py`：把 detect/write 结果整理成人可读报告，包含成熟项目接入摘要。

## 7. 输出要求

- 已创建项
- 已跳过项
- 待确认项
- 接入方式
- 完整迁移时：文档评估摘要、已确认问卷答案数量、仍开放的关键问题
- 拒绝原因

## 8. 写入范围

允许创建：

- `.ruyirc`
- `.ruyi/README.md`
- `.ruyi/spec/project-overview.md`
- `.ruyi/spec/project-structure.md`
- `.ruyi/spec/INDEX.md`
- `.ruyi/spec/testing-baseline.md`
- `.ruyi/spec/development-baseline.md`
- `.ruyi/spec/coding-baseline.md`
- `.ruyi/spec/open-questions.md`
- `.ruyi/spec/api.md`
- `.ruyi/contracts/`
- `.ruyi/plans/`
- `.ruyi/tests/`
- `.ruyi/project-actions.md`
- `.claude/commands/ruyi.md`

完整迁移时额外允许创建：

- `.ruyi/spec/docs-registry.md`
- `.ruyi/spec/interview-bank.md`

允许追加：

- `.gitignore` 中的 `.ruyi/tasks/**`
- `.gitignore` 中的 `.ruyi/spec-candidates/**`
- `.claude/settings.json` 中的 `hooks.UserPromptSubmit`
- `CLAUDE.md` 中的 `## Ruyi 主流程激活` 段

禁止：

- 覆盖已有文件。
- 自动补齐不完整初始化。
- 批量生成历史交付 contract / plan / test；完整迁移只允许生成当前业务事实 baseline contract。
- 把陈旧或低质量文档入口录入 docs-registry。
- 把 distilled / claimed 内容当成 observed 事实。
- 读取页面文件正文来推断业务。
- 读取 team 层规范来决定初始化内容。
- 在 hook 中执行业务路由或读取 `.ruyi/` 内容；hook 只能检测存在性并输出 reminder。

## 9. 必读参考

- `references/main-flow.md`
- `references/spec-schema.md`
- `references/init-discipline.md`
