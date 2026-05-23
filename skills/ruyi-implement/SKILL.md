---
name: ruyi-implement
description: Routed by using-ruyi. Use only after using-ruyi has determined the next stage is implementation. Handles frontend coding from a confirmed plan, lightweight maintenance mode for no-behavior-change code optimization or micro-refactoring, task execution, code self-review, project spec constraints, and implementation quality checks.
---

# Ruyi Implement

## 1. 适用场景

- 已有明确 plan，需要进入编码实现。
- 预计跨轮次或跨多个文件组实现时，需要使用本地 task checkpoint 恢复执行进度。
- 需要完成代码自检、代码质量检视和优化收口。
- `using-ruyi` 已确认进入轻量维护模式，需要处理不改变业务行为的代码优化或代码微重构。

## 2. 硬门禁

- 项目必须已初始化。
- 正式需求实现必须存在 contract 和 plan。
- 轻量维护模式不要求 contract / plan / task，但必须由 `using-ruyi` 明确路由进入。
- 轻量维护模式必须确认不改变业务行为。
- 不在缺少 plan 或等价实施计划时进入正式需求实现。
- 不生成 explain，不执行审批。

## 3. 执行原则

- 先读取 project spec 与可用 team spec。
- 以 contract 为需求边界，以 plan 为实施边界。
- 轻量维护模式以维护目标和写入边界为实施边界，以现有 spec 为约束来源。
- `tiny` contract 可以跳过 plan/checkpoint，但如果实际改动超过 3 个文件、新增 hook/组件或出现业务规则变化，必须升级为 `standard` 并返回 `ruyi-plan`。
- 非 tiny 实现仅在多 task 或预计跨轮次/文件组工作时，于首次修改源码前按需创建 `.ruyi/tasks/` checkpoint；它是本地恢复状态，不提交 git，也不作为 formal test 门禁。
- 轻量维护模式如果发现用户可感知行为、业务规则、接口语义、状态语义、权限、路由或验收标准变化，必须停止并返回 `ruyi-contract`。
- 实现阶段遵守 `references/implementation-discipline.md`。
- 代码自检和 review 反馈处理遵守 `references/code-review-discipline.md`。
- 遇到修复类问题时读取 `references/debugging-discipline.md`。
- 不把编码阶段的临时判断直接写成项目规范。

## 4. 执行步骤

1. 检查项目是否已初始化。
2. 读取 contract 和 plan。
3. 读取 project spec 和可用 team spec。
4. 读取 `references/implementation-discipline.md` 和 `references/code-review-discipline.md`。
5. 判断本次实现是否需要本地 checkpoint；需要时在首次修改源码前创建，并在完成文件组、运行验证或准备结束回复前更新。
6. 实现 plan 范围内的最小必要改动。
7. 运行局部验证。
8. 完成代码自检、review 反馈处理和必要优化。
9. 不声明完成，交给 `ruyi-test` 收口。

轻量维护模式：

1. 检查项目是否已初始化。
2. 明确维护目标、写入边界和不改变业务行为的判断。
3. 读取相关 project spec 和可用 team spec。
4. 读取 `references/implementation-discipline.md` 和 `references/code-review-discipline.md`。
5. 在写入边界内完成最小代码优化或代码微重构。
6. 运行可行的局部验证。
7. 完成代码自检和 review 反馈处理。
8. 输出代码变更摘要、验证结果，以及是否发现可沉淀规范。

## 5. 产物要求

- 代码变更。
- 必要时生成并持续更新的本地 task checkpoint。
- 代码自检和代码质量结论。
- 可进入测试验证阶段的实现结果。
- 轻量维护模式不生成 checkpoint；输出维护目标、写入边界、验证结果和可沉淀规范判断。
- 团队需要复用的代码质量、自检与风险结论必须进入正式 `test` 或 `explain`，不得只留在本地 checkpoint。

## 6. 脚本调用

task 是 plan 下的本地执行恢复点。只有预计跨轮次或多个文件组的工作才按需创建：

```bash
python <skills-dir>/ruyi-implement/scripts/task_create.py --project <project> --module <module> --feature <feature> --date <YYYY-MM-DD> --title <title> --goal <goal> --scope <item> --write-scope <item> --step <item> --completion <item>
```

脚本职责：

- 校验项目已初始化。
- 校验对应 contract 存在。
- 校验对应 plan 存在且 `status: confirmed`。
- 懒创建 `.ruyi/tasks/` 并按 `task-01.md`、`task-02.md` 递增创建 checkpoint。
- 状态仅允许 `pending / in-progress / done`。
- 不生成业务代码。
- 不修改 contract、plan、test、explain 或 spec。
- 不重建 `.ruyi/INDEX.md`。

执行期间更新当前 checkpoint：

```bash
python <skills-dir>/ruyi-implement/scripts/task_checkpoint.py --project <project> --task <task-path> --status in-progress --next-step <next-step>
```

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
