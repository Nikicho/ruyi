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
- contract 存在 `## 接口范围` 时，plan 必须写 `## 接口对接`。

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

## 5. 接口对接策略

plan 的 `## 接口对接` 只回答前端怎么接，不重新定义后端 API。

必须覆盖：

- 调用层：新增、修改或复用哪个 api/service 函数。
- 类型定义：生成或手写位置，临时定义来源。
- Mock 策略：是否需要 mock、放在哪里、何时删除。
- 错误处理：全局 interceptor、局部空态、toast 或重试。
- 状态管理：是否缓存、使用哪个 store、hook 或组件状态。

禁止把完整请求响应字段表从 contract 复制到 plan。

## 6. 重评模式

类型 B 中途变更后，plan 不允许只追加新步骤。必须先评估现有步骤、顺序与写入边界；旧本地 checkpoint 与新 plan 不一致时删除并按当前 plan 重建。

## 7. 反模式

| 反模式 | 正确处理 |
| --- | --- |
| contract 还不清楚就开始拆 task | 返回 `ruyi-contract` 补齐需求 |
| 把实现猜测写成业务规则 | 从 plan 移除，必要时回到 contract |
| 只写“修改页面”而没有写入范围 | 明确文件、模块或责任边界 |
| 没有测试策略就进入编码 | 先补齐验证方式 |
| 为了并行而强行拆任务 | 保持单 task，降低协调成本 |
| contract 有接口范围但 plan 没有接口对接 | 补齐 service、类型、mock、错误处理、状态管理 |
| 中途变更只新增 task 不评估旧 task | 先评估旧 task 状态，再新增或 supersede |

## 8. 进入 implement 的条件

- contract 明确。
- 测试策略明确。
- task 拆分足够执行。
- 写入范围和风险已说明。
- 用户已确认 plan，或已有等价实施计划。
