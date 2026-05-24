# Task Schema

## 1. 定位

`.ruyi/tasks/` 是本地执行恢复点，只服务于跨轮次或多文件组实现，不提交 git，不进入团队 INDEX。

## 2. 规则

- task 只在预计跨轮次或多个文件组时按需创建。
- task 状态只允许 `pending / in-progress / done`。
- task 不作为进入 test 或 approve 的正式门禁。
- 团队可复用的自检、质量与风险结论必须进入正式 test、spec candidate 或 spec，不能只留在 task。

## 3. 路径

```text
.ruyi/tasks/<module>/<feature>/<contract-date>/task-01.md
```

## 4. Git

`.ruyi/tasks/**` 必须被 `.gitignore` 忽略。
