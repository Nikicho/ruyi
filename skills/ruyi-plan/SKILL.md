---
name: ruyi-plan
description: Use when a confirmed Ruyi contract needs implementation planning, test strategy mapping, task breakdown, execution order, or write-scope boundaries before coding.
---

# Ruyi Plan

## 1. 适用场景

- 已有明确 contract，需要进入编码前计划。
- 需要把自然语言测试用例转成验证策略。
- 需要把一次 contract 拆成一个或多个 task。
- 需要判断实施顺序、依赖关系和写入范围。

## 2. 硬门禁

- 项目必须已初始化。
- 必须存在 contract 或等价需求定义。
- contract 缺少核心验收标准或自然语言测试用例时，返回 `ruyi-contract`。
- 没有 plan 或等价实施计划时，不进入正式 `ruyi-implement`。

## 3. 执行原则

- plan 只做实施设计，不写业务需求。
- plan 必须覆盖 contract 中的测试用例。
- plan 必须说明 task 拆分、实施顺序、写入范围和完成条件。
- 发现需求边界不清时返回 `ruyi-contract`，不在 plan 里隐式扩展需求。
- 并行开发只在 task 边界清楚时建议，不强制使用多 agent。

## 4. 执行步骤

1. 检查项目是否已初始化。
2. 读取 contract。
3. 读取 project spec 和可用 team spec。
4. 读取 `references/plan-schema.md`。
5. 读取 `references/planning-discipline.md`。
6. 将自然语言测试用例映射为验证策略。
7. 拆分 task，并明确每个 task 的写入范围和完成条件。
8. 明确实施顺序、依赖和风险。
9. 用户确认后，写入 plan，并按需生成 task。

## 5. 产物要求

产物路径：

```text
.ruyi/plans/<module>/<feature>/<contract-date>.md
```

正文结构遵守 `references/plan-schema.md`。

## 6. 脚本调用

确认 contract 已经 `confirmed` 后，可以使用脚本生成正式 plan：

```bash
python <skills-dir>/ruyi-plan/scripts/plan_create.py --project <project> --module <module> --feature <feature> --date <YYYY-MM-DD> --title <title> --status <draft|confirmed|blocked> --goal <goal> --input <item> --test-strategy <item> --task <item> --sequence <item> --write-scope <item> --completion <item>
```

可选参数：

- `--risk <item>`

脚本职责：

- 校验项目已初始化。
- 校验对应 contract 存在且 `status: confirmed`。
- 写入 `.ruyi/plans/<module>/<feature>/<contract-date>.md`。
- 不覆盖已有 plan。
- 不生成 task。
- 不修改 contract、test、explain 或 spec。

脚本只负责落盘，不替代 agent 的实施设计判断。

## 7. 必读参考

- `references/main-flow.md`
- `references/contract-schema.md`
- `references/plan-schema.md`
- `references/task-schema.md`
- `references/spec-schema.md`
- `references/engineering-discipline.md`
- `references/planning-discipline.md`
