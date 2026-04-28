![Ruyi 首页图](./assets/ruyi-home.png)

# Ruyi 如意

> A frontend dev contract framework for AI coding agents.
> Forces "requirement -> plan -> implement -> verify -> brief -> approve -> distill" as a hard pipeline so agents cannot skip stages or fake completion.

Ruyi 是一个面向前端项目的 AI 协作开发框架，以 code agent skill 包的形式提供固定开发流程、项目知识沉淀和轻量脚本辅助。

它不是 CLI 产品。用户不需要记命令；日常使用时由 agent 通过 `using-ruyi` 判断当前项目状态、识别用户意图，并路由到对应阶段。

## 核心目标

- 让前端需求从“口头描述”进入可追踪的 contract。
- 让编码、验证、开发简报、审批和知识沉淀按固定阶段推进。
- 让项目长期规则沉淀到 `.ruyi/spec/`，让单次需求留在 `contract / task / test / explain`。
- 让 agent 不跳过需求定义、验证证据和审批确认。

## 支持范围

首版只支持前端项目：

- Vue
- Vite
- React
- Webpack
- 常见 JS/TS 组合

非前端项目应拒绝初始化。

## Skill 结构

```text
skills/
├── using-ruyi
├── ruyi-init
├── ruyi-contract
├── ruyi-plan
├── ruyi-implement
├── ruyi-test
├── ruyi-explain
├── ruyi-approve
├── ruyi-spec-evolve
└── ruyi-spec-merge
```

`using-ruyi` 是入口 skill。其他 skill 只负责各自阶段。

## 主流程

Ruyi 固定主流程：

1. 初始化：生成 `.ruyirc` 和 `.ruyi/`。
2. 需求定义：生成 `contract`。
3. 开发计划：生成 `plan` 与必要 `task`。
4. 编码实现：代码变更、实现自检和代码质量结论。
5. 测试验证：生成 `test`。
6. 开发简报：生成 `explain`。
7. 审批：更新 explain 中的 `approval`。
8. 知识沉淀：生成 `spec-candidate`。

项目不能改写主流程，只能通过 `.ruyi/project-actions.md` 追加项目特殊动作。

## 项目层结构

初始化后的项目会包含：

```text
.ruyirc
.ruyi/
├── spec/
├── contracts/
├── plans/
├── tasks/
├── tests/
├── explain/
├── spec-candidates/
├── workspace/
├── project-actions.md
└── README.md
```

其中：

- `spec/`：项目长期有效事实和规范。
- `contracts/`：某次需求的设计与验收定义。
- `plans/`：围绕 contract 的开发计划、测试策略和 task 拆分。
- `tasks/`：围绕 plan 的执行单元。
- `tests/`：某次 contract 的正式验证结果。
- `explain/`：面向 PM 的开发简报。
- `spec-candidates/`：审批通过后的知识沉淀候选。
- `workspace/`：临时过程材料，默认不提交正式内容。

## 使用方式

把 `skills/` 目录链接到目标 code agent 可用的 skills 目录后，在项目中对 agent 说自然语言目标即可，例如：

- “把这个 Vue 项目接入 Ruyi。”
- “新增订单关键词搜索。”
- “继续。”
- “生成开发简报。”
- “这个交付通过。”
- “把这次经验沉淀一下。”

agent 应先加载 `using-ruyi`，再根据项目状态和用户意图路由到具体阶段。

## 安装

Ruyi 仿照 Superpowers 的安装思路：保留完整 Ruyi 目录，只把 `skills/` 目录链接到目标 code agent 可发现的 skills 目录。

本地开发安装：

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\ruyi" "D:\AIWorks\ruyi\skills"
```

安装后重启 code agent。

详细说明见 [docs/install.md](docs/install.md)。

## 入口路由

路由由 agent 按 `using-ruyi/SKILL.md` 的路由判定表直接判断。Python 脚本只是可选复核工具，不是必经入口。

可选复核：

```powershell
python .\skills\using-ruyi\scripts\route_request.py --project <project> --intent continue --module <module> --feature <feature> --date <YYYY-MM-DD>
```

脚本只判断下一阶段，不生成正式产物。自然语言意图仍由 agent 判断。Python 不可用时，agent 必须按 schema 和路由判定表直接读取 `.ruyi/`，不能绕过门禁。

## 阶段脚本

当前最小脚本链：

```text
ruyi-init        初始化项目
ruyi-contract    创建 contract
ruyi-plan        创建 plan
ruyi-implement   创建 task
ruyi-test        创建 test
ruyi-explain     创建 explain
ruyi-approve     更新 explain 审批状态
ruyi-spec-evolve 创建 spec-candidate
ruyi-spec-merge  周期性人工合入 spec-candidate
```

这些脚本用于稳定写入协议产物，不替代 agent 的需求澄清、编码实现、测试判断和审批沟通。

运行时 fallback 见 [references/script-runtime-protocol.md](references/script-runtime-protocol.md)。

## 验证

运行所有 Python 脚本测试：

```powershell
python -m unittest discover .\skills\using-ruyi\scripts\tests -v
python -m unittest discover .\skills\ruyi-init\scripts\tests -v
python -m unittest discover .\skills\ruyi-contract\scripts\tests -v
python -m unittest discover .\skills\ruyi-plan\scripts\tests -v
python -m unittest discover .\skills\ruyi-implement\scripts\tests -v
python -m unittest discover .\skills\ruyi-test\scripts\tests -v
python -m unittest discover .\skills\ruyi-explain\scripts\tests -v
python -m unittest discover .\skills\ruyi-approve\scripts\tests -v
python -m unittest discover .\skills\ruyi-spec-evolve\scripts\tests -v
```

验证 fixture 前端构建：

```powershell
cd .\fixtures\vue-vite-basic
npx vite build
```

注意：fixture 的 `npm run build` 当前受 `vue-tsc` 与环境兼容问题影响，`npx vite build` 可通过。

## 当前状态

首版最小主流程已经跑通：

```text
init -> contract -> plan -> task/implement -> test -> explain -> approve -> spec-candidate
```

fixture 中已经用两个示例需求验证：

- `board/card-status-filter`
- `orders/order-keyword-search`

同时包含失败/退回 fixture：

- `board/missing-acceptance`：contract 缺验收标准，阻止进入 plan。
- `orders/orphan-plan`：孤立 plan，阻止进入 implement。
- `board/failed-test`：test failed，阻止进入 explain。
- `orders/no-test-evidence`：explain 风险缺少 test 证据，lint 拒绝。
- `board/premature`：approval pending，阻止 spec-evolve。
- `board/copy-tweak`：tiny 分档示例，完成 contract -> test 的轻量路径。

## 后续重点

- 继续在真实项目中压测 `tiny / standard / large` 分档边界。
- 为高频写入脚本补充 `.mjs` 等价实现，进一步降低 Python 环境依赖。
- 将 fast-browser case/flow/site 与 `ruyi-test` 深度联动。
- 建立自动化的 EXPECTED fixture 评分机制。
