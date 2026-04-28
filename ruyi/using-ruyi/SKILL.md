---
name: using-ruyi
description: MUST load this skill FIRST in any conversation that touches a project containing .ruyi/ or .ruyirc, before any code edit, file write, or shell command in that project. Also load when the user mentions Ruyi explicitly, or asks to initialize a frontend project for AI-assisted development.
---

# Using Ruyi

## 0. 加载即执行（Ritual）

当本 skill 被加载时，立即按顺序执行：

1. 检查当前工作目录或用户指定项目根目录是否存在 `.ruyi/` 或 `.ruyirc`。
2. 若存在：声明 `Ruyi 主流程已激活`，读取 `.ruyi/INDEX.md` 头部或最近产物，列出最多 5 条活动需求候选。
3. 若不存在：判断用户意图是否为初始化；不是初始化则退出 Ruyi 上下文。
4. 在完成上述判断前，不得执行任何代码编辑、文件写入或项目内 shell 命令。

如果你跳过这一步直接编辑代码、运行命令或生成阶段产物，你违反了 Ruyi 主流程。停止当前动作，重新进入 Ritual。

## 1. 定位

`using-ruyi` 是 Ruyi 的独立入口 skill，负责识别用户意图、检查项目状态，并把请求路由到正确的 Ruyi 子 skill。

它不直接生成 `contract / task / explain`，不直接编码，不直接审批，也不独立沉淀知识。

## 2. 核心原则

- Ruyi 由本体固定提供主流程。
- 当前项目根目录存在 `.ruyi/` 或 `.ruyirc` 时，Ruyi 是该项目开发协作的主流程。
- 用户优先描述功能、问题或交付目标，不需要记忆命令。
- `spec` 不是独立 skill，而是默认注入各阶段的规则层。
- 项目只能通过 `.ruyi/project-actions.md` 追加项目特有操作，不能改写 Ruyi 主流程。
- 通用工程纪律由 Ruyi references 内化提供，Ruyi 负责阶段门禁、文档对象和知识沉淀。
- 如果同时安装 Superpowers，Superpowers 只能作为通用方法来源，不能覆盖 Ruyi 的阶段门禁。

## 3. 入口判断

1. 检查当前项目根目录是否存在 `.ruyi/` 或 `.ruyirc`。
2. 若存在，优先使用 Ruyi 主流程。
3. 判断当前项目是否已初始化。
4. 未初始化时，只能进入 `ruyi-init`。
5. 已初始化时，先判断用户意图。
6. 如果用户只说“继续”，先定位当前活动需求；无法唯一定位时请用户确认。
7. 如果能识别 `module / feature / date`，优先按本文件“路由判定表”推断下一阶段；可选使用 `scripts/route_request.py` 复核。
8. 路由到对应子 skill，并要求子 skill 执行自身门禁。

硬门禁：

- 除 `ruyi-init` 外，任何 Ruyi 子 skill 都要求项目已初始化。
- 项目存在 `.ruyi/` 或 `.ruyirc` 时，除非用户明确要求不用 Ruyi，否则不应绕过 Ruyi 主流程。
- 单纯语法问答、资料查询、与当前项目无关的闲聊，可以不进入 Ruyi。
- 前置条件不满足时，停止正式执行，说明缺失项，并引导回前一阶段。
- 产物存在但状态不允许时，停止正式执行，回到对应阶段处理。
- 无法唯一定位当前活动需求时，不凭聊天记忆猜测。

## 4. 子 Skill 路由

| 用户意图 | 子 skill |
| --- | --- |
| 初始化已有前端项目 | `../ruyi-init/SKILL.md` |
| 定义新功能、修复、重构目标 | `../ruyi-contract/SKILL.md` |
| 根据已确认需求制定开发计划 | `../ruyi-plan/SKILL.md` |
| 根据已确认计划编码实现 | `../ruyi-implement/SKILL.md` |
| 验证实现结果 | `../ruyi-test/SKILL.md` |
| 生成开发简报 | `../ruyi-explain/SKILL.md` |
| 记录审批结论 | `../ruyi-approve/SKILL.md` |
| 提炼项目或团队规范候选 | `../ruyi-spec-evolve/SKILL.md` |
| 周期性合入规范候选 | `../ruyi-spec-merge/SKILL.md` |

## 5. 意图映射

agent 负责把用户自然语言映射为下列 intent：

| intent | 触发场景 |
| --- | --- |
| `init` | 初始化、接入 Ruyi、创建 `.ruyi` |
| `contract` | 新功能、修复、重构、需求澄清、验收标准、自然语言测试用例 |
| `plan` | 已有 contract，要制定测试策略、开发计划或拆 task |
| `implement` | 已有 plan，要开始编码、执行 task 或做代码自检 |
| `test` | 验证、测试、构建、浏览器检查 |
| `explain` | 生成开发简报、交付说明 |
| `approve` | 审批、通过、驳回、要求修改 |
| `spec-evolve` | 沉淀规范、形成候选、提炼经验 |
| `continue` | 用户说“继续”、下一步、往后走 |

用户只需要描述目标，不需要记这些 intent。

## 6. 路由判定表

agent 必须按下列顺序判断，命中后立即停止继续向后判断：

| 条件 | 下一阶段 | 标准处理 |
| --- | --- | --- |
| 项目缺少 `.ruyi/` 或 `.ruyirc` | `ruyi-init` | 只允许初始化或退出 Ruyi 上下文 |
| 缺少 contract | `ruyi-contract` | 拒绝 plan/implement/test/explain/approve/spec-evolve |
| contract `status` 不是 `confirmed` | `ruyi-contract` | 要求先确认需求 |
| contract `size: tiny` 且需继续 | `ruyi-implement` | tiny 跳过 plan/task，直接进入实现 |
| contract 非 tiny 且缺少 plan | `ruyi-plan` | 要求先制定计划 |
| plan `status` 不是 `confirmed` | `ruyi-plan` | 要求先确认计划 |
| 非 tiny 且缺少 done task | `ruyi-implement` | 要求先执行 task 并自检 |
| 缺少 test | `ruyi-test` | 要求先生成验证证据 |
| test `result: failed` | `ruyi-test` | 拒绝 explain，返回修复或补充验证 |
| tiny 且 test 通过或带备注通过 | 完成或按需 explain | tiny 默认不强制 explain/approve/spec-candidate |
| 非 tiny 且缺少 explain | `ruyi-explain` | 要求生成开发简报 |
| explain `approval: changes-requested/rejected` 且有 `return_stage` | 对应返回阶段 | 按审批结论退回 |
| explain `approval: conditionally-approved` | `ruyi-approve` | 先处理条件，不进入沉淀 |
| explain `approval` 不是 `approved` | `ruyi-approve` | 要求审批 |
| 缺少 spec-candidate | `ruyi-spec-evolve` | 判断是否沉淀候选 |
| spec-candidate 已存在 | 完成 | 主流程闭环 |

禁止行为：

- 不允许凭聊天记忆绕过上述表。
- 不允许为通过门禁自动补造缺失产物。
- 不允许把 tiny 当成绕过验证的理由；tiny 也必须有 contract、implement 和 test 证据。

## 7. 脚本调用（可选复核）

当请求对应某个具体 contract，并且能识别 `module / feature / date` 时，先运行：

```bash
python <skills-dir>/using-ruyi/scripts/route_request.py --project <project> --intent <intent> --module <module> --feature <feature> --date <YYYY-MM-DD>
```

如果项目未初始化，可以只传：

```bash
python <skills-dir>/using-ruyi/scripts/route_request.py --project <project> --intent init
```

如果用户只说“继续”，且当前对话无法可靠识别 `module / feature / date`，可以运行：

```bash
python <skills-dir>/using-ruyi/scripts/route_request.py --project <project> --intent continue
```

脚本职责：

- 检查项目是否初始化。
- 检查当前阶段所需的前置产物。
- 检查关键产物状态是否允许进入下一阶段。
- 在 `continue` 缺少对象时发现候选活动需求。
- 返回应进入的 Ruyi 阶段、子 skill 和阻塞项。
- 不生成任何正式产物。
- 不替代 agent 对用户意图的理解。
- `route_request.py` 是可选复核工具，不是 Ruyi 的唯一入口；当 Python 不可用时，agent 必须按“路由判定表”直接读取 `.ruyi/` 推断。

## 8. 必读参考

- `../references/main-flow.md`
- `../references/knowledge-evolution.md`
- `../references/index-protocol.md`
- `../references/script-runtime-protocol.md`
- `../references/spec-schema.md`
- `../references/contract-schema.md`
- `../references/plan-schema.md`
- `../references/task-schema.md`
- `../references/explain-schema.md`
- `references/engineering-discipline.md`
