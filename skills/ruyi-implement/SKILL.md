---
name: ruyi-implement
description: Use when an approved Ruyi plan should be implemented in frontend code, with task execution, code self-review, and project spec constraints.
---

# Ruyi Implement

## 1. 适用场景

- 已有明确 plan，需要进入编码实现。
- 需要执行 plan 中的 task。
- 需要完成代码自检、代码质量检视和优化收口。

## 2. 硬门禁

- 项目必须已初始化。
- 必须存在 contract 和 plan。
- 不在缺少 plan 或等价实施计划时进入正式实现。
- 不生成 explain，不执行审批。

## 3. 执行原则

- 先读取 project spec 与可用 team spec。
- 以 contract 为需求边界，以 plan 为实施边界。
- `tiny` contract 可以跳过 plan/task，但如果实际改动超过 3 个文件、新增 hook/组件或出现业务规则变化，必须升级为 `standard` 并返回 `ruyi-plan`。
- 实现阶段遵守 `references/implementation-discipline.md`。
- 代码自检和 review 反馈处理遵守 `references/code-review-discipline.md`。
- 遇到修复类问题时读取 `references/debugging-discipline.md`。
- 不把编码阶段的临时判断直接写成项目规范。

## 4. 执行步骤

1. 检查项目是否已初始化。
2. 读取 contract 和 plan。
3. 读取 project spec 和可用 team spec。
4. 读取 `references/implementation-discipline.md` 和 `references/code-review-discipline.md`。
5. 按 plan 执行 task。
6. 实现 plan 范围内的最小必要改动。
7. 运行局部验证。
8. 完成代码自检、review 反馈处理和必要优化。
9. 不声明完成，交给 `ruyi-test` 收口。

## 5. 产物要求

- 代码变更。
- task 执行结果。
- 代码自检和代码质量结论。
- 可进入测试验证阶段的实现结果。

## 6. 脚本调用

task 是 plan 下的执行单元。当前 task 创建脚本保留在 `ruyi-implement` 下，用于进入实现阶段前后创建执行单元：

```bash
python <skills-dir>/ruyi-implement/scripts/task_create.py --project <project> --module <module> --feature <feature> --date <YYYY-MM-DD> --title <title> --goal <goal> --scope <item> --write-scope <item> --step <item> --completion <item>
```

脚本职责：

- 校验项目已初始化。
- 校验对应 contract 存在。
- 校验对应 plan 存在且 `status: confirmed`。
- 按 `task-01.md`、`task-02.md` 递增创建 task。
- 不生成业务代码。
- 不修改 contract、plan、test、explain 或 spec。

## 7. 必读参考

- `references/main-flow.md`
- `references/spec-schema.md`
- `references/contract-schema.md`
- `references/plan-schema.md`
- `references/task-schema.md`
- `references/engineering-discipline.md`
- `references/implementation-discipline.md`
- `references/code-review-discipline.md`
- `references/debugging-discipline.md`
