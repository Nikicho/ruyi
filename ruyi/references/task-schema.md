# Task Schema

## 1. 对象定位

`task` 是围绕某个具体 plan 的执行单元，不是需求定义。

一个 plan 可以拆成多个 task。

## 2. 路径规则

路径格式：

```text
tasks/<module>/<feature>/<contract-date>/task-01.md
```

任务文件按 `task-01.md`、`task-02.md` 递增。

## 3. 头部元信息

建议包含：

- 状态
- 对应 Contract
- 对应 Plan

## 4. 正文结构

```md
# Task：[任务名称]

## 目标
## 范围
## 写入边界
## 前置条件
## 执行步骤
## 风险与关注点
## 完成标准
## 自检与 Review 结论
```

## 5. 硬门禁

- task 必须对应某个具体 plan 和 contract 日期版本。
- task 不定义需求，只定义执行。
- `done` 状态 task 必须包含自检与 review 结论，供 explain 的代码质量简报引用。
- task 不能整体升级为 `spec`，只能作为提炼来源。
