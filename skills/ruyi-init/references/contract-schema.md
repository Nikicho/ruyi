# Contract Schema

## 1. 对象定位

`contract` 是某模块下某功能在某日期生效的业务需求定义与验收定义。

`contract` 是纯业务文档，不写实现细节。

成熟项目完整迁移时允许生成 `baseline contract`，用于记录某模块当前已经存在的业务事实。baseline contract 不是一次新需求，不直接进入 plan / implement / test；后续相关变更应先读取 baseline，再创建本次变更 contract。

`contract` 通过 `size` 字段选择需求分级通道：

- `tiny`：单文件、无业务规则变化、无 UI 状态新增的小改动。
- `standard`：默认档，适用于涉及 UI 行为、业务规则或多文件协作的常规需求。
- `large`：涉及多模块、验收标准较多或明显需要拆分 task 的需求。

## 2. 路径规则

路径格式：

```text
contracts/<module>/<feature>/<YYYY-MM-DD>.md
contracts/<module>/_baseline/current.md
contracts/<module>/<feature>/baseline.md
```

规则：

- `module` 优先对齐项目现有模块目录。
- `feature` 使用业务对象名，不使用动作名。
- `feature` 只要求模块内唯一。
- 日期格式固定为 `YYYY-MM-DD.md`。
- `_baseline/current.md` 和 `<feature>/baseline.md` 只用于成熟项目当前业务事实基线，不参与日期版本判断。

## 3. 正文结构

```md
# Contract：[功能名称]

## 用户故事
## 需求范围
## 业务规则
## 修复事实
## 接口范围
## 验收标准
## 测试用例
## 修订记录
## 返工记录
```

`## 修复事实` 仅在 `type: fix` 时必填，必须包含：

- 问题现象。
- 影响范围。
- 验证方向。

`## 接口范围` 在本次需求涉及后端接口、BFF、mock 接口或接口字段变化时必填。该段只记录本次涉及接口的范围，不抄完整 API 文档。

推荐结构：

```md
## 接口范围

| 接口 | 方法 | 类型 | 来源 | 备注 |
| --- | --- | --- | --- | --- |
| /api/orders/search | POST | 新增 | 待后端补充 | 关键词搜索 |
```

类型枚举：`新增 / 修改 / 复用 / 废弃`。

临时定义仅在后端权威文档未就位时允许，必须标注来源和替换时机：

```md
### /api/orders/search（临时定义，待后端正式文档替换）

- 临时定义来源：与后端在 2026-04-28 确认
- 替换时机：Apifox / Swagger 发布后删除本段，改为链接权威源
```

`## 修订记录` 在中途变更类型 A/B 时使用；类型 C 新建日期 contract，旧 contract 只在 frontmatter 写 `superseded_by`。`## 返工记录` 在已审批原需求被重新打开时使用。

## 4. 演进规则

- 语义变化时，新建新的日期文件。
- 非语义修订时，原地修改当前文件。
- 当前生效版本等于同目录下最新日期文件。
- 中途变更必须先分类并获得用户确认：
  - 类型 A：微调，不改业务规则、验收标准、接口路径/方法，不影响已完成产物，原地修订并追加 `## 修订记录`。
  - 类型 B：范围扩展或策略调整，改需求范围、接口范围、接口对接或影响 task，contract 原地修订，plan 进入重评。
  - 类型 C：语义变化，改用户故事核心、业务规则、已确认验收标准或需求类型，新建日期 contract，旧 contract 加 `superseded_by`。
  - 类型 D：审批后返工，重开同一 contract，写入返工记录并重置当前交付状态；不新建 contract。

## 5. 状态规则

- `draft`：草稿，尚未确认，不能进入 plan。
- `confirmed`：已确认，可进入 plan。
- `reopened`：已审批原需求因澄清遗漏或交付返工而重新打开，需重新澄清后回到 `confirmed`。

frontmatter 允许包含：

- `superseded_by`：类型 C 使用，指向取代当前 contract 的新日期文件。

## 6. 分档规则

- `tiny` 必须仍然有 contract、implement 和 test 证据。
- `tiny` 跳过 plan 和 approve；如后续发现范围扩大，必须升级为 `standard` 并补 plan。
- `tiny` 不允许包含业务规则变化，不允许用于 `fix` 类型。
- `standard` 默认走完整主流程。
- `large` 必须进入 plan，且 plan 应拆分多个 task。

## 7. 硬门禁

- 没有明确需求目标时，不落盘。
- 没有验收标准时，contract 不能标 `confirmed`。
- 没有测试用例时，contract 不能标 `confirmed`，也不进入 plan；draft 允许至少 1 条占位骨架。
- `confirmed` 且 `size: standard / large` 时，测试用例必须覆盖正常路径、边界、异常三类。
- 涉及接口但缺少 `## 接口范围` 时，不能标 `confirmed`。
- `fix` 类型缺少问题现象、影响范围或验证方向时，不落盘。
- `fix` 类型不能标记为 `tiny`。
- 未确认的 `draft` contract 不进入 plan。
- 未初始化项目，不正式创建或维护 contract。
- `contract` 不能整体升级为 `spec`，只能作为提炼来源。

