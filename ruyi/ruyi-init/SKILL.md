---
name: ruyi-init
description: Use when an existing frontend project needs to be initialized for Ruyi with .ruyi, .ruyirc, project spec anchors, project actions, and workspace placeholders.
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
- 保守写入。
- `spec` 采用空白占位加部分自动内容。
- 不为追求完整而猜测。
- 不读取 team 层基线来决定初始化内容；team 层只在协作开发过程中参与规则注入。
- 初始化过程遵守 `references/init-discipline.md`。

## 4. 主流程

1. 判断支持范围。
2. 判断初始化状态。
3. 读取项目事实。
4. 生成 `.ruyirc`。
5. 生成 `.ruyi/spec/` 的 5 个锚点文件。
6. 创建 `contracts / plans / tasks / tests / explain / spec-candidates / workspace` 目录。
7. 生成 `.ruyi/project-actions.md`。
8. 更新 `.gitignore`。
9. 输出结果。

## 5. 脚本调用

推荐执行顺序：

1. 运行 `scripts/init_detect.py --project <path>`。
2. 如果 `supported=false`，直接拒绝初始化。
3. 如果 `initialized=true` 且 `complete=true`，停止，不重复初始化。
4. 如果 `initialized=true` 且 `complete=false`，停止，只报告缺失项，不自动补齐。
5. 如果未初始化且支持，运行 `scripts/init_read.py --project <path>`。
6. 把读取结果保存为 facts JSON。
7. 运行 `scripts/init_write.py --project <path> --facts <facts.json>`。
8. 运行 `scripts/init_report.py --detect <detect.json> --write <write.json>` 输出最终报告。

脚本职责：

- `scripts/init_detect.py`：输出项目是否支持、是否初始化、结构是否完整、缺失项。
- `scripts/init_read.py`：按白名单读取前端项目事实，输出 facts JSON。
- `scripts/init_write.py`：保守写入 `.ruyirc` 和 `.ruyi/` 固定结构，不覆盖已有文件。
- `scripts/init_report.py`：把 detect/write 结果整理成人可读报告。

## 6. 输出要求

- 已创建项
- 已跳过项
- 待确认项
- 拒绝原因

## 7. 写入范围

允许创建：

- `.ruyirc`
- `.ruyi/README.md`
- `.ruyi/spec/project-overview.md`
- `.ruyi/spec/project-structure.md`
- `.ruyi/spec/frontend-baseline.md`
- `.ruyi/spec/testing-baseline.md`
- `.ruyi/spec/open-questions.md`
- `.ruyi/contracts/`
- `.ruyi/plans/`
- `.ruyi/tasks/`
- `.ruyi/tests/`
- `.ruyi/explain/`
- `.ruyi/spec-candidates/`
- `.ruyi/workspace/README.md`
- `.ruyi/project-actions.md`

允许追加：

- `.gitignore` 中的 `.ruyi/workspace/**`
- `.gitignore` 中的 `!.ruyi/workspace/README.md`

禁止：

- 覆盖已有文件。
- 自动补齐不完整初始化。
- 读取页面文件正文来推断业务。
- 读取 team 层规范来决定初始化内容。

## 8. 必读参考

- `../references/main-flow.md`
- `../references/spec-schema.md`
- `references/init-discipline.md`
