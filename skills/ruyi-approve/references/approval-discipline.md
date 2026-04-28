# Approval Discipline

## 1. 目标

approve 阶段负责记录 PM 对本次交付的接受、拒绝或有条件接受结论，并决定下一步回到哪个阶段。

审批不替代代码 review，也不替代测试验证。

本纪律内化自 Superpowers 的 `receiving-code-review` 和 `finishing-a-development-branch`：

- 吸收 `receiving-code-review` 的反馈处理纪律：先判断反馈是否明确、可执行、需要澄清，再决定返回阶段。
- 吸收 `finishing-a-development-branch` 的收尾意识：审批结论必须明确交付状态、条件、风险或下一步。
- 审批反馈面向交付接受度，不替代 implement 阶段的代码质量 review。

## 2. 硬门禁

- 没有 explain 或等价开发简报，不进入审批。
- explain 没有明确对应 contract、plan 和 test，不进入审批。
- 审批不能补写验证结果。
- 审批不修改 contract 的历史事实。
- 被拒绝或有条件接受时，必须明确返回阶段。

## 3. 审批结论

允许的结论：

- `approved`：接受交付，可进入知识沉淀判断。
- `changes-requested`：需要修改，必须返回 contract、plan、implement 或 test。
- `conditionally-approved`：有条件接受，必须写明条件和后续动作。
- `rejected`：拒绝交付，必须写明原因和返回阶段。

## 4. 最小流程

1. 读取 explain。
2. 确认对应 contract、plan 和 test。
3. 读取验证摘要和风险项。
4. 按 `../../../references/approval-schema.md` 记录审批结论。
5. 如果未通过，明确返回阶段。
6. 如果通过，进入 spec-evolve 判断。

## 5. 反模式

| 反模式 | 正确处理 |
| --- | --- |
| 没有 explain 直接问是否通过 | 先生成 explain |
| 把审批当代码 review | 代码 review 是工程质量活动，不是 PM 审批 |
| 审批时改需求范围 | 返回 contract 修订 |
| 审批时要求调整实施方案 | 返回 plan 修订 |
| 条件通过但不写条件 | 必须写明条件和后续动作 |
| 审批通过后直接改 spec | 先进入 spec-evolve 判断 |

## 6. 具体反模式（Anti-patterns）

### ❌ 用户说“通过，但上线前补个自动化”，我标 approved

**触发场景**：用户同意交付，但附带后置条件。

**你想做的事**：写 `approved`，然后在正文里备注条件。

**为什么错**：后续流程只看 `approval` 状态，会误判为可直接沉淀。

**正确做法**：标记 `conditionally-approved`，写明 `condition` 和 `return_stage`，让路由能识别条件未闭环。

### ❌ 用户说“不行”，我只记录 rejected

**触发场景**：PM 拒绝交付或要求重做。

**你想做的事**：只记录拒绝原因。

**为什么错**：没有返回阶段，agent 不知道该回 contract、plan、implement 还是 test。

**正确做法**：必须写 `return_stage`，并把原因转成可执行修改方向。

## 7. 检查清单

审批前检查：

- explain 是否存在？
- explain 是否对应明确 contract、plan 和 test？
- 验证摘要是否存在？
- 风险和未覆盖项是否透明？
- 审批结论是否属于允许枚举？
- 未通过时是否明确返回阶段？
