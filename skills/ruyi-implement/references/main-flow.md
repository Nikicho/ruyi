# Ruyi 主流程

## 1. 目标

本文件定义 Ruyi 本体固定提供的开发主流程。所有 Ruyi 子 skill 都围绕该流程工作，项目不能改写主流程本身。

项目如有特殊操作，只能通过 `.ruyi/project-actions.md` 追加动作。

## 2. 主流程阶段

1. 初始化
2. 存量结构升级（按需）
3. 需求定义
4. 开发计划
5. 编码实现
6. 测试验证
7. 开发简报
8. 审批
9. 知识沉淀（按需）

## 3. 阶段进入规则

- 未初始化项目，必须先进入初始化阶段。
- 已初始化但 `schema_version` 落后时，必须先进入 `ruyi-upgrade`；升级只机械迁移结构，废弃目录删除需确认。
- 未完成初始化前，除 `ruyi-init` 外，不进入其他子 skill 的正式执行。
- 有明确功能需求、修复目标或业务重构目标时，先进入需求定义阶段。
- 代码优化、代码微重构等无行为变化维护请求，可由 `using-ruyi` 路由到 `ruyi-implement` 轻量维护模式；该模式不要求 contract / plan / task。
- 没有 `contract` 或等价需求定义时，不进入开发计划阶段。
- 没有 `plan` 或等价实施计划时，不进入正式需求实现阶段；轻量维护模式除外。
- 没有需求定义锚点时，不进入开发简报阶段。
- 没有 `test` 验证结果时，不进入开发简报阶段。
- 审批发生在开发简报之后，不允许绕过开发简报直接进入审批。
- 没有 explain 或等价结果依据时，不进入知识沉淀阶段。
- 知识沉淀不是交付完成门禁；发现可复用规则时才按需进入，默认先落项目层，再评估是否具备升级到 team 层的条件。

## 4. 分档规则

Ruyi 主流程默认走 `standard` 档。contract 可通过 `size` 字段声明三档：

| size | 流程 | 约束 |
| --- | --- | --- |
| `tiny` | contract -> implement -> test -> complete | 仅适用于单文件、无业务规则变化、无新增 UI 状态的小改动；不能用于 `fix` |
| `standard` | 完整主流程 | 默认档 |
| `large` | 完整主流程，plan 必须拆解执行步骤 | 适用于多模块或复杂需求；跨轮次时创建本地 checkpoint |

tiny 不是绕过 Ruyi。tiny 只是省略 plan/explain/approve，仍必须有已确认 contract 和 test 证据。

## 5. 阶段产物

- 初始化：`.ruyirc`、`.ruyi/`
- 需求定义：`contract`
- 开发计划：`plan`
- 编码实现：代码变更、实现自检与代码质量结论
- 测试验证：`test`
- 开发简报：`explain`
- 审批：更新 explain 中的 `approval`
- 知识沉淀：用户当场确认时直接更新正式 `spec`；延后审视时生成本地 `spec-candidate`

长 plan 的本地执行恢复点保存在 `.ruyi/tasks/`，只使用 `pending / in-progress / done`，不提交 git，也不作为测试或 explain 的正式门禁。

## 6. 人工确认点

- 初始化完成后的确认
- 需求定义完成后的确认
- 开发简报后的审批确认

## 7. 项目特殊操作挂接规则

- 项目不能改写主流程。
- 项目只能通过 `.ruyi/project-actions.md` 追加特殊操作。
- 特殊操作只能挂接在某个阶段之前或之后。
- 特殊操作不能替代阶段产物。
- 特殊操作不能改变阶段顺序。

核心原则：`main-flow.md` 定义必须经过哪些阶段，各子 skill 定义该阶段内部如何执行。

## 8. 主流程外的人工动作

以下动作不属于单次需求主流程，但允许周期性执行：

- `ruyi-spec-discover`：从现有代码反推本地 spec-candidate，不直接写正式 spec。
- `ruyi-spec-merge`：人工确认本地 candidate，采纳时直接更新正式 spec 后删除候选。
- 轻量维护模式：用于代码优化、代码微重构等无行为变化维护，不生成 contract / plan / task / explain / spec-candidate。

## 9. 中途变更处理

中途变更不新增阶段，也不新增 skill。它在现有 contract / plan / implement / test 阶段内部处理。

agent 必须先把变更分类说给用户确认，用户确认前不得落盘或改代码。

| 类型 | 名称 | 判断 | 处理 |
| --- | --- | --- | --- |
| A | 微调 | 不改业务规则、验收标准、接口路径/方法，不影响已完成产物 | contract 原地修订，追加 `## 修订记录` |
| B | 范围扩展或策略调整 | 改需求范围、接口范围、接口对接或影响执行方式，但不改核心业务定义 | contract 修订，plan 重评，本地 checkpoint 按当前 plan 重建 |
| C | 语义变化 | 改用户故事核心、业务规则、已确认验收标准或需求类型 | 新建日期 contract，旧 contract 加 `superseded_by`，plan/test 重做 |
| D | 审批后返工 | 已有 `approved` explain 后发现原需求澄清遗漏或交付需返工 | 重开同一 contract 并记录返工原因；当前 plan/test/explain 按返回阶段重置 |

独立的新需求仍应新建 contract；对原需求的返工在同一文件路径保留当前唯一状态和返工记录。
