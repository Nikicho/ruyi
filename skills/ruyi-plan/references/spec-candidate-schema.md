# Spec Candidate Schema

## 1. 对象定位

`spec-candidate` 是本地临时知识候选，用于记录“可能值得沉淀为长期规范”的内容。

它不是正式 spec，不会自动改变项目长期规则，也不应该提交到 git 误导团队成员。

## 2. 路径规则

路径格式：

```text
.ruyi/spec-candidates/<target-layer>/<target-spec-path>
```

示例：

```text
.ruyi/spec-candidates/project/coding-baseline.md
.ruyi/spec-candidates/project/references/shared/table/columns.md
.ruyi/spec-candidates/project/references/modules/orders/search.md
```

候选路径跟随目标 spec 路径，不使用日期做版本目录。日期只作为来源 explain 的锚点。

## 3. 头部元信息

建议包含：

- `source_explain`
- `module`
- `feature`
- `date`
- `target_layer`
- `target_spec`
- `local_only: true`
- `status`

新 candidate 的状态仅允许 `pending`：待人工确认。旧版状态由 `ruyi-upgrade` 报告人工处理，不作为新流程输出。

## 4. 正文结构

```md
# Spec Candidate：<名称>

## 沉淀建议
## 依据
## 适用范围
## 不应沉淀内容
## 待确认问题
```

## 5. 规则

- 必须锚定已审批通过的 explain，除非由 `ruyi-spec-discover` 从代码反推生成并明确标记来源。
- 来源 explain 必须锚定 contract、plan 和 test。
- 候选必须包含目标层级、目标 spec、建议内容、证据和适用范围。
- 不允许把 contract、test、explain 原文搬运进候选。
- 候选必须说明适用范围。
- 候选必须说明哪些内容不应沉淀。
- team 层内容只形成候选，不自动写入 `.ruyi-team`。
- 用户确认采用项目层候选时，直接更新当前正式 spec，再由 `ruyi-spec-merge` 删除已处理 candidate。
- 用户拒绝或以更新提案取代候选时，直接删除本地 candidate，不归档。
- candidate 可以被 agent 默认读取，但只能作为待确认信号，不能覆盖正式 spec。
