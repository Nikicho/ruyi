# Test Schema

## 1. 定位

`tests/` 保存主流程正式验证结果、验收证据和审批状态。它是团队共享交付资产，应提交 git。

`.ruyi/tasks/` 只保存本地执行恢复进度，不能作为正式验证证据，也不能替代 test。

## 2. 路径

```text
.ruyi/tests/<module>/<feature>/<contract-date>.md
```

## 3. Frontmatter

```yaml
contract: .ruyi/contracts/<module>/<feature>/<date>.md
plan: .ruyi/plans/<module>/<feature>/<date>.md
module: <module>
feature: <feature>
date: <YYYY-MM-DD>
result: passed | passed-with-notes | failed | pending
approval: pending | approved | changes-requested
return_stage: contract | plan | implement | test
```

- `approval` 由 `ruyi-test` 初始化为 `pending`，由 `ruyi-approve` 更新。
- `return_stage` 只在 `changes-requested` 时出现。

## 4. 正文结构

```md
# Test：[功能名称]

## 验收与证据

## 结论
```

仅当影响判断时追加：

```md
## 失败项

## 风险与未覆盖项

## 审批结论
```

## 5. 规则

- 验证失败时，不能进入审批。
- `failed` 必须写失败项。
- `failed` 或 `passed-with-notes` 必须写风险或未覆盖项。
- UI 相关需求应优先使用 fast-browser 或项目已有 UI 自动化；无法自动化时必须说明原因。
- test 不记录长篇执行过程，只记录足够复核的验收、证据和结论。
