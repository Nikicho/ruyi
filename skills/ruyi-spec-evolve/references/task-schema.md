# Task Schema

## 1. 对象定位

`task` 是围绕某个具体 plan 的本地执行 checkpoint，不是需求定义，也不是团队交付凭证。

一个 plan 预计跨轮次或多个文件组执行时，可以按需创建多个 task；短实现无需创建。

## 2. 路径规则

路径格式：

```text
tasks/<module>/<feature>/<contract-date>/task-01.md
```

任务文件按 `task-01.md`、`task-02.md` 递增；`.ruyi/tasks/` 默认 gitignored，且不进入 `.ruyi/INDEX.md`。

## 3. 头部元信息

建议包含：

- 状态
- 对应 Contract
- 对应 Plan

任务状态建议使用：

- `pending`
- `in-progress`
- `done`

plan 变化导致 checkpoint 不再有效时，删除旧本地 task 并按当前 plan 重建，不保留历史状态。

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
## 当前进度
## 本地自检记录
```

## 5. 硬门禁

- task 必须对应某个已确认 plan 和 contract 日期版本。
- task 不定义需求，只定义执行。
- task 不提交 git，不作为进入 test 或 explain 的门禁。
- 团队可复用的自检、质量与风险结论必须写入正式 test 或 explain，不能只留在 task。
