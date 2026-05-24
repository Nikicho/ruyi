---
name: ruyi-contract
description: Routed by using-ruyi. Use only after using-ruyi has determined the next stage is contract definition or contract amendment. Handles new feature, bug fix, refactor, requirement adjustment, acceptance criteria, API scope, and required natural-language test cases.
---

# Ruyi Contract

## 1. 适用场景

- 新功能需求定义。
- 修复类需求定义。
- 重构目标定义。
- 已有 contract 的补充和修订。
- 输出自然语言测试用例（contract 阶段必产出物，与验收标准并列权重）。
- 判断一个 contract 是否需要进入 plan 拆分。

## 2. 硬门禁

- 项目必须已初始化。
- 没有明确需求目标时，不落盘。
- contract 落盘必须至少包含一条自然语言测试用例（draft 允许占位骨架）。
- 没有完整自然语言测试用例时，contract 不能标 `confirmed`。
- 没有验收标准或测试用例时，`confirmed` contract 不进入 plan。
- 语义变化时新建日期文件；非语义修订时原地修改当前文件。

## 3. 执行原则

- 以业务定义为主。
- 不写实现细节。
- 优先简洁。
- 需求设计过程遵守 `references/contract-discipline.md`。
- 修复类需求必要时先遵守 `references/debugging-discipline.md`。
- `fix / refactor` 是 contract 的需求类型，不是独立 Ruyi skill。
- 需要读取项目规范时，先读 `.ruyi/spec/INDEX.md`，再按索引读取相关 spec；baseline contract 只作为当前业务事实背景，不替代本次变更 contract。

## 4. 执行步骤

1. 检查项目是否已初始化。
2. 读取 `references/contract-schema.md`。
3. 读取 `references/contract-discipline.md`。
4. 读取 `.ruyi/spec/INDEX.md`，并按索引读取本次相关 spec 或 baseline contract。
5. 如果是修复类需求，先读取并执行 `references/debugging-discipline.md`。
6. 判断模块和功能命名，优先贴近项目现有模块目录。
7. 澄清业务目标、用户故事、范围边界、验收标准。
8. 判断本次是否涉及接口；涉及时收集 `## 接口范围` 信息，只记录接口路径、方法、类型、来源和必要临时定义，不抄完整 API 文档。
9. 基于验收标准 brainstorm 自然语言测试用例。每条测试用例必须：
   - 能映射回至少一条验收标准。
   - 描述具体场景，不是抽象规则。
   - 覆盖正常路径、边界、异常三类；tiny 可按实际简化但不能为空。
   一次只问一个测试场景缺口，不一次性猜完。
10. 判断是新建日期 contract，还是修订当前 contract。
11. 用户确认后，按路径写入或更新 contract。
12. 如 contract 需要拆分或需要实施设计，引导进入 `ruyi-plan`。

## 5. 修订模式

进入修订模式前，必须由 `using-ruyi` 完成 A/B/C/D 分类并获得用户确认。

1. 读取目标 contract：`.ruyi/contracts/<module>/<feature>/<最新日期>.md`。
2. 按确认分类执行：
   - 类型 A：原地修订相关字段，追加 `## 修订记录`。
   - 类型 B：原地修订相关字段，追加 `## 修订记录`，然后提示进入 `ruyi-plan` 重评模式。
   - 类型 C：新建日期 contract，旧 contract frontmatter 加 `superseded_by`。
   - 类型 D：重开同一 contract，写入 `status: reopened` 和 `## 返工记录`；按返回阶段重置当前 plan/test 状态，不新建 contract。
3. 未确认分类时，不允许落盘修订。
4. 修订后必须刷新或提示刷新 `.ruyi/INDEX.md`。

## 6. 脚本调用

最小可用落盘脚本：

```powershell
python scripts/contract_create.py `
  --project <project-root> `
  --module <module-slug> `
  --feature <feature-slug> `
  --date <YYYY-MM-DD> `
  --type <new-feature|fix|refactor|change> `
  --size <tiny|standard|large> `
  --status <draft|confirmed|reopened> `
  --title <功能名称> `
  --goal <业务目标> `
  --story <用户故事> `
  --scope <范围内条目> `
  --acceptance <验收标准> `
  --test-case <自然语言测试用例> `
  --api-scope <接口范围条目>
```

脚本规则：

- 要求项目已初始化，至少存在 `.ruyirc` 和 `.ruyi/contracts/`。
- 默认只创建新 contract；类型 D 被重开后，允许在同路径更新当前有效内容并保留返工记录。
- `module / feature` 使用小写字母、数字和连字符。
- `date` 固定为 `YYYY-MM-DD`。
- `type` 只允许 `new-feature / fix / refactor / change`。
- `size` 只允许 `tiny / standard / large`；默认 `standard`。
- `fix` 不能使用 `tiny`。
- `status` 只允许 `draft / confirmed / reopened`；只有 `confirmed` contract 可进入 plan。
- `test-case` 至少 1 条，用自然语言描述用户路径、输入、预期结果或边界场景。
- `confirmed` 且 `size` 为 `standard / large` 时，至少 3 条测试用例，覆盖正常、边界、异常。
- `api-scope` 只列本次涉及接口；完整 API 文档应引用后端权威源，不写入 contract。
- 脚本只负责落盘，不负责替代需求澄清和用户确认。

类型 D 的重开动作使用：

```powershell
python scripts/reopen_delivery.py --project <project-root> --module <module-slug> --feature <feature-slug> --date <YYYY-MM-DD> --reason <返工原因> --return-stage <contract|plan|implement|test>
```

该动作只更新原交付文件的当前状态并记录返工原因，不写 `derived_from`。

## 7. 产物要求

产物路径：

```text
contracts/<module>/<feature>/<YYYY-MM-DD>.md
```

正文结构遵守 `references/contract-schema.md`。

## 8. 必读参考

- `references/main-flow.md`
- `references/contract-schema.md`
- `references/spec-schema.md`
- `references/engineering-discipline.md`
- `references/contract-discipline.md`
- `references/debugging-discipline.md`
