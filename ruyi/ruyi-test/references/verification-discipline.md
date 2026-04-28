# Verification Discipline

## 1. 目标

验证阶段负责证明本次实现满足 contract 和 plan 中的测试策略，并清楚暴露未覆盖、失败和风险。

本纪律内化自 Superpowers 的 `verification-before-completion`、`systematic-debugging` 和 `test-driven-development`：

- 吸收 `verification-before-completion` 的证据要求：完成声明必须有证据，不能用主观判断代替验证。
- 吸收 `systematic-debugging` 的失败处理纪律：验证失败时记录现象、证据和诊断方向，不猜根因、不粉饰结果。
- 吸收 `test-driven-development` 的验收对齐纪律：test 阶段必须回到 contract 的自然语言测试用例和 plan 的验证策略逐条收口。

## 2. 硬门禁

- 没有明确验证对象，不生成验证结论。
- 没有执行验证命令、手工步骤或观察证据，不声明通过。
- 验证失败时，不进入 explain 正式产出。
- 未覆盖项必须显式写出，不能用“应该没问题”掩盖。
- `failed` 必须写出失败项；`failed` 或 `passed-with-notes` 必须写出风险或未覆盖项。
- 只要修改了代码，就必须说明验证范围。
- UI 相关需求必须优先尝试 fast-browser，无法自动化时必须说明原因。
- 如果项目没有可用测试命令，也要说明人工验证路径或当前无法验证的原因。

## 3. 最小流程

1. 读取 contract 和验收标准。
2. 读取 plan 中的测试策略。
3. 读取实现阶段给出的验证点。
4. 选择项目已有验证方式。
5. UI 相关路径优先尝试 fast-browser。
6. 执行验证。
7. 记录命令、步骤、UI 自动化或观察证据。
8. 对照验收标准给出结论。
9. 写出失败、风险和未覆盖项。
10. 通过后才允许进入 explain。

## 4. 可接受证据

可接受证据包括：

- 测试命令及结果
- 构建命令及结果
- lint/typecheck 命令及结果
- 页面操作步骤及观察结果
- fast-browser case/flow/site 执行结果
- fast-browser 失败诊断证据
- 接口请求和响应结果
- 错误复现前后对比

不可接受证据包括：

- “代码看起来没问题”
- “我已经检查过”
- “理论上可行”
- “没有报错所以通过”

## 5. 反模式

| 反模式 | 正确处理 |
| --- | --- |
| 测试失败但继续写 explain | 返回 implement 或 test 修复问题 |
| 没跑命令却说验证通过 | 执行验证或声明未验证 |
| 只验证 happy path | 写出未覆盖风险 |
| 验证对象和 contract 无关 | 重新按验收标准设计验证 |
| 用一次截图代替所有验证 | 说明截图覆盖的范围和未覆盖项 |
| UI 需求只手工点一下 | 优先尝试 fast-browser，无法自动化时写明原因 |

## 6. 具体反模式（Anti-patterns）

### ❌ 构建成功但有 deprecation warning，我直接标 passed

**触发场景**：命令退出成功，但输出包含 warning 或兼容性提示。

**你想做的事**：只记录“构建通过”。

**为什么错**：warning 可能是后续风险，不能从证据里消失。

**正确做法**：根据影响标记 `passed` 或 `passed-with-notes`，并把 warning 写入风险或未覆盖项。

### ❌ UI 自动化失败一次，刷新好了，我标 passed

**触发场景**：UI 验证第一次失败，重试后通过。

**你想做的事**：只记录最终通过。

**为什么错**：flaky 是测试风险，不是成功路径。

**正确做法**：记录失败现象、重试结果和可能风险；必要时标 `passed-with-notes`。

## 7. 检查清单

收口前检查：

- 验证对象是否明确？
- 验证方式是否说明？
- 是否有命令、步骤或观察证据？
- UI 相关需求是否尝试 fast-browser？
- 是否逐条对应 contract 验收标准？
- 是否写出失败项？
- 是否写出风险和未覆盖项？
- 是否能支撑进入 explain？

任何一项缺失，都不要声明完成。
