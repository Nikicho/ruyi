# Code Review Discipline

## 1. 定位

代码质量检视发生在 `ruyi-implement` 阶段，是编码循环的一部分。

它不属于 `ruyi-explain`，也不由 PM 审批替代。

## 2. 来源

本纪律内化自 Superpowers 的 `requesting-code-review` 和 `receiving-code-review`。

## 3. 检视范围

- 是否遵守 contract 和 plan 边界。
- 是否符合 project spec 和可用 team spec。
- 文件架构是否清晰。
- hooks、组件、服务、状态和工具函数拆分是否合理。
- 是否存在明显重复、隐式耦合或不必要复杂度。
- 是否存在未处理的失败态、空态、加载态或边界输入。
- 是否有必要的局部验证。

## 4. 反馈处理

- 明确正确的问题，直接修。
- 不明确的问题，先澄清。
- 不合理的问题，说明技术理由。
- 反馈导致需求变化时，返回 `ruyi-contract`。
- 反馈导致实施方案变化时，返回 `ruyi-plan`。

## 5. 输出要求

实现阶段结束时，应能给出简短代码质量结论，供 `ruyi-explain` 的代码质量简报引用。

`done` 状态 task 至少要记录：

- 是否遵守 contract 和 plan 边界。
- 本次主要文件架构、hooks、组件或服务拆分判断。
- 已完成的局部验证或无法验证原因。
- 已处理或待处理的 review 反馈。
