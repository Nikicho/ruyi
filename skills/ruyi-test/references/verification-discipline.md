# Verification Discipline

## 1. 目标

test 阶段负责把本次 contract 的验收结果、证据和结论收口到正式 test 文件。

## 2. 硬门禁

- 没有 contract，不进入正式验证。
- standard / large 没有 confirmed plan，不进入正式验证。
- 没有实际证据，不写 passed。
- 验证失败时，不进入 approve。
- 风险和未覆盖项必须写入 test，不能只写在最终回复里。

## 3. 最小流程

1. 读取 contract 和 plan。
2. 读取 `.ruyi/spec/INDEX.md` 和相关测试规范。
3. 选择项目已有验证方式。
4. UI 相关需求优先使用 fast-browser 或项目已有 UI 自动化。
5. 执行验证。
6. 记录验收、证据和结论。
7. `failed` 或 `passed-with-notes` 时记录失败项、风险或未覆盖项。
8. 通过后才允许进入 approve。

## 4. 反模式

| 反模式 | 正确处理 |
| --- | --- |
| 测试失败但继续审批 | 返回 implement 或 test 修复问题 |
| 没有证据就写 passed | 先补验证证据 |
| UI 需求不说明为什么没自动化 | 写明无法自动化原因或执行 fast-browser |
| 风险只写在回复里 | 写入 test 的风险或未覆盖项 |

## 5. 检查清单

- 是否覆盖 contract 的自然语言测试用例？
- 是否有可复核证据？
- 是否记录了 UI 自动化或无法自动化原因？
- 是否能支撑进入 approve？
