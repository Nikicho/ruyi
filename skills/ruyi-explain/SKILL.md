---
name: ruyi-explain
description: Use when a completed Ruyi contract needs a PM-facing development brief, delivery explanation, verification summary, code quality brief, or implementation impact note.
---

# Ruyi Explain

## 1. 适用场景

- 开发完成后需要生成简报。
- 审批前需要说明本次交付结果。
- 需要说明文件架构、hooks 拆分、组件设计、代码设计和自检优化结论。

## 2. 硬门禁

- 项目必须已初始化。
- 没有需求定义锚点，不生成 explain。
- 没有 `test` 验证结果，不进入 explain 正式产出。
- explain 不包含审批结论正文。

## 3. 执行原则

- 面向 PM 阅读。
- 对照 contract，而不是对照代码 diff。
- 代码质量简报来自 plan、implement 自检和实际代码事实。
- 允许少量高价值技术备注。
- 不写成技术流水账。

## 4. 执行步骤

1. 检查项目是否已初始化。
2. 读取 contract。
3. 读取 plan。
4. 读取 `test` 验证结果。
5. 读取 implement 阶段自检和代码质量结论。
6. 读取 `references/explain-discipline.md`。
7. 对照验收标准整理交付结果。
8. 写出影响范围、验证摘要、代码质量简报、风险和未覆盖项。
9. 按 `../../references/explain-schema.md` 生成 explain。
10. 不写审批结论，等待 `ruyi-approve`。

## 5. 产物要求

产物路径：

```text
explain/<module>/<feature>/<contract-date>.md
```

正文结构遵守 `../../references/explain-schema.md`。

## 6. 脚本调用

确认 contract、plan 和通过的 test 都存在后，可以使用脚本生成正式 explain：

```bash
python skills/ruyi-explain/scripts/explain_create.py --project <project> --module <module> --feature <feature> --date <YYYY-MM-DD> --title <title> --completed <item> --requirement-result <item> --verification <item> --code-quality <item>
```

脚本职责：

- 校验项目已初始化。
- 校验对应 contract 存在。
- 校验对应 plan 存在。
- 校验对应 test 存在，且 `result` 为 `passed` 或 `passed-with-notes`。
- 按固定路径写入 `.ruyi/explain/<module>/<feature>/<contract-date>.md`。
- 不覆盖已有 explain。
- 固定写入 `approval: pending`。
- 写入代码质量简报。

脚本不负责从代码 diff 自动总结，不写审批结论。

审批前可使用 lint 脚本检查 explain 是否越界引用 test 中不存在的风险：

```bash
python skills/ruyi-explain/scripts/explain_lint.py --project <project> --module <module> --feature <feature> --date <YYYY-MM-DD>
```

lint 失败时，返回 `ruyi-test` 补证据，或把风险明确标记为待确认。

## 7. 必读参考

- `../../references/main-flow.md`
- `../../references/contract-schema.md`
- `../../references/plan-schema.md`
- `../../references/test-schema.md`
- `../../references/explain-schema.md`
- `references/explain-discipline.md`
