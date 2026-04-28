# Test Schema

## 1. 对象定位

`test` 是某次 contract 对应的验证结果，记录验证对象、验证方式、证据、结论、风险和未覆盖项。

它不是自动化测试脚本本身，也不是开发流水账。

## 2. 路径规则

路径格式：

```text
tests/<module>/<feature>/<contract-date>.md
```

其中：

- `module`：对应 contract 的业务模块。
- `feature`：对应 contract 的功能对象名。
- `contract-date`：对应 contract 文件日期。

## 3. 头部元信息

建议包含：

- 对应 Contract
- 所属模块
- 功能对象
- 日期
- 验证结论

验证结论建议使用：

- `passed`
- `passed-with-notes`
- `failed`

## 4. 正文结构

```md
# Test：[功能名称]

## 验证对象
## 验证方式
## UI 自动化验证
## 验证证据
## 与验收标准对照
## 失败项
## 风险与未覆盖项
## 结论
```

## 5. 规则

- test 必须锚定一个 contract。
- test 应优先引用 plan 中定义的测试策略。
- test 必须覆盖 contract 的验收标准，未覆盖项必须明确写出。
- 命令验证、浏览器验证、人工检查都可以作为验证方式，但必须记录具体证据。
- UI 相关需求应优先尝试 fast-browser CLI；无法自动化时必须说明原因。
- `failed` 必须包含失败项。
- `failed` 或 `passed-with-notes` 必须包含风险或未覆盖项。
- 验证失败时，不能进入正式 explain。

## 6. 与 workspace 的关系

`tests/` 保存主流程正式验证结果。

`.ruyi/workspace/` 只保存临时分析、草稿和过程材料，不能作为 `explain` 的正式门禁依据。
