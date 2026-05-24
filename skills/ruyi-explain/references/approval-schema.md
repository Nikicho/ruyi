# Approval Schema

## 1. 定位

`approval` 是 PM 对某次 test 验证结果和交付可接受性的审批结论。

schema v3 不新增独立审批目录，审批结论直接写回对应 test：

- 更新 test 头部元信息中的 `approval`。
- 必要时写入 `return_stage`。
- 在 test 正文末尾追加或替换 `## 审批结论`。

## 2. Frontmatter

```yaml
approval: pending | approved | changes-requested
return_stage: contract | plan | implement | test
```

- `pending`：由 `ruyi-test` 创建，等待审批。
- `approved`：接受交付，可进入知识沉淀判断。
- `changes-requested`：需要修改，必须带 `return_stage`。

## 3. 审批章节

审批后在 test 末尾追加：

```md
## 审批结论

- 审批状态：approved | changes-requested
- 审批说明：...
- 返回阶段：无需返回。 | contract | plan | implement | test
```

## 4. 门禁

- 没有 test，不允许审批。
- test 必须锚定 contract 和 plan；tiny 可按当前流程约定省略 plan。
- test 的 `result` 必须是 `passed` 或 `passed-with-notes`。
- 只有 `approval: pending` 的 test 可以被审批。
- `changes-requested` 必须明确返回阶段。
