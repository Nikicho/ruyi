# Test Schema

## 1. 对象定位

`test` 是某次 contract 对应的最小验证账本，记录验收项、证据、结论，以及必要的失败或风险信息。

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

## 验收与证据

- 验收：...
- 验证方式：...
- UI 自动化：... # 仅 UI 场景需要
- 证据：...

## 结论

...

## 失败项 # 仅 failed 时出现
## 风险与未覆盖项 # 仅 failed / passed-with-notes 时出现
```

## 5. 规则

- test 必须锚定一个 contract。
- test 应优先引用 plan 中定义的测试策略。
- test 必须覆盖 contract 的验收标准，未覆盖项必须明确写出。
- 命令验证、浏览器验证、人工检查都可以作为验证方式，但必须记录具体证据。
- UI 相关需求应优先尝试 fast-browser CLI；无法自动化时必须说明原因。
- 默认只使用 `验收与证据` 和 `结论` 两节，不为了结构完整生成空章节。
- `failed` 必须包含失败项。
- `failed` 或 `passed-with-notes` 必须包含风险或未覆盖项。
- 验证失败时，不能进入正式 explain。
- 类型 B 中途变更不新建日期 test；在原 test 文件追加 `## 修订验证`，记录新增或重跑的验证项。
- 类型 C 语义变化必须新建日期 test，因为旧验证不再代表新业务定义。

## 6. 修订验证

类型 B 中途变更后，在原 test 文件末尾追加：

```md
## 修订验证

### <YYYY-MM-DD> 修订验证

- 变更来源：contract `## 修订记录` 第 N 条
- 重跑项：...
- 新增项：...
- 结论：passed / passed-with-notes / failed
```

## 7. 与本地 checkpoint 的关系

`tests/` 保存主流程正式验证结果。`.ruyi/tasks/` 只保存本地执行恢复进度，不能作为 `explain` 的正式门禁依据，也不能替代 test 证据。
