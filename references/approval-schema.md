# Approval Schema

## 1. 对象定位

`approval` 是 PM 对某次 explain 的审批结论。

首版不新增独立目录，审批结论直接写回对应 explain：

- 更新 explain 头部元信息中的 `approval`。
- 非 `approved` 状态同步写入 `return_stage`，便于主流程识别退回阶段。
- 在 explain 正文末尾追加 `## 审批结论`。

## 2. 状态枚举

允许的审批状态：

- `pending`：待审批，只能由 explain 生成阶段写入。
- `approved`：接受交付，可进入知识沉淀判断。
- `changes-requested`：需要修改，必须返回 contract、plan、implement 或 test。
- `conditionally-approved`：有条件接受，必须写明条件、后续动作和返回阶段。
- `rejected`：拒绝交付，必须写明原因和返回阶段。

## 3. 正文结构

审批后在 explain 末尾追加：

```md
## 审批结论

- 审批状态：[status]
- 审批说明：[reason]
- 返回阶段：[contract|plan|implement|test|无需返回。]
- 条件：[condition]
- 后续动作：[follow-up]
```

`条件` 和 `后续动作` 只在需要时出现。

## 4. 规则

- 没有 explain，不允许审批。
- explain 必须锚定 contract、plan 和 test。
- 只有 `approval: pending` 的 explain 可以被审批。
- 非 `approved` 状态必须写明返回阶段。
- `conditionally-approved` 必须写明条件。
- 审批不修改 contract、plan，不补写 test，不直接更新 spec。
