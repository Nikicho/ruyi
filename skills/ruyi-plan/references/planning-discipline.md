# Planning Discipline

## 1. 来源

本纪律内化自 Superpowers 的 `writing-plans`、`test-driven-development`、`dispatching-parallel-agents` 和 `subagent-driven-development`。

Ruyi 不依赖这些 skill 运行，但吸收其计划拆分、验证优先和并行边界思想。

## 2. 核心要求

- 先确认 contract，再写 plan。
- 先明确测试策略，再设计实施步骤。
- 每个 task 都必须能独立说明目标、范围、写入边界和完成条件。
- 不把未确认需求写进 plan。
- 不把 plan 写成代码实现流水账。

## 3. 测试用例映射

contract 中的自然语言 test case 应映射为：

- 自动化验证：可用现有测试、构建、lint 或 fast-browser 验证。
- 手工验证：暂时无法自动化，但可明确操作路径和预期结果。
- 待确认验证：测试条件不清，需要返回 contract 或请求用户确认。

## 4. Task 拆分原则

- 优先按用户可感知的交付切片拆分。
- 其次按明确的文件或责任边界拆分。
- 不为形式化并行而拆分 task。
- 多 task 必须说明依赖顺序。
- 可能并行的 task 必须写明互不重叠的写入范围。

## 5. 反模式

| 反模式 | 正确处理 |
| --- | --- |
| contract 还不清楚就开始拆 task | 返回 `ruyi-contract` 补齐需求 |
| 把实现猜测写成业务规则 | 从 plan 移除，必要时回到 contract |
| 只写“修改页面”而没有写入范围 | 明确文件、模块或责任边界 |
| 没有测试策略就进入编码 | 先补齐验证方式 |
| 为了并行而强行拆任务 | 保持单 task，降低协调成本 |

## 6. 进入 implement 的条件

- contract 明确。
- 测试策略明确。
- task 拆分足够执行。
- 写入范围和风险已说明。
- 用户已确认 plan，或已有等价实施计划。
