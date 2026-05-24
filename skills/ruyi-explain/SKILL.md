---
name: ruyi-explain
description: Deprecated in Ruyi schema v3. Do not use for normal delivery flow; verification summary and approval now live in test.
---

# Ruyi Explain

## 状态

`ruyi-explain` 已在 schema v3 主流程中退役。

正式交付流程不再生成 `.ruyi/explain/`：

```text
contract -> plan -> implement -> test -> approve -> complete
```

其中：

- `ruyi-test` 记录验收、证据、验证结论和风险。
- `ruyi-approve` 直接更新对应 test 的 `approval` 状态。
- `ruyi-spec-evolve` 后续从 approved test 或代码反推结果判断是否沉淀 spec。

## 处理方式

如果用户要求生成 explain：

1. 说明 schema v3 已不再使用 explain。
2. 引导用户回到 `ruyi-test` 查看或补充验证摘要。
3. 如需要审批，进入 `ruyi-approve` 更新 test。
4. 如旧项目存在 `.ruyi/explain/`，进入 `ruyi-upgrade` 迁移到 schema v3。

## 脚本行为

`scripts/explain_create.py` 和 `scripts/explain_lint.py` 仅保留为兼容提示入口，直接返回 `deprecated-in-schema-v3`，不会创建或修改 `.ruyi/explain/` 文件。
