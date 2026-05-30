# Plan Schema

## 1. 对象定位

`plan` 是某个 contract 进入编码前给人确认的架构与实施边界方案，负责把需求转成可判断的技术方向、文件落点、最小接口数据判断、spec 约束、task 标题和验证策略。

`plan` 不是业务需求定义，不复述 contract；也不是详细开发步骤，详细步骤进入 implement 阶段的本地 task checkpoint。

## 2. 路径规则

路径格式：

```text
plans/<module>/<feature>/<contract-date>.md
```

其中：

- `module`：对应 contract 的业务模块。
- `feature`：对应 contract 的功能对象名。
- `contract-date`：对应 contract 文件日期。

## 3. 头部元信息

建议包含：

- 对应 Contract
- 所属模块
- 功能对象
- 日期
- 计划状态

计划状态建议使用：

- `draft`
- `confirmed`
- `blocked`

## 4. 正文结构

```md
# Plan：[功能名称]

## 方案概述
## 文件/模块架构
## 接口与数据
## Spec 约束
## Task 拆分
## 验证策略
## 修订记录
```

## 5. 规则

- plan 必须锚定一个 contract。
- plan 必须说明架构方案和关键取舍，但不写详细开发步骤。
- `## 文件/模块架构` 展示最终功能会落到哪些目录、文件、模块或组件，并标注 new / modify / reuse / unchanged / candidate。
- `## 接口与数据` 只写最少开发判断：接口是否变化、入参、出参、关键状态、异常处理。没有接口变化时写“本次不涉及接口变化。”
- `## Spec 约束` 必须列出实现前要读取的 spec，并为每个文件写一个短标签，例如“代码基线”“开发检查”“订单列表行为”“搜索组件约定”。
- `## Task 拆分` 只写实际实施步骤的标题列表，不展开目标、范围、写入边界、完成条件。
- `## 验证策略` 必须覆盖 contract 中的自然语言测试用例，并说明验证方式。
- 当 contract 存在 `## 接口范围` 且非空时，plan 必须包含 `## 接口与数据`。
- 类型 B 中途变更后，plan 必须追加 `## 修订记录`，说明哪些 task 保留、取代或新增。
- contract 不足时，返回 contract 阶段，不在 plan 中隐式补业务需求。

`## 接口与数据` 至少确认：

- 接口：新增、修改、复用或不涉及。
- 入参：本次新增或复用的关键参数。
- 出参：是否变化。
- 状态：关键前端状态或缓存变化。
- 异常：沿用现有处理还是新增处理。

## 6. 与 task 的关系

`plan` 是一次需求的人类确认层。

`task` 是 implement 阶段的本地执行层。plan 里的 `## Task 拆分` 只给出标题和顺序；进入 implement 后，agent 再按这些标题生成本地 task checkpoint，并补充详细步骤、进度和 compact 恢复点。
