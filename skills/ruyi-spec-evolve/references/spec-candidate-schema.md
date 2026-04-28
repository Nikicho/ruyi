# Spec Candidate Schema

## 1. 对象定位

`spec-candidate` 是知识沉淀候选，用于记录“这次交付中可能值得沉淀为长期规范的内容”。

它不是正式 spec，不会自动改变项目长期规则。

## 2. 路径规则

路径格式：

```text
spec-candidates/<module>/<feature>/<contract-date>.md
```

## 3. 头部元信息

建议包含：

- 来源 explain
- 所属模块
- 功能对象
- 日期
- 目标层级
- 目标 spec 文件
- 状态

状态允许：

- `pending`：待人工确认。
- `merged`：已合入正式 spec。
- `rejected`：已拒绝。
- `superseded`：已被其他候选取代。

旧版 `candidate` 视为 `pending`。

## 4. 正文结构

```md
# Spec Candidate：[名称]

## 沉淀建议
## 依据
## 适用范围
## 不应沉淀内容
## 待确认问题
```

## 5. 规则

- 必须锚定已审批通过的 explain。
- 来源 explain 必须锚定 contract、plan 和 test。
- 候选必须包含目标层级、目标 spec、建议内容、证据和适用范围。
- 不允许把 contract、test、explain 原文搬运进候选。
- 候选必须说明适用范围。
- 候选必须说明哪些内容不应沉淀。
- team 层内容只形成候选，不自动写入 `.ruyi-team`。
- 候选合入正式 spec 只能通过 `ruyi-spec-merge` 的人工确认流程执行。
