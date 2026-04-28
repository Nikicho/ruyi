# Explain Discipline

## 1. 目标

explain 阶段负责把一次开发结果整理成 PM 能读懂、能审批的开发简报，并包含研发管理可读的代码质量简报。

它不是代码 diff 说明，也不是技术流水账，也不替代 implement 阶段的 code review。

本纪律内化自 Superpowers 的 `verification-before-completion` 和 `finishing-a-development-branch`：

- 吸收 `verification-before-completion` 的证据要求，explain 只能基于 contract、plan、implement 自检和 test 事实。
- 吸收 `finishing-a-development-branch` 的收尾意识，交付说明必须包含风险、未覆盖项和下一步判断。
- explain 不重新执行代码 review，也不生成审批结论。

## 2. 硬门禁

- 没有 contract 或等价需求定义，不生成正式 explain。
- 没有 `test` 验证结果，不生成正式 explain。
- explain 不写审批结论。
- 不能只列改了哪些文件，必须对照验收标准说明交付结果。
- 代码质量简报必须来自 plan、implement 自检或实际代码事实。
- 代码质量简报必须写出来源，不能只给结论。
- 验证失败或未覆盖风险未说明时，不进入审批。

## 3. 最小流程

1. 读取 contract。
2. 读取 plan。
3. 读取 `test` 验证结果。
4. 读取 implement 阶段自检和代码质量结论。
5. 对照验收标准整理交付结果。
6. 写出影响范围。
7. 写出验证摘要。
8. 写出代码质量简报。
9. 写出失败、风险和未覆盖项。
10. 写出少量必要技术备注。
11. 生成 explain，等待审批。

## 4. 反模式

| 反模式 | 正确处理 |
| --- | --- |
| 把 git diff 翻译成中文 | 对照 contract 写交付结果 |
| explain 里直接写“审批通过” | 审批结论属于 approve 阶段 |
| 隐藏验证失败 | 明确失败项并返回 test 或 implement |
| 技术细节过多 | 只保留影响交付、风险、后续维护的技术备注 |
| 没有 PM 可读结论 | 用业务语言总结本次是否满足需求 |
| 虚构架构优化 | 只写实际发生且有依据的文件架构、hooks、组件或代码设计 |

## 5. 具体反模式（Anti-patterns）

### ❌ test 没写的风险，我凭经验补进 explain

**触发场景**：你发现可能存在某个风险，但 test 没有记录。

**你想做的事**：在 explain 中补充“风险提示”。

**为什么错**：explain 只能引用 test 事实或明确标注待确认，不能生成新验证结论。

**正确做法**：返回 test 补证据；若无法验证，写为“待确认风险”并说明来源。

### ❌ 我顺便给 PM 写“下次建议”

**触发场景**：交付说明写完后，你想追加改进建议。

**你想做的事**：把后续规范或架构建议写进 explain。

**为什么错**：长期规则和后续建议属于 spec-candidate，不属于审批前简报。

**正确做法**：explain 只说明本次交付、风险和验证；可复用经验进入 `ruyi-spec-evolve`。

## 6. 检查清单

生成前检查：

- 是否有对应 contract？
- 是否有 `test` 验证结果？
- 是否逐条回应验收标准？
- 是否写清交付结果？
- 是否写清代码质量简报？
- 是否写清风险和未覆盖项？
- 是否没有夹带审批结论？
