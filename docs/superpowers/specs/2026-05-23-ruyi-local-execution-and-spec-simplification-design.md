# Ruyi 本地执行恢复与 Spec 目录简化设计

## 1. 背景

Ruyi 当前把单次交付拆成 `contract / plan / task / test / explain`，并为规范沉淀引入了 `spec-candidates / spec-archive / spec-patches`。实际使用中出现两个问题：

- 长 plan 在 agent compact 或切换 session 后，执行到哪一步无法稳定恢复。
- 多个本地中间目录被预创建并长期存在，但其中不少内容既不应提交给团队，也没有持续使用价值。

本设计以一个边界为前提：团队需要共享的是需求、方案、最终证据和正式规则；agent 执行中的流水与待处理草稿只留在本地。

## 2. 已确认决策

### 2.1 Git 提交的正式资产

以下内容描述团队应共同遵守或可复用的事实，继续提交 Git：

```text
.ruyi/
  contracts/
  plans/
  tests/
  explain/
  spec/
```

- `contracts/`：变更需求以及成熟项目接入形成的 baseline contract。
- `plans/`：团队认可的实施方案，包含 task 拆分、实施顺序、写入边界和完成条件。
- `tests/`：最终验证结论及必要证据。
- `explain/`：面向审批或交付理解的说明。
- `spec/`：正式规范的唯一当前版本。

### 2.2 本地按需产生的临时资产

仅保留两类本地资产，且不在 `init` 时预创建：

```text
.ruyi/
  tasks/
  spec-candidates/
```

- `tasks/`：agent 执行 plan 时的本地恢复点，不是团队交付文件。
- `spec-candidates/`：不能立即确认写入正式 spec 时的本地候选。

两者默认写入 `.gitignore`，只有实际需要时才由对应流程创建。

### 2.3 移除的目录和产物

以下目录不再作为 Ruyi 资产存在：

```text
.ruyi/workspace/
.ruyi/spec-archive/
.ruyi/spec-patches/
```

- `workspace/` 的职责过于泛化，当前只有完整迁移评估记录使用，未进入后续协作流程。
- `spec-archive/` 保存的是已决策的本地候选；正式采纳结果由 `spec/` 及 Git 历史承担，被拒绝内容无需长期保留。
- `spec-patches/` 是正式 spec 写入前的额外过渡层；用户确认后直接更新正式 spec 即可。

完整迁移不再生成 `workspace/init-evaluation-notes.md`。有效结论分别进入 baseline contract、`docs-registry.md` 或 `interview-bank.md`；未采用文档的临时排除记录不成为长期项目资产。

## 3. 长 Plan 的本地恢复流程

### 3.1 Plan 与 Task 的职责

`plan` 是正式设计文档，必须足以让团队理解要执行哪些工作：

- task 列表与顺序；
- 每个 task 的目标、写入边界和完成条件；
- 测试策略和最终收口条件。

`task` 文件不再承担正式流程凭证职责，而是 agent 的本地执行状态。它只在 agent 需要持久化执行位置时创建，例如多步实现、跨多轮会话执行或预期会发生 compact 的工作。

当 plan 含有多个 task，或任一 task 明显需要跨多个文件组/多轮验证执行时，`ruyi-implement` 必须在第一次源码修改前创建本地 task checkpoint。短小且可在单轮内完成的单 task 实现可以不创建本地文件。

### 3.2 本地 Task 路径与内容

本地恢复点沿用现有 task 路径结构：

```text
.ruyi/tasks/<module>/<feature>/<contract-date>/task-01.md
```

本地 task 至少记录：

```md
---
plan: plans/<module>/<feature>/<contract-date>.md
task_id: task-01
status: in-progress
updated_at: <time>
---

# Task：<名称>

## 当前进度

- 已完成步骤：
- 当前处理：
- 下一步：
- 已修改文件：
- 已运行验证：
- 阻塞项：
```

状态仅服务本地执行，使用 `pending / in-progress / done`。当 plan 返工或任务拆分变化时，旧本地 checkpoint 可删除并按当前 plan 重建，不为本地流水保留取代或撤销状态。

### 3.3 写入 Checkpoint 的时机

实现阶段存在本地 task 时，agent 应在以下时机更新其进度：

- 开始一个 task 时；
- 完成一个可单独确认的实现步骤时；
- 完成一组文件修改并准备转向下一步时；
- 运行验证后；
- 因阻塞需要询问用户或结束当前回复前。

### 3.4 Compact 或新 Session 后的恢复

`using-ruyi continue` 在已定位当前变更后按以下顺序判断：

1. 读取已确认的 contract 和 plan。
2. 查找同一路径下是否存在本地 task。
3. 若存在 `in-progress` task，读取其当前进度并继续执行。
4. 若只有 `pending` task，选择第一个待执行 task。
5. 若没有本地 task，依据正式 plan 与当前代码状态重新判断下一步；不能假定实现已完成。
6. 所有实现工作完成后执行 `ruyi-test`，最终共享证据写入正式 test 文档。

## 4. 流程门禁调整

当前路由以存在任意 `done task` 作为进入 test 的条件。这在多 task plan 下会误放行，并且在 task 本地化后无法作为团队可复现的门禁。

新规则为：

- `task` 不再是跨成员或跨机器的正式门禁。
- 非 tiny 变更进入实现前仍必须存在 confirmed plan。
- agent 从 implement 转到 test 前，应按 plan 的完成条件检查实现是否覆盖全部计划工作。
- `test` 输出承担共享的验证结论；`test` 未通过时不能进入 explain 或 approve。
- `explain` 的代码质量依据不得依赖本地 task 路径；需要共享的自检、review 或风险结论应写入正式 test 或 explain。
- `continue` 可利用本地 task 恢复位置，但没有本地 task 时仍应能基于正式 plan 继续工作。

因此，路由逻辑应移除“必须发现 done task 才可 test”的硬依赖，改为以 confirmed plan 与最终 test 结果控制正式流程。

## 5. Spec 沉淀流程简化

### 5.1 正式 Spec 是唯一当前真相

`.ruyi/spec/` 继续承载当前应遵守的长期规则、跨模块约束、项目结构事实和索引。正式 spec 不按日期存版本，历史由 Git 记录。

### 5.2 Candidate 只用于延后确认

出现可沉淀规则时：

1. agent 说明拟写入的正式 spec 目标文件和规则内容。
2. 用户当场确认，则直接更新 `.ruyi/spec/`。
3. 用户要求稍后集中处理，或代码反推产生的内容需要批量评审时，才创建本地 `.ruyi/spec-candidates/`。
4. candidate 评审通过后，用户确认写入正式 spec，并删除 candidate。
5. candidate 被拒绝或已失效，直接删除。

任何情况下，candidate 不能覆盖正式 spec，也不提交 Git。

### 5.3 Spec Skill 的职责

- `ruyi-spec-evolve`：识别一次交付中出现的稳定规则，优先引导用户直接更新正式 spec；需要延后决策时再生成 candidate。
- `ruyi-spec-discover`：从现有代码反推可能的规则；存在批量评审需求时生成 candidate。
- `ruyi-spec-merge`：保留为 candidate 评审入口，但行为简化为“确认后直接更新正式 spec 并删除 candidate”，不再生成 patch 或 archive。

## 6. 已审批需求返工与状态收敛

### 6.1 类型 D 改为需求重开

当前规则把 approved explain 之后发生的任何变化都视为新需求，并创建新的 contract。这会把同一需求因澄清遗漏导致的返工拆成多个合同。

新规则中，审批状态不直接决定是否新建 contract：

| 类型 | 含义 | Contract 处理 |
| --- | --- | --- |
| A | 未交付完成前的轻微调整 | 原 contract 原地修订 |
| B | 未交付完成前的范围或策略调整 | 原 contract 原地修订，重评 plan |
| C | 独立需求或业务语义改变 | 新建 contract，旧 contract 可记录被取代关系 |
| D | 已审批需求因澄清不足、遗漏或返工要求重新打开 | 原 contract 重新打开，不新建 contract |

类型 D 只有在本次调整仍属于原需求责任范围时成立。已完成能力之后提出的独立新能力，即使业务相关，也仍是类型 C。

### 6.2 唯一当前状态与历史记录

`contract / plan / test / explain` 都继续使用同一路径下的唯一文件表达当前流程状态，不为返工生成新的交付轮次文件，也不引入 contract revision。

当 approved 需求重新打开时：

- 文件头部状态改为当前有效状态。
- 文件正文更新为当前有效内容。
- 已经发生过的批准、验证和重新打开原因，写入简短的 `## 返工记录` 或 `## 状态变更记录`，用于审计，不作为当前结论读取。

返工记录至少包含：

```md
## 返工记录

### <YYYY-MM-DD> 重新打开

- 重新打开原因：需求澄清不充分 / 需求遗漏 / 已交付内容需返工
- 原审批结论：approved
- 原验证结论：passed / passed-with-notes
- 返回阶段：contract / plan / implement / test
- 当前调整范围：...
```

### 6.3 最小状态模型

状态只在影响路由或表达当前有效事实时存在。新模型如下：

| 产物 | 状态字段 | 状态集合 | 说明 |
| --- | --- | --- | --- |
| `contract` | `status` | `draft / confirmed / reopened` | `reopened` 表示已审批需求因返工重新进入澄清 |
| `plan` | `status` | `draft / confirmed / blocked` | 无新增状态；方案需重评时回退 `draft` |
| 本地 `task` | `status` | `pending / in-progress / done` | 只承担本地执行恢复，不保留取代或撤销审计 |
| `test` | `result` | `pending / passed / passed-with-notes / failed` | `pending` 表示当前需求需要重新验证 |
| `explain` | `approval` | `pending / approved / changes-requested` | 当前是否可视为交付通过；历史批准写入返工记录 |
| 本地 `spec-candidate` | `status` | `pending` | 处理后直接删除，不保留处理状态 |

对原审批阶段的状态收缩规则：

- `conditionally-approved` 不再保留。必须完成才可交付的条件，改为 `changes-requested` 并返回对应阶段；不影响交付的建议写入 approved explain 的后续事项。
- `rejected` 不再作为 explain 的长期审批状态。若只是要求修改，使用 `changes-requested`；若需求应终止，后续另行设计 contract 级终止语义，不在本次改动中扩大范围。

### 6.4 类型 D 状态迁移

已有 `approved` explain 的需求被确认为类型 D 时，状态按影响面回退：

```text
contract: confirmed -> reopened -> confirmed
plan:     confirmed -> draft -> confirmed      # 仅当实现方案需要调整
test:     passed / passed-with-notes -> pending -> passed / passed-with-notes
explain:  approved -> pending -> approved
```

规则如下：

- `contract` 必须写入返工记录并设置为 `reopened`；重新澄清完成后才回到 `confirmed`。
- 需求变化影响 task 拆分、实施顺序、接口对接或写入边界时，`plan` 回退为 `draft` 并重新确认；否则保持原计划有效。
- 已审批需求重新进入开发流程时，原 test 结论不再表示当前需求，必须重置为 `pending` 并重新验证。
- explain 的当前审批状态重置为 `pending`；旧的 approved 事实只保存在返工记录中，不再充当当前交付结论。
- 返回 implement 或 test 也不能借用旧审批结果直接进入 spec 沉淀。

## 7. 存量项目 Schema 升级

### 7.1 新增 `ruyi-upgrade`

Ruyi skills 的协议变化不能只影响新初始化项目。已经接入 Ruyi 的项目也需要把已有 `.ruyi/` 目录、状态字段、忽略规则和索引更新到当前 schema。

新增 `ruyi-upgrade` 作为存量项目升级 skill，职责是迁移 Ruyi 自身产物结构与协议，不重新进行项目接入，也不替用户判断业务内容。

统一入口仍是 `using-ruyi`：

```text
using-ruyi
  -> 项目未初始化：ruyi-init
  -> 项目已初始化且 schema 落后：ruyi-upgrade
  -> schema 已是当前版本：进入原请求对应阶段
```

### 7.2 Schema 版本

`.ruyirc` 增加独立的 `schema_version`：

```yaml
schema_version: 2
```

`schema_version` 只表示项目内 `.ruyi/` 资产协议版本，不等同于 Ruyi 发布版本。只有目录、状态或文件 schema 发生变化时才增加 schema 版本。

迁移必须使用显式、顺序执行的升级链：

```text
schema v1 -> v2 -> ... -> current
```

升级脚本必须幂等；重复运行不能重复追加记录、重复改写内容或损坏目录结构。

### 7.3 自动执行边界

发现 schema 落后后，`ruyi-upgrade` 自动执行确定性的结构迁移，不要求用户先确认迁移清单：

- 更新 `.ruyirc` 的 `schema_version`。
- 更新 `.gitignore` 中的 Ruyi 本地目录规则。
- 将 `tasks/` 迁移为本地执行恢复目录的语义。
- 停止创建或引用 `workspace / spec-archive / spec-patches`。
- 对可机械判断的目录、字段、说明文件进行迁移。
- 重建 `.ruyi/INDEX.md`。

以下业务含义判断不得自动改写，只能在升级总结中列为待人工审视项：

- 旧 `derived_from` contract 是否其实属于应重开的类型 D 返工。
- 旧 `conditionally-approved` 或 `rejected` explain 应归为哪种当前状态。
- 正式 spec 的业务规则是否需要拆分、合并或重写。
- 历史文档中的事实是否应进入 baseline contract。

### 7.4 废弃目录清理确认

`workspace / spec-archive / spec-patches` 等废弃本地目录不再参与新流程。升级发现这些目录时，不保留垃圾内容作为长期兼容层，但删除动作必须向用户确认一次。

提示应直接列出待清理目录：

```text
发现以下目录已被当前 Ruyi schema 废弃：

- .ruyi/workspace/
- .ruyi/spec-archive/
- .ruyi/spec-patches/

这些目录不再参与后续流程。是否删除？
```

- 用户确认：删除所列目录，并在升级总结中记录已清理项。
- 用户拒绝：保留目录，但后续 Ruyi 流程不再读取或写入，并在升级总结中记录遗留项。

### 7.5 升级输出

升级完成后输出简短总结，然后继续处理用户原本请求：

```md
Ruyi 项目已升级：schema v1 -> v2

已自动处理：
- 更新 `.ruyirc` 的 `schema_version`
- 更新 `.gitignore`
- `tasks/` 调整为本地执行恢复目录
- 重建 `.ruyi/INDEX.md`

已清理：
- 删除 `.ruyi/workspace/`
- 删除 `.ruyi/spec-archive/`
- 删除 `.ruyi/spec-patches/`

需要人工审视：
- 发现旧 `derived_from` contract，可能属于返工重开场景
- 发现旧 `conditionally-approved` explain，需要判断当前状态
```

## 8. Init 与存量项目迁移

### 8.1 新初始化项目

`ruyi-init` 只创建正式目录：

```text
contracts/
plans/
tests/
explain/
spec/
```

初始化时写入忽略规则，但不预创建本地目录：

```gitignore
.ruyi/tasks/**
.ruyi/spec-candidates/**
```

完整迁移继续允许生成 baseline contract、`docs-registry.md` 与 `interview-bank.md`，不再生成 `workspace` 及评估 notes。

### 8.2 已接入项目

已有项目升级时采用以下处理方式：

- `spec/` 与已有正式 contract、plan、test、explain 保持原位。
- 已存在的 pending `spec-candidates/` 可继续评审；完成后直接写入正式 spec 并删除。
- `spec-archive/`、`spec-patches/`、`workspace/` 由 `ruyi-upgrade` 检出并在用户确认后删除。
- 若已有被提交的 `tasks/` 含有最终质量结论，应先把仍有价值的结论整理进 test 或 explain，再将 task 调整为本地资产。
- 已经使用 `derived_from` 创建但实际属于原需求返工的旧链路不自动迁移；后续处理同类变更时改用原 contract 重新打开规则。

## 9. 实施影响范围

后续实施预计涉及：

- `README.md`、安装及流程说明文档。
- `ruyi-init` 的目录生成、完整迁移产物与 `.gitignore` 写入规则。
- 新增 `ruyi-upgrade`，负责 `.ruyirc` schema 版本检测、顺序迁移、废弃目录清理提示与升级总结。
- `using-ruyi` 的 continue 路由与 test 进入条件。
- `using-ruyi` 在正式流程路由前检测并触发项目 schema 升级。
- `ruyi-plan`、`ruyi-implement`、`ruyi-test`、`ruyi-explain` 对 task 职责和门禁的描述。
- `ruyi-contract`、`ruyi-approve` 以及 `using-ruyi` 的 A/B/C/D 分类、返工记录与最小状态枚举。
- `ruyi-spec-evolve`、`ruyi-spec-discover`、`ruyi-spec-merge` 的候选处理行为。
- 所有发布 skill 内重复保存的相关 schema/reference 副本。

## 10. 验证要点

实施完成后至少验证：

- init 后不生成 `workspace / tasks / spec-candidates / spec-archive / spec-patches` 目录，但存在正确的本地忽略规则。
- 完整迁移不再生成 `init-evaluation-notes.md`，有效业务事实仍进入 baseline contract。
- 长 plan 执行中可创建本地 task；新 session 通过 `continue` 能恢复 `in-progress` task。
- 多 task 或预期跨轮执行的 plan 会在首次源码修改前写入本地 checkpoint。
- 未存在本地 task 的环境仍可按 confirmed plan 进入实现及验证流程。
- 多 task 计划不会因为单个本地 task 为 `done` 而错误认为交付已完成。
- explain 可在没有本地 task 文件的团队环境中理解代码质量与风险结论。
- 用户确认规则后可直接更新正式 spec；延后评审时才创建 candidate。
- candidate 评审后不会生成 archive 或 patch。
- 已审批需求的小范围返工不会创建新 contract，而会将原 contract 置为 `reopened` 并记录原因。
- 类型 D 返工后，test 与 explain 的当前状态会被重置，旧 `passed / approved` 不能误放行后续阶段。
- `conditionally-approved / rejected` 不再作为 explain 当前状态产生；spec-candidate 处理后不会留下终态文件。
- 已初始化但 schema 落后的项目在进入主流程前自动路由到 `ruyi-upgrade`。
- 升级脚本可重复执行且不会重复迁移或破坏正式产物。
- 升级自动处理确定性结构变更，并只对废弃目录删除动作要求用户确认。
- 升级不会自动改写旧 `derived_from`、旧审批语义或正式 spec 的业务内容。
