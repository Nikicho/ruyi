---
name: ruyi-contract
description: Use when a frontend change needs a business contract for a new feature, bug fix, refactor, requirement adjustment, acceptance criteria, or natural-language test cases before planning.
---

# Ruyi Contract

## 1. 适用场景

- 新功能需求定义。
- 修复类需求定义。
- 重构目标定义。
- 已有 contract 的补充和修订。
- 输出自然语言测试用例。
- 判断一个 contract 是否需要进入 plan 拆分。

## 2. 硬门禁

- 项目必须已初始化。
- 没有明确需求目标时，不落盘。
- 未完成需求定义、验收标准和核心测试用例时，不进入 plan。
- 语义变化时新建日期文件；非语义修订时原地修改当前文件。

## 3. 执行原则

- 以业务定义为主。
- 不写实现细节。
- 优先简洁。
- 需求设计过程遵守 `references/contract-discipline.md`。
- 修复类需求必要时先遵守 `references/debugging-discipline.md`。
- `fix / refactor` 是 contract 的需求类型，不是独立 Ruyi skill。

## 4. 执行步骤

1. 检查项目是否已初始化。
2. 读取 `../references/contract-schema.md`。
3. 读取 `references/contract-discipline.md`。
4. 如果是修复类需求，先读取并执行 `references/debugging-discipline.md`。
5. 判断模块和功能命名，优先贴近项目现有模块目录。
6. 澄清业务目标、用户故事、验收标准、自然语言测试用例和范围边界。
7. 判断是新建日期 contract，还是修订当前 contract。
8. 用户确认后，按路径写入或更新 contract。
9. 如 contract 需要拆分或需要实施设计，引导进入 `ruyi-plan`。

## 5. 脚本调用

最小可用落盘脚本：

```powershell
python scripts/contract_create.py `
  --project <project-root> `
  --module <module-slug> `
  --feature <feature-slug> `
  --date <YYYY-MM-DD> `
  --type <new-feature|fix|refactor|change> `
  --size <tiny|standard|large> `
  --status <draft|confirmed> `
  --title <功能名称> `
  --goal <业务目标> `
  --story <用户故事> `
  --scope <范围内条目> `
  --acceptance <验收标准> `
  --test-case <自然语言测试用例>
```

脚本规则：

- 要求项目已初始化，至少存在 `.ruyirc` 和 `.ruyi/contracts/`。
- 只创建新 contract，不覆盖已有文件。
- `module / feature` 使用小写字母、数字和连字符。
- `date` 固定为 `YYYY-MM-DD`。
- `type` 只允许 `new-feature / fix / refactor / change`。
- `size` 只允许 `tiny / standard / large`；默认 `standard`。
- `fix` 不能使用 `tiny`。
- `status` 只允许 `draft / confirmed`；只有 `confirmed` contract 可进入 plan。
- `test-case` 至少 1 条，用自然语言描述用户路径、输入、预期结果或边界场景。
- 脚本只负责落盘，不负责替代需求澄清和用户确认。

## 6. 产物要求

产物路径：

```text
contracts/<module>/<feature>/<YYYY-MM-DD>.md
```

正文结构遵守 `../references/contract-schema.md`。

## 7. 必读参考

- `../references/main-flow.md`
- `../references/contract-schema.md`
- `../references/spec-schema.md`
- `../using-ruyi/references/engineering-discipline.md`
- `references/contract-discipline.md`
- `references/debugging-discipline.md`
