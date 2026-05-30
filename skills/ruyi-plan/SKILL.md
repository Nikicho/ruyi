---
name: ruyi-plan
description: Routed by using-ruyi. Use only after using-ruyi has determined the next stage is implementation planning or plan re-evaluation. Handles architecture direction, file/module structure, minimal interface and data decisions, spec constraints, task title breakdown, and validation strategy before coding.
---

# Ruyi Plan

## 1. 适用场景

- 已有明确 contract，需要进入编码前计划。
- 需要确认架构方向、文件/模块落点、接口与数据判断、spec 约束和验证策略。
- 需要把一次 contract 拆成一个或多个实际实施步骤标题。
- 需要为 implement 阶段生成本地 task checkpoint 提供标题和顺序。
- 中途变更类型 B 后，需要重评 plan 和 task。

## 2. 硬门禁

- 项目必须已初始化。
- 必须存在 contract 或等价需求定义。
- contract 缺少核心验收标准或自然语言测试用例时，返回 `ruyi-contract`。
- 没有 plan 或等价实施计划时，不进入正式 `ruyi-implement`。

## 3. 执行原则

- plan 只做实施设计，不写业务需求。
- plan 必须覆盖 contract 中的测试用例。
- plan 是人类确认层，聚焦方案、文件架构、接口与数据、spec 约束、task 标题和验证策略。
- plan 不写详细开发步骤；详细步骤、完成条件和进度由 implement 阶段本地 task 维护。
- `## Task 拆分` 只写实际实施步骤标题，不能写成抽象分层，也不能展开细节。
- 发现需求边界不清时返回 `ruyi-contract`，不在 plan 里隐式扩展需求。
- 读取项目规范时，先读 `.ruyi/spec/INDEX.md`，再按索引读取相关 spec。
- 并行开发只在 task 边界清楚时建议，不强制使用多 agent。

## 4. 执行步骤

1. 检查项目是否已初始化。
2. 读取 contract。
3. 读取 `.ruyi/spec/INDEX.md`，并按索引读取相关 project spec 和可用 team spec。
4. 读取 `references/plan-schema.md`。
5. 读取 `references/planning-discipline.md`。
6. 形成 `## 方案概述`：实现方向和关键取舍。
7. 形成 `## 文件/模块架构`：最终文件落点，标注 new / modify / reuse / unchanged / candidate。
8. 形成 `## 接口与数据`：接口、入参、出参、状态、异常的最小判断；不涉及接口时明确写不涉及。
9. 形成 `## Spec 约束`：必须读取的 spec 文件和短标签。
10. 形成 `## Task 拆分`：实际实施步骤标题列表，不写详细步骤。
11. 将自然语言测试用例映射为 `## 验证策略`。
12. 用户确认后，写入 plan；进入实现后由 implement 按 task 标题生成本地 task checkpoint。

## 5. 重评模式

类型 B 中途变更后进入重评模式：

1. 读取最新 contract 的 `## 修订记录`。
2. 评估当前 plan 的方案、文件架构、接口与数据、spec 约束、task 标题和验证策略是否仍有效。
3. 如果已有本地 task checkpoint 与重评后的 plan 不一致，删除旧 checkpoint，进入实现阶段时按当前 plan 重建。
4. plan 文件追加 `## 修订记录`，引用 contract 修订条目。
5. 不允许只追加 task 标题而不评估已有 plan 的影响。

## 6. 产物要求

产物路径：

```text
.ruyi/plans/<module>/<feature>/<contract-date>.md
```

正文结构遵守 `references/plan-schema.md`。

## 7. 脚本调用

确认 contract 已经 `confirmed` 后，可以使用脚本生成正式 plan：

```bash
python <skills-dir>/ruyi-plan/scripts/plan_create.py --project <project> --module <module> --feature <feature> --date <YYYY-MM-DD> --title <title> --status <draft|confirmed|blocked> --solution <text> --architecture <item> --data-interface <item> --spec <path：标签> --task <title> --test-strategy <item>
```

可选参数：

- `--unresolved <item>`：仅存在阻塞或待确认项时使用。
- `--data-interface <item>`：当 contract 存在 `## 接口范围` 时必填；无接口变化时可写“本次不涉及接口变化。”

脚本职责：

- 校验项目已初始化。
- 校验对应 contract 存在且 `status: confirmed`。
- 写入 `.ruyi/plans/<module>/<feature>/<contract-date>.md`。
- 不覆盖已有 plan。
- 不生成 task；task 详细内容由 implement 阶段本地 checkpoint 生成。
- 不修改 contract、test 或 spec。

脚本只负责落盘，不替代 agent 的实施设计判断。

## 8. 必读参考

- `references/main-flow.md`
- `references/contract-schema.md`
- `references/plan-schema.md`
- `references/task-schema.md`
- `references/spec-schema.md`
- `references/engineering-discipline.md`
- `references/planning-discipline.md`
