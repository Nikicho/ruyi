# Init Discipline

## 1. 目标

init 阶段负责把一个已有前端项目接入 Ruyi，并生成固定 `.ruyi/` 协议结构。

它不是项目重构、不是业务分析、不是 team 规范加载，也不是一次性把所有缺失内容自动补齐。

成熟项目接入时，init 的目标是建立未来工作所需的最小知识基线，不把历史功能倒灌成 contract。

本纪律内化自 Superpowers 的 `brainstorming` 和 `writing-skills`：

- 吸收 `brainstorming` 的“先理解上下文再行动”，初始化前必须先读取项目事实。
- 吸收 `writing-skills` 的可维护结构意识，Ruyi 初始化产物必须结构固定、边界清楚、后续可维护。
- 不吸收工作树管理、复杂仓库策略或通用脚手架行为。

## 2. 硬门禁

- 当前仅支持前端项目：Vue、Vite、React、Webpack 及常见 JS/TS 组合。
- 非前端项目直接拒绝，不尝试兼容。
- 已完整初始化时停止，不重复写入。
- 已初始化但结构不完整时只报告缺失项，不自动补齐。
- 不读取 team 层规范来决定初始化内容。
- 不覆盖已有文件。
- 初始化必须部署入口保护：INDEX 占位、CLAUDE.md 持久提示、Claude Code hook、`/ruyi` 手动兜底命令。
- 初始化必须创建 `.ruyi/spec/api/README.md`，但不读取项目代码推断 API 列表。
- 初始化必须为 spec 内容写入 confidence，区分 `observed / distilled / claimed / open / confirmed_by_user`。
- 快速开始不生成 `docs-registry.md`、`interview-bank.md` 和 `workspace/init-evaluation-notes.md`。
- 完整迁移必须生成 `docs-registry.md`、`interview-bank.md` 和 `workspace/init-evaluation-notes.md`。
- 不批量生成历史 contract、plan、test、explain。

## 3. 项目事实读取

允许读取：

- `package.json`。
- 构建配置，如 Vite、Webpack、TypeScript、Babel、ESLint 配置。
- 核心入口文件，如 `main.js`、`main.ts`、`App.vue`、`index.html`。
- router、store、service、api 的使用方式。
- 三层以内目录概览，用于判断模块分布。

禁止读取或推断：

- 不读取 `src/views/**/index.vue`、`src/pages/**/index.vue` 正文来猜业务。
- 不根据页面文件正文推断业务规则。
- 不把临时发现直接写成正式规范。

## 4. Brownfield 接入规则

成熟项目接入只有两种方式：

- 快速开始：只启用 Ruyi 流程，历史知识后续按需补。
- 完整迁移：蒸馏现有文档并澄清关键问题，建立项目知识基线。

完整迁移采用 evaluate / distill / interview / fallback：

- evaluate：扫描 README、CHANGELOG、docs、mock 等候选文档源，只输出候选和抽样，不默认信任。
- distill：部分有用文档只抽 10-20 条关键事实进 spec，不翻译全文。
- interview：用封闭式问卷收集鉴权、错误处理、路由约定等关键答案，答案写入 `interview-bank.md`。
- fallback：用户对必问问题答“不知道”达到 3 条，或项目无可用文档时，生成 `open` 占位并在报告中提示知识基线薄弱。

外部文档读取规则：

- 如果用户本地有 `agent-browser`、`fast-browser`、`bb-browser` 等浏览器工具，优先推荐通过浏览器工具查看外部文档后再蒸馏。
- 如果没有可用浏览器工具，要求用户提供本地导出文件，例如 Markdown、HTML、PDF、docx；只蒸馏，不保存外部文档地址。
- 本地导出文件只作为蒸馏输入，不写入 `docs-registry.md`，也不把本地路径写进可提交 spec。
- 不采用复制粘贴长文方式。

文档三档分流：

| 质量 | 处理 |
| --- | --- |
| 有用 | 录入 `.ruyi/spec/docs-registry.md` |
| 部分有用 | 蒸馏关键事实进 spec，源本身不录入 registry |
| 陈旧 / 已废 / 误导 | 不录入，只写入 `workspace/init-evaluation-notes.md` |

## 5. Confidence 规则

| confidence | 含义 |
| --- | --- |
| `observed` | 从代码、配置、目录结构观察到的事实 |
| `distilled` | 从外部文档蒸馏出的关键事实，引用前需复核 |
| `claimed` | 文档声称但未验证的事实 |
| `open` | 未确认问题，不能当事实引用 |
| `confirmed_by_user` | 用户在问卷或对话中明确确认 |

## 6. 反模式

| 反模式 | 正确处理 |
| --- | --- |
| 看到 `package.json` 就直接写入 | 先完成支持范围和初始化状态判断 |
| 非前端项目也尝试接入 | 直接拒绝并说明 Ruyi 当前仅支持前端 |
| 不完整初始化时自动补齐 | 停止并报告缺失项，让用户决定后续处理 |
| 初始化时读取 team 规范 | team 层只在协作开发过程中参与规则注入 |
| 猜测业务模块规则 | 只记录可观察项目事实和待确认问题 |
| 初始化时把 Swagger / API 列表复制进 spec | 只创建 `spec/api/README.md`，由用户后续补权威源链接 |
| 用 hook 执行业务路由 | hook 只检测 `.ruyi/` 或 `.ruyirc` 并输出 reminder |
| 把历史功能倒灌成 contract | 历史留在代码、git、外部文档；Ruyi 从下一次变更开始生成 contract |
| 把所有外部文档都录入 docs-registry | 只录入已确认有用入口，陈旧文档写入评估笔记 |
| 蒸馏时翻译全文 | 只抽关键事实，并写 confidence/source/verified_at |
| 用户答不上来仍强行写规范 | 触发 fallback，写 open 占位 |

## 7. 检查清单

初始化前检查：

- 是否是支持范围内的前端项目？
- 是否已经存在 `.ruyi/` 或 `.ruyirc`？
- 如果已存在，结构是否完整？
- 本次写入是否会覆盖已有文件？
- 项目事实是否来自白名单文件？
- spec 占位内容是否只记录事实和待确认问题？
- 是否避免生成历史 contract？
- docs-registry 是否只包含有用入口？
- 所有 spec 是否带 confidence？
