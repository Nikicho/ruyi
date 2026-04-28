# Contract Schema

## 1. 对象定位

`contract` 是某模块下某功能在某日期生效的业务需求定义与验收定义。

`contract` 是纯业务文档，不写实现细节。

`contract` 通过 `size` 字段选择需求分级通道：

- `tiny`：单文件、无业务规则变化、无 UI 状态新增的小改动。
- `standard`：默认档，适用于涉及 UI 行为、业务规则或多文件协作的常规需求。
- `large`：涉及多模块、验收标准较多或明显需要拆分 task 的需求。

## 2. 路径规则

路径格式：

```text
contracts/<module>/<feature>/<YYYY-MM-DD>.md
```

规则：

- `module` 优先对齐项目现有模块目录。
- `feature` 使用业务对象名，不使用动作名。
- `feature` 只要求模块内唯一。
- 日期格式固定为 `YYYY-MM-DD.md`。

## 3. 正文结构

```md
# Contract：[功能名称]

## 用户故事
## 需求范围
## 业务规则
## 修复事实
## 验收标准
## 测试用例
```

`## 修复事实` 仅在 `type: fix` 时必填，必须包含：

- 问题现象。
- 影响范围。
- 验证方向。

## 4. 演进规则

- 语义变化时，新建新的日期文件。
- 非语义修订时，原地修改当前文件。
- 当前生效版本等于同目录下最新日期文件。

## 5. 状态规则

- `draft`：草稿，尚未确认，不能进入 plan。
- `confirmed`：已确认，可进入 plan。

## 6. 分档规则

- `tiny` 必须仍然有 contract、implement 和 test 证据。
- `tiny` 跳过 plan、task、explain、approve 和 spec-candidate；如后续发现范围扩大，必须升级为 `standard` 并补 plan。
- `tiny` 不允许包含业务规则变化，不允许用于 `fix` 类型。
- `standard` 默认走完整主流程。
- `large` 必须进入 plan，且 plan 应拆分多个 task。

## 7. 硬门禁

- 没有明确需求目标时，不落盘。
- 没有核心验收标准和测试用例时，不进入 plan。
- `fix` 类型缺少问题现象、影响范围或验证方向时，不落盘。
- `fix` 类型不能标记为 `tiny`。
- 未确认的 `draft` contract 不进入 plan。
- 未初始化项目，不正式创建或维护 contract。
- `contract` 不能整体升级为 `spec`，只能作为提炼来源。
