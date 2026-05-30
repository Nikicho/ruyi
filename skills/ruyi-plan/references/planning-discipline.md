# Planning Discipline

## 1. 来源

本纪律内化自 Superpowers 的 `writing-plans`、`test-driven-development`、`dispatching-parallel-agents` 和 `subagent-driven-development`。

Ruyi 不依赖这些 skill 运行，但吸收其计划拆分、验证优先和并行边界思想。

## 2. 核心要求

- 先确认 contract，再写 plan。
- 先确认方案、文件架构和 spec 约束，再进入实现。
- Task 拆分只写实际实施步骤标题；详细步骤、完成条件和进度进入 implement 阶段本地 task。
- 不把未确认需求写进 plan。
- 不把 plan 写成代码实现流水账。
- contract 存在 `## 接口范围` 时，plan 必须写 `## 接口与数据`。
- plan 若发现方案选择会改变用户行为、业务规则、接口范围或验收标准，必须返回 contract，不允许在 plan 中隐式扩展需求。
- 读取项目规范时，先读 `.ruyi/spec/INDEX.md`，再按索引读取相关 spec。

## 3. 测试用例映射

contract 中的自然语言 test case 应映射为：

- 自动化验证：可用现有测试、构建、lint 或 fast-browser 验证。
- 手工验证：暂时无法自动化，但可明确操作路径和预期结果。
- 待确认验证：测试条件不清，需要返回 contract 或请求用户确认。

## 4. 文件/模块架构原则

- 展示最终功能的文件或模块落点。
- 每个条目应标注 `new / modify / reuse / unchanged / candidate` 之一。
- 文件架构同时承担写入边界表达，不再单独写“写入范围”章节。
- 明确不改的关键全局模块，可以在本节用一行“不改：...”说明。

## 5. Task 拆分原则

- Task 拆分是实际实施步骤标题列表，不是抽象层级。
- 每个标题应描述一个可执行步骤，例如“扩展订单列表查询参数”“接入搜索输入组件”。
- 不写详细函数修改、完成条件、写入边界和检查清单。
- 顺序即推荐实施顺序。
- 详细执行拆解由 implement 阶段本地 task 生成，不提交 git。

## 6. 接口与数据

plan 的 `## 接口与数据` 只回答能否开始开发所需的最小信息，不重新定义后端 API。

必须覆盖：

- 接口：新增、修改、复用或不涉及。
- 入参：本次新增或复用的关键参数。
- 出参：是否变化。
- 状态：关键前端状态或缓存变化。
- 异常：沿用现有处理还是新增处理。

禁止把完整请求响应字段表从 contract 复制到 plan。

## 7. Spec 约束

Spec 约束必须是短清单，每条包含文件和短标签：

```md
- `.ruyi/spec/coding-baseline.md`：代码基线
- `.ruyi/spec/references/shared/components/search-input.md`：搜索组件约定
```

标签只说明为什么要读，不写长解释。

## 8. 重评模式

类型 B 中途变更后，plan 不允许只追加新步骤。必须先评估现有方案、文件架构、接口与数据、spec 约束、task 标题是否仍有效；旧本地 checkpoint 与新 plan 不一致时删除并按当前 plan 重建。

## 9. 反模式

| 反模式 | 正确处理 |
| --- | --- |
| contract 还不清楚就开始拆 task | 返回 `ruyi-contract` 补齐需求 |
| 把实现猜测写成业务规则 | 从 plan 移除，必要时回到 contract |
| 只写“修改页面”而没有文件架构 | 明确文件、模块或责任边界 |
| 没有测试策略就进入编码 | 先补齐验证方式 |
| Task 写成“查询层/页面层/验证层” | 改成实际实施步骤标题 |
| Task 写了详细函数步骤 | 下沉到 implement 本地 task |
| contract 有接口范围但 plan 没有接口与数据 | 补齐接口、入参、出参、状态、异常 |
| 中途变更只新增 task 不评估旧 task | 先评估旧 task 状态，再新增或 supersede |
| plan 中顺手扩大需求范围 | 返回 contract 重新确认业务边界 |

## 10. 进入 implement 的条件

- contract 明确。
- 方案概述明确。
- 文件/模块架构明确。
- 接口与数据足以开始开发。
- Spec 约束清楚且有短标签。
- Task 标题能指导 implement 生成本地 task。
- 测试策略明确。
- 用户已确认 plan，或已有等价实施计划。
