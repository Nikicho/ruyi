---
name: ruyi-test
description: Use when a Ruyi implementation result needs frontend validation, fast-browser UI automation, manual test evidence, coverage notes, or a verification summary before explain.
---

# Ruyi Test

## 1. 适用场景

- 编码实现后需要验证。
- 需要整理某次 contract 对应的验证结果。
- 需要把自然语言 test case 转成 UI 自动化验证证据。

## 2. 硬门禁

- 项目必须已初始化。
- 必须有明确验证对象。
- 没有验证对象时，不生成验证结果。

## 3. 执行原则

- 明确验证对象是什么。
- 优先使用项目已有测试方式。
- UI 相关需求优先使用 fast-browser CLI。
- 结果收口前遵守 `references/verification-discipline.md`。
- fast-browser 使用遵守 `references/fast-browser-testing.md`。

## 4. 执行步骤

1. 检查项目是否已初始化。
2. 读取 contract、plan 和实现阶段验证点。
3. 读取 `references/verification-discipline.md` 和 `references/fast-browser-testing.md`。
4. 选择项目已有验证方式。
5. UI 相关需求优先尝试 fast-browser case/flow/site。
6. 执行验证命令、UI 自动化或手工验证步骤。
7. 按 `references/test-schema.md` 记录验证证据、失败项、风险和未覆盖项。
8. 验证失败时返回 implement、plan 或 contract。
9. 验证通过后，允许进入 `ruyi-explain`。

## 5. 产物要求

路径：

```text
.ruyi/tests/<module>/<feature>/<contract-date>.md
```

内容必须包含：

- 验证对象。
- 验证方式。
- 验证证据。
- 与验收标准对照。
- 验证结论。
- 失败、风险或未覆盖项。

## 6. 脚本调用

验证执行完成后，可以使用脚本生成正式 `test` 文件：

```bash
python <skills-dir>/ruyi-test/scripts/test_create.py --project <project> --module <module> --feature <feature> --date <YYYY-MM-DD> --title <title> --result <passed|passed-with-notes|failed> --method <method> --ui-automation <item> --evidence <evidence> --acceptance-result <result> --conclusion <conclusion>
```

脚本职责：

- 校验项目已初始化。
- 校验对应 contract 存在。
- 校验对应 plan 存在且 `status: confirmed`。
- 按固定路径写入 `.ruyi/tests/<module>/<feature>/<contract-date>.md`。
- 不覆盖已有 test。
- 记录 UI 自动化证据或无法自动化的原因。

脚本不负责选择测试策略，也不替代实际验证。

## 7. 必读参考

- `references/main-flow.md`
- `references/contract-schema.md`
- `references/plan-schema.md`
- `references/test-schema.md`
- `references/explain-schema.md`
- `references/engineering-discipline.md`
- `references/verification-discipline.md`
- `references/fast-browser-testing.md`
