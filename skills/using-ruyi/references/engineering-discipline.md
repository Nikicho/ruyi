# Ruyi 工程纪律

## 1. 定位

工程纪律是 Ruyi 主流程的执行约束，用来保证 agent 不跳阶段、不凭感觉收口、不把一次性经验误沉淀成规范。

工程纪律不是独立流程，也不是独立 skill。它由 `using-ruyi` 负责注入阶段意识，并由各阶段 skill 在本地 `references/` 中落实。

本纪律内化自 Superpowers 的 `using-superpowers` 和 `verification-before-completion`：

- 吸收 `using-superpowers` 的入口强制性和技能选择纪律，但改写为 Ruyi 主流程路由，而不是通用 skill 发现器。
- 吸收 `verification-before-completion` 的证据要求，要求进入完成、说明、审批和沉淀前必须存在可追溯产物。
- 当 Ruyi 与 Superpowers 同时存在时，Ruyi 的阶段门禁优先，Superpowers 只作为通用工程方法来源。

## 2. 全局硬门禁

- 未初始化项目时，除 `ruyi-init` 外，不进入任何正式阶段。
- 没有需求定义锚点时，不进入开发计划。
- 没有 `plan` 或等价实施计划时，不进入正式需求实现；由 `using-ruyi` 明确路由的轻量维护模式除外。
- 没有 task 执行单元时，不进入正式测试。
- 没有 `test` 验证结果时，不生成正式 explain。
- 没有 explain 或等价交付说明时，不进入审批。
- explain 未审批通过时，不进入知识沉淀。
- 没有结果依据时，不进入知识沉淀。
- 用户说“继续”不能绕过上面的门禁，只能触发下一步检查。

## 3. 阶段纪律映射

| 阶段 | 本地纪律 |
| --- | --- |
| contract | `../../ruyi-contract/references/contract-discipline.md` |
| 修复类 contract | `../../ruyi-contract/references/debugging-discipline.md` |
| plan | `../../ruyi-plan/references/planning-discipline.md` |
| implement | `../../ruyi-implement/references/implementation-discipline.md` |
| code review | `../../ruyi-implement/references/code-review-discipline.md` |
| test | `../../ruyi-test/references/verification-discipline.md` |
| UI 自动化测试 | `../../ruyi-test/references/fast-browser-testing.md` |
| explain | `../../ruyi-explain/references/explain-discipline.md` |
| approve | `../../ruyi-approve/references/approval-discipline.md` |
| spec-evolve | `../../ruyi-spec-evolve/references/spec-evolution-discipline.md` |

## 4. 反模式

| 反模式 | 正确处理 |
| --- | --- |
| 用户给一句需求就开始写代码 | 先进入 contract，把目标和验收标准补齐 |
| 修复类问题直接猜代码位置 | 先确认现象、证据、复现或失败日志 |
| 把代码优化、代码微重构当成业务需求 | 先确认是否改变业务行为；不改变则进入 `ruyi-implement` 轻量维护模式 |
| contract 后直接编码 | 先进入 plan，明确测试策略、task 和写入边界 |
| 写完代码直接说完成 | 先进入 test，给出验证证据 |
| UI 需求只手工点一下 | test 阶段优先尝试 fast-browser，不能自动化时说明原因 |
| PM 审批当成代码 review | code review 属于 implement 阶段，审批只处理交付接受度 |
| 把一次任务记录复制进 spec | 只提炼稳定规则，不能搬运流水账 |
| 同时做需求、实现、审批、沉淀 | 按主流程分阶段推进 |
| 用户说“继续”，看到 `.ruyi/` 后直接编辑上次记得的文件 | 先执行 using-ruyi Ritual，读取活动需求候选和路由判定表 |
| 项目存在 `.ruyi/` 但 contract 不齐，先写代码再补 contract | 立即停止，回到 `ruyi-contract` 补齐并确认 |
| 轻量维护时发现用户可感知行为、业务规则或接口语义变化还继续改 | 停止并回到 `ruyi-contract` |
| Python 路由脚本不可用，于是凭感觉继续 | 按 `using-ruyi/SKILL.md` 的路由判定表直接读取 `.ruyi/` 推断 |
| 加载 `using-ruyi` 后把所有 contract 读了一遍 | 只读 INDEX；路由到具体 feature 后才读对应 contract 正文 |

## 5. 最小自检

进入任何阶段前，先回答：

- 当前项目是否已初始化？
- 当前阶段的前置产物是否存在？
- 当前请求属于主流程哪个阶段？
- 是否需要读取 project spec 或 team spec？
- 如果现在继续，是否会跳过一个硬门禁？
- 如果用户只说“继续”，是否能唯一定位当前活动需求？
- 当前阶段产物的状态是否允许进入下一阶段？

如果任何答案不确定，停止正式执行并补齐缺失项。

## 6. 活动需求定位

当用户只说“继续”且没有提供 `module / feature / date` 时，agent 应先定位当前活动需求：

1. 优先读取 `.ruyi/INDEX.md`。
2. INDEX 不存在时，只扫描 `.ruyi/contracts/`、`.ruyi/explain/` 的目录名，不读文件正文。
3. 如果只有一个候选，继续检查该候选的下一阶段。
4. 如果存在多个候选，停止正式执行，请用户确认要继续哪一个。
5. 不允许凭聊天记忆直接假设当前需求。

候选必须能解析出 `module / feature / date`。

## 7. 具体反模式：过度读取

### ❌ 加载 using-ruyi 后把所有 contract 读了一遍

**触发场景**：用户说“修个 bug”，agent 为了“了解项目背景”读取了 `.ruyi/contracts/` 下所有文件。

**为什么错**：

- 浪费上下文，真实项目里可能放大 10 倍以上。
- 增加误引用风险，agent 可能基于无关 contract 推理出错误背景。
- 长对话更早触达上下文上限。

**正确做法**：

- 只读 INDEX。
- 按 INDEX 的“业务目标”判断相关性。
- 路由到具体 feature 后才读对应 contract 正文。
- 其它 feature 的 contract 一律不读，除非用户明确指定跨 feature 引用。
