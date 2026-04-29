---
name: ruyi-approve
description: Routed by using-ruyi. Use only after using-ruyi has determined the next stage is approval. Handles PM approval, rejection, conditional acceptance, or return decisions to contract, plan, coding, or test.
---

# Ruyi Approve

## 1. 适用场景

- PM 需要审批本次交付。
- explain 已生成，需要记录审批结论。

## 2. 硬门禁

- 项目必须已初始化。
- 必须存在 explain 或等价开发简报。
- explain 必须有明确对应 contract、plan 和 test。
- 不允许绕过 explain 直接审批。

## 3. 执行原则

- 审批关注交付是否可接受。
- 审批不替代代码 review。
- 审批结论更新 explain 的头部元信息，并在正文末尾追加审批结论。

## 4. 执行步骤

1. 检查项目是否已初始化。
2. 读取 explain。
3. 读取 `references/approval-discipline.md`。
4. 确认 explain 对应的 contract、plan、test 和验证摘要。
5. 记录审批结论。
6. 未通过时明确返回 contract、plan、implement 或 test。
7. 通过时允许进入 `ruyi-spec-evolve` 判断。

## 5. 产物要求

- 审批结论。
- 如需修改，明确返回到哪个阶段。
- 如通过，可进入知识沉淀判断。

## 6. 脚本调用

确认 explain 已经生成，并且用户已经给出明确审批意见后，可以使用脚本记录审批结论：

```bash
python <skills-dir>/ruyi-approve/scripts/approve_update.py --project <project> --module <module> --feature <feature> --date <YYYY-MM-DD> --status <approved|changes-requested|conditionally-approved|rejected> --reason <reason>
```

非 `approved` 状态必须追加：

```bash
--return-stage <contract|plan|implement|test>
```

`conditionally-approved` 还必须追加：

```bash
--condition <condition>
```

脚本职责：

- 校验项目已初始化。
- 校验 explain 存在。
- 校验 explain 锚定 contract、plan 和 test。
- 只更新 `approval: pending` 的 explain。
- 不修改 contract、plan、test 或 spec。

## 7. 必读参考

- `references/main-flow.md`
- `references/explain-schema.md`
- `references/approval-schema.md`
- `references/knowledge-evolution.md`
- `references/approval-discipline.md`
