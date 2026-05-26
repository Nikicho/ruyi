![Ruyi 首页图](./assets/ruyi-home.png)

# Ruyi 如意

> A repo-native collaboration framework for AI coding agents.

Ruyi 是一套面向 AI 协作开发的规范框架。它让 agent 在项目仓库里按固定流程工作：先澄清需求，再制定计划，再实现、验证、审批，最后把有长期价值的经验沉淀成可提交的项目规范。

Ruyi 不是 CLI 产品，也不是项目管理系统。用户日常只需要用自然语言和 agent 对话；Ruyi 通过 skills 和项目内 `.ruyi/` 文档，让 agent 知道当前该读什么、该做什么、不能跳过什么。

## 适合什么场景

Ruyi 适合已经开始用 AI agent 做真实开发的团队，尤其是这些问题已经出现时：

- agent 拿一句口头需求就直接改代码。
- 长对话里漏读项目规则、漏跑测试、忘记验收标准。
- 需求、计划、验证和审批散落在聊天记录里，团队成员无法复用。
- 成熟项目想接入 AI 协作流程，但不想补写大量历史 contract。
- 项目经验需要沉淀成可提交、可版本化的规范，而不是只留在某次会话里。

Ruyi 的核心资产是项目里的 `.ruyi/` 文档。它们应该和业务代码一起提交，让团队成员和 agent 都读取同一份项目事实。

## 安装

把本仓库 `skills/` 目录里的内容复制到 code agent 可发现的 skills 目录。

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
Copy-Item -Recurse -Force ".\skills\*" "$env:USERPROFILE\.agents\skills\"
```

本地开发 Ruyi 时，也可以为每个 skill 建目录联接，避免复制后忘记同步。

```powershell
cmd /c mklink /J "%USERPROFILE%\.agents\skills\using-ruyi" "D:\AIWorks\ruyi\skills\using-ruyi"
cmd /c mklink /J "%USERPROFILE%\.agents\skills\ruyi-init" "D:\AIWorks\ruyi\skills\ruyi-init"
```

其他阶段 skill 按同样方式链接。安装后重启 code agent。

## 最快开始

在目标项目里对 agent 说：

```text
把这个项目接入 Ruyi。
```

agent 应先进入 `using-ruyi`，判断项目是否已经初始化。如果项目还没有 `.ruyi/`，会进入 `ruyi-init` 并让你选择接入方式：

- 快速开始：创建最小 `.ruyi/` 结构、入口保护和基础项目规范，不蒸馏历史文档。
- 完整迁移：读取 agent 可访问的历史文档和当前代码观察，建立项目知识基线。

初始化完成后，继续用自然语言提需求：

```text
新增订单关键词搜索。
```

Ruyi 会把 agent 路由到对应阶段，而不是让 agent 直接改代码。

## 日常流程

Ruyi 的正式开发流程是：

```text
contract -> plan -> implement -> test -> approve
```

各阶段职责：

- `contract`：澄清本次需求、范围、验收标准、影响面和测试方向。
- `plan`：在 contract 确认后制定实现方案、接口处理、测试策略和任务边界。
- `implement`：按 plan 修改代码，并在长任务中按需维护本地 checkpoint。
- `test`：记录验证结论、关键证据、风险和审批状态。
- `approve`：用户确认交付后，更新 test 中的 approval。
- `spec`：只有当本次经验具备长期价值时，才更新正式规范。

Ruyi 的目标不是增加文档负担，而是让 agent 不能绕过关键判断：需求是否清楚、方案是否存在、验证是否有证据、交付是否被确认。

## 成熟项目接入

成熟项目不需要倒灌历史 contract。Ruyi 从接入后的下一次变更开始形成正式 contract。

接入方式只有两种：

- 快速开始：只启用 Ruyi 流程和基础项目画像，历史知识在具体需求中逐步补充。
- 完整迁移：蒸馏现有业务文档和当前代码观察；当前业务事实进入 baseline contract，长期规则进入 `.ruyi/spec/`。

完整迁移读取外部文档时：

- 有 `agent-browser`、`fast-browser`、`bb-browser` 等浏览器工具时，可以让 agent 用浏览器工具查看外部文档后蒸馏。
- 没有浏览器工具时，用户应提供 Markdown 或纯文本等 agent 易读文件。
- 本地导出文件只作为蒸馏输入，不写入可提交 spec，也不保存不可复用的本地路径。

## 三层知识模型

Ruyi 有三层，不应该混在一起：

- `skills/`：Ruyi 本体，提供入口路由、阶段规则、产物结构和辅助脚本。
- `.ruyi/`：项目级知识层，放在业务项目根目录，记录当前项目事实、项目规范、需求、计划、测试和审批。
- `ruyi-team/`：团队级知识层，可选存在，用于沉淀跨项目复用的团队规范、工作流、测试方法论、审批规则和公共约束。

项目初始化时主要读取当前项目，不要求存在 `ruyi-team/`。团队层信息是在协作开发过程中由 agent 按需读取，用来和项目层规范合并判断。

推荐团队层结构：

```text
ruyi-team/
├── spec/
├── actions.md
└── README.md
```

其中：

- `spec/`：团队长期有效规范，例如前端工程规范、测试要求、组件设计原则、交互约束。
- `actions.md`：团队特殊动作，例如测试报告提交位置、审批系统地址、发布前检查方式。
- `README.md`：团队层说明，帮助 agent 判断这份团队知识适用范围。

团队层和项目层的边界：

- 项目层描述当前项目的具体事实。
- 团队层描述跨项目通用约束。
- 项目经验先沉淀到项目层，确认具备跨项目价值后，再提升到团队层。
- 当团队层与项目层存在同类规范时，agent 应合并判断；冲突时不能简单覆盖，应整理为待确认问题。

## 项目里会生成什么

初始化后的项目会包含：

```text
.ruyirc
.ruyi/
├── spec/
│   ├── INDEX.md
│   ├── project-overview.md
│   ├── project-structure.md
│   ├── development-baseline.md
│   ├── coding-baseline.md
│   ├── testing-baseline.md
│   ├── api.md
│   ├── open-questions.md
│   ├── docs-registry.md
│   ├── interview-bank.md
│   └── references/
│       ├── shared/
│       └── modules/
├── contracts/
├── plans/
├── tests/
├── INDEX.md
├── project-actions.md
└── README.md
.claude/
└── commands/
    └── ruyi.md
CLAUDE.md
```

其中：

- `spec/`：项目长期有效事实和规范。
- `spec/INDEX.md`：正式 spec 的唯一检索入口。
- `spec/development-baseline.md`：开发过程约束，例如必须运行的检查。
- `spec/coding-baseline.md`：代码编写约束。
- `spec/references/shared/`：跨模块共享规范。
- `spec/references/modules/`：具体模块、页面、功能或公共组件规范。
- `contracts/`：某次需求的设计与验收定义。
- `plans/`：围绕 contract 的开发计划、测试策略和任务边界。
- `tests/`：某次 contract 的正式验证结果和审批状态。
- `INDEX.md`：跨需求轻量索引，agent 进入项目时优先读取它。
- `project-actions.md`：项目特殊动作，例如发布前必须执行的检查。
- `.claude/` 与 `CLAUDE.md`：入口保护和手动兜底。

`tasks/`、`spec-candidates/` 等执行恢复点和待审候选默认只保留本地，不作为团队正式知识提交。

## Spec 怎么用

Ruyi 里的 spec 只保存长期有效的项目事实和规则，不保存一次性过程记录。

读取规则：

- 进入项目时先读 `.ruyi/INDEX.md`。
- 需要项目规范时先读 `.ruyi/spec/INDEX.md`。
- 只有路由到具体功能后，才读取相关 contract、plan、test 或模块 spec。
- 同一个功能、页面、公共组件的 spec 应放在同一个模块目录下，再按 `usage`、`internals`、`api`、`testing` 等主题拆文件。

沉淀规则：

- 当前需求的验收、实现方案和验证证据留在 `contract / plan / test`。
- 可长期复用的代码约束、组件约定、业务规则进入 `.ruyi/spec/`。
- 尚未确认的问题进入 `spec/open-questions.md`，不要塞进交付说明里。

## API 文档归位

Ruyi 不维护后端 API 文档本体，只维护三类信息：

- `.ruyi/spec/api.md`：长期 API 约定和权威源入口，例如 Swagger / Apifox / Yapi / OpenAPI 链接。
- `contract` 的接口范围：本次需求涉及哪些接口、新增、修改、复用或移除。
- `plan` 的接口对接：前端如何接 service、类型、mock、错误处理和状态管理。

完整请求响应结构应留在后端权威源；只有前端先行的临时定义可以短期写入 contract，并标注来源和替换时机。

## 常用说法

安装和初始化：

- “把这个 Vue 项目接入 Ruyi。”
- “快速开始接入。”
- “完整迁移接入，先帮我蒸馏这些项目文档。”

开发需求：

- “新增订单关键词搜索。”
- “修复订单列表筛选后分页不重置的问题。”
- “优化这个组件的渲染性能。”
- “做一次小重构，保持行为不变。”

流程推进：

- “继续。”
- “这个 contract 可以。”
- “按这个 plan 开始实现。”
- “这个交付通过。”
- “把这次经验沉淀一下。”

## 支持范围

当前主要面向前端项目：

- Vue
- Vite
- React
- Webpack
- 常见 JS/TS 组合

非前端项目默认不初始化，除非团队已经补充了对应项目类型的 Ruyi 规范。
