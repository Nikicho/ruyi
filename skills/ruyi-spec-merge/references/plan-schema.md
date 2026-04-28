# Plan Schema

## 1. 对象定位

`plan` 是某个 contract 进入编码前的实施方案，负责把业务需求、自然语言测试用例和项目规范转成可执行开发路径。

`plan` 不是业务需求定义，也不是最终验证结果。

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

## 实施目标
## 输入依据
## 测试策略
## Task 拆分
## 实施顺序
## 写入范围
## 依赖与风险
## 完成条件
```

## 5. 规则

- plan 必须锚定一个 contract。
- plan 必须覆盖 contract 中的自然语言测试用例，并说明验证方式。
- plan 可以拆分多个 task，但不能改写 contract 的业务范围。
- plan 中每个 task 条目必须说明目标、范围、写入边界和完成条件。
- plan 必须说明主要写入范围，尤其是并行开发或多 task 场景。
- contract 不足时，返回 contract 阶段，不在 plan 中隐式补业务需求。

## 6. 与 task 的关系

`plan` 是一次需求的整体实施方案。

`task` 是 plan 下的具体执行单元。一个 plan 可以对应一个或多个 task。
