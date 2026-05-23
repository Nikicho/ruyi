---
name: using-ruyi
description: Frontend project Ruyi pipeline router. Use whenever the user asks to add a feature, fix a bug, refactor, optimize code, implement, test, generate a dev brief, approve a delivery, distill knowledge, infer specs from code, amend an ongoing requirement, or continue ongoing work in a frontend project. Common Chinese triggers: "继续"、"新增"、"修复"、"重构"、"代码优化"、"代码微重构"、"代码反推spec"、"梳理组件规范"、"接入Ruyi"、"开发简报"、"通过"、"沉淀"、"再加"、"改一下". Common English triggers: "continue", "add feature", "fix", "refactor", "optimize", "infer spec", "implement", "test", "approve", "distill", "also add", "change". MUST load before any code edit in projects containing .ruyi/ or .ruyirc.
---

# Using Ruyi

## 0. 加载即执行（Ritual）

当本 skill 被加载时，立即按顺序执行：

1. 检查当前工作目录或用户指定项目根目录是否存在 `.ruyi/` 或 `.ruyirc`。
2. 若存在：声明 `Ruyi 主流程已激活`；先读取 `.ruyirc` 的 `schema_version`。低于当前 schema 时立即路由到 `ruyi-upgrade`，升级前不得继续阶段流转；schema 当前时再读取 `.ruyi/INDEX.md`。**禁止读取 contract / plan / explain 文件正文**。
   - INDEX 不存在时，仅扫描 `contracts/` 与 `explain/` 的目录名，不读文件正文。
   - 列出最多 5 条活动需求候选时，只使用 INDEX 的元信息和一句话业务目标。
3. 若不存在：判断用户意图是否为初始化；不是初始化则退出 Ruyi 上下文。若是初始化，必须先让用户选择“快速开始”或“完整迁移”，未选择前不得运行 `init_write.py` 或写入 `.ruyi/`。
4. 在完成上述判断前，不得执行任何代码编辑、文件写入或项目内 shell 命令。
5. 上下文预算：路由确定前，最多读取 `.ruyi/INDEX.md` 与 1 个目标 module 的目录列表。
   - 不允许读取多个 feature 的 contract / plan / explain 正文。
   - 只有路由确定到具体 feature 后，才读取该 feature 的最新 contract；成熟项目如果存在同 module 的 baseline contract，可同时读取该 baseline 作为业务背景。
   - 跨 feature 引用必须由用户明确指定，不靠扫描自动发现。

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
4. 未初始化时，只能进入 `ruyi-init`，并且必须先完成接入方式选择。
5. 已初始化时，先检查 `schema_version`；低于当前版本时先进入 `ruyi-upgrade`，完成后再处理原意图。
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
| 升级已有 Ruyi 项目结构 | `../ruyi-upgrade/SKILL.md` |
| 定义新功能、修复、业务重构目标 | `../ruyi-contract/SKILL.md` |
| 代码优化、代码微重构、无行为变化维护 | `../ruyi-implement/SKILL.md`（轻量维护模式） |
| 根据已确认需求制定开发计划 | `../ruyi-plan/SKILL.md` |
| 根据已确认计划编码实现 | `../ruyi-implement/SKILL.md` |
| 验证实现结果 | `../ruyi-test/SKILL.md` |
| 生成开发简报 | `../ruyi-explain/SKILL.md` |
| 记录审批结论 | `../ruyi-approve/SKILL.md` |
| 从现有代码反推本地规范候选 | `../ruyi-spec-discover/SKILL.md` |
| 提炼项目或团队规范候选 | `../ruyi-spec-evolve/SKILL.md` |
| 周期性合入规范候选 | `../ruyi-spec-merge/SKILL.md` |

## 5. 意图映射

agent 负责把用户自然语言映射为下列 intent：

| intent | 触发场景 |
| --- | --- |
| `init` | 初始化、接入 Ruyi、创建 `.ruyi` |
| `upgrade` | 更新 Ruyi 后规整已有 `.ruyi` 文档结构 |
| `contract` | 新功能、修复、业务重构、需求澄清、验收标准、自然语言测试用例 |
| `maintain` | 代码优化、代码微重构、抽函数、拆组件、去重复、类型收紧、lint 整理，且不改变业务行为 |
| `plan` | 已有 contract，要制定测试策略、开发计划或拆 task |
| `implement` | 已有 plan，要开始编码、执行 task 或做代码自检 |
| `test` | 验证、测试、构建、浏览器检查 |
| `explain` | 生成开发简报、交付说明 |
| `approve` | 审批、通过、驳回、要求修改 |
| `spec-discover` | 从现有代码反推 spec、梳理组件规范、整理模块约定、生成本地候选 |
| `spec-evolve` | 沉淀规范、形成候选、提炼经验 |
| `continue` | 用户说“继续”、下一步、往后走 |
| `amend` | 中途变更：再加、再改、改成、不要、换种方式、忘了说、also add、also change |

用户只需要描述目标，不需要记这些 intent。

## 6. 路由判定表

agent 必须按下列顺序判断，命中后立即停止继续向后判断：

路由判断时的读取规则：

- 只读取与当前 `module / feature` 匹配的目录；不允许读取兄弟 feature 的产物正文。
- 用户未指明 `module / feature` 且 INDEX 无法唯一定位时，向用户询问，不靠扫描全部 contract 推断。
- 判断“是否缺少 contract”时，只检查目标路径下的文件是否存在，不读取文件正文。
- baseline contract 只提供成熟项目当前业务事实背景，不能替代本次变更 contract。
- 判断“是否已有审批通过”时，只读取目标 feature 最新 explain 的 frontmatter 或摘要信息；不得改写已审批事实。

变更意图优先判断：

| 条件 | 下一步 | 标准处理 |
| --- | --- | --- |
| 用户消息含“再加 / 改一下 / 不要 X 了 / 换种方式 / 忘了说 / also add / also change”等变更意图，且已有进行中的 contract | 变更分类决策 | 先按 A/B/C/D 决策树判断，向用户确认分类后再路由 |
| 类型 A 已确认 | `ruyi-contract`（修订模式） | 原地修订 + `## 修订记录` |
| 类型 B 已确认 | `ruyi-contract`（修订模式）→ `ruyi-plan`（重评模式） | contract 修订后重评 plan/task/test |
| 类型 C 已确认 | `ruyi-contract`（新建日期模式） | 旧 contract 加 `superseded_by` |
| 类型 D 已确认 | `ruyi-contract`（返工重开模式） | 重开同一 contract，记录返工原因并重置当前交付状态 |

| 条件 | 下一阶段 | 标准处理 |
| --- | --- | --- |
| 项目缺少 `.ruyi/` 或 `.ruyirc` | `ruyi-init` | 先询问接入方式：快速开始 / 完整迁移；未选择前不得写入 `.ruyi/` |
| 项目 `schema_version` 低于当前版本 | `ruyi-upgrade` | 先机械迁移结构；废弃目录删除另行确认 |
| 代码优化 / 代码微重构，且不改变用户可感知行为、业务规则、接口语义、状态语义、权限、路由或验收标准 | `ruyi-implement` | 进入轻量维护模式，不要求 contract / plan / task |
| 缺少 contract | `ruyi-contract` | 拒绝 plan/implement/test/explain/approve/spec-evolve |
| contract `status` 不是 `confirmed` | `ruyi-contract` | 要求先确认需求 |
| contract `size: tiny` 且需继续 | `ruyi-implement` | tiny 跳过 plan/task，直接进入实现 |
| contract 非 tiny 且缺少 plan | `ruyi-plan` | 要求先制定计划 |
| plan `status` 不是 `confirmed` | `ruyi-plan` | 要求先确认计划 |
| 存在本地 `in-progress` task checkpoint 且用户要求继续 | `ruyi-implement` | 恢复本地执行进度；task 不作为正式测试门禁 |
| 缺少 test | `ruyi-test` | 要求先生成验证证据 |
| test `result: failed` | `ruyi-test` | 拒绝 explain，返回修复或补充验证 |
| tiny 且 test 通过或带备注通过 | 完成或按需 explain | tiny 默认不强制 explain/approve/spec-candidate |
| 非 tiny 且缺少 explain | `ruyi-explain` | 要求生成开发简报 |
| explain `approval: changes-requested` 且有 `return_stage` | 对应返回阶段 | 按审批结论退回 |
| explain `approval` 不是 `approved` | `ruyi-approve` | 要求审批 |
| explain `approval: approved` | 完成 | 主流程闭环；存在可复用规则时按需进入 `ruyi-spec-evolve` |

禁止行为：

- 不允许凭聊天记忆绕过上述表。
- 不允许为通过门禁自动补造缺失产物。
- 不允许把 tiny 当成绕过验证的理由；tiny 也必须有 contract、implement 和 test 证据。

## 7. 快捷路径

### fix 意图

触发短语：“修个 bug”、“这里坏了”、“按钮点不了”、“不生效”、“报错”等。

执行：

1. 仅读 INDEX 定位是否已有相关 feature。
2. 已有相关 feature 时，只读该 feature 最新 contract，进入 `ruyi-contract` 修订模式。
3. 没有相关 feature 时，直接进入 `ruyi-contract` 创建新的 fix contract。
4. **禁止**读取无关 module 的 contract / plan / explain 正文。

### maintain 意图

触发短语：“代码优化”、“代码微重构”、“无行为变化重构”、“抽函数”、“拆组件”、“去重复”、“类型收紧”、“lint 整理”等。

执行：

1. 先确认本次不改变用户可感知行为、业务规则、接口语义、状态语义、权限、路由或验收标准。
2. 若会改变上述任一项，回到 `ruyi-contract`。
3. 若确认只是维护型代码变更，进入 `ruyi-implement` 轻量维护模式。
4. 轻量维护模式不要求 contract / plan / task，但必须有维护目标、写入边界、自检和验证结果。
5. 收口时只识别是否存在可沉淀规范；如有，提示用户后续单独进入 spec-evolve，不自动生成 spec-candidate。

### amend 意图

触发短语：“再加”、“再改”、“加一个”、“改成”、“不要”、“换”、“调整”、“还有”、“忘了说”、“补一下”。

执行：

1. 先判断当前需求是否已有 `approved` 的 explain；若有，归为类型 D：重开同一 contract 并记录返工原因。
2. 再判断是否改变用户故事核心、业务规则、已确认验收标准或需求类型；若是，归为类型 C。
3. 再判断是否改变需求范围、接口范围、接口对接或影响 task；若是，归为类型 B。
4. 其它不影响下游的文案、样式、轻微交互微调归为类型 A。
5. 必须先把分类和处理路径说给用户确认；用户未确认前不落盘、不改代码。

## 8. 脚本调用（可选复核）

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

## 9. 必读参考

- `references/main-flow.md`
- `references/knowledge-evolution.md`
- `references/index-protocol.md`
- `references/script-runtime-protocol.md`
- `references/spec-schema.md`
- `references/contract-schema.md`
- `references/plan-schema.md`
- `references/task-schema.md`
- `references/explain-schema.md`
- `references/engineering-discipline.md`
