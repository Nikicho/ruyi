# Ruyi Schema v3 完整升级与索引收敛设计

## 1. 背景与目标

Ruyi 已完成 schema v2 的第一轮流程简化，但实际存量项目仍存在三个结构性问题：

- 旧项目可能保留 `frontend-baseline.md`，没有真正拆分为开发过程规范与代码编写规范。
- `references/` 中的细分规范没有稳定的运行时检索入口，agent 容易只读取顶层 baseline 后直接开发。
- `explain` 与 `test / approve / open-questions` 职责重叠，持续保留会产生重复、过时且难维护的正式资产。

schema v3 的目标是把“升级”定义为完整文档协议迁移：

- 已接入项目升级结束后，全部正式 Ruyi 资产符合当前 skills 的结构与读取规则。
- 团队共享的 `.ruyi` 正式资产在升级完成后提交并推送，避免成员继续消费旧格式。
- 本地执行恢复点与待审候选继续保持 local-only，不混入团队资产。

## 2. 已确认决策

### 2.1 Schema 版本

- 当前协议版本提升为 `schema_version: 3`。
- `.ruyirc` 存在但没有 `schema_version` 时，视为 legacy v1 项目，直接迁移到 v3，不生成或保留 v2 中间形态。
- `using-ruyi` 检测到低于 v3 的项目时，必须先进入 `ruyi-upgrade`。
- `ruyi-upgrade` 不允许长期停留在“部分升级完成”状态；进入升级后应持续处理到正式资产满足 v3，再恢复原需求流程。

### 2.2 正式资产与本地资产

Git 正式资产：

```text
.ruyi/
  INDEX.md
  contracts/
  plans/
  tests/
  spec/
```

本地按需资产：

```text
.ruyi/tasks/
.ruyi/spec-candidates/
```

废弃并在升级中删除的资产：

```text
.ruyi/explain/
.ruyi/workspace/
.ruyi/spec-archive/
.ruyi/spec-patches/
```

### 2.3 主流程

standard / large 的主流程调整为：

```text
init/upgrade -> contract -> plan -> implement -> test -> approve -> complete
```

`tiny` 沿用轻路径：

```text
contract -> implement -> test -> complete
```

`tiny` 不强制进入审批；一旦范围升级为 standard / large，则进入完整主流程。

### 2.3 Contract 与 Plan 的架构讨论边界

`contract` 阶段允许讨论由架构背景暴露出来的业务约束，但不展开实施方案。

可留在 `contract` 的内容：

- 会影响用户可见行为、兼容范围、性能目标、安全边界或交付范围的约束。
- 外部系统、历史数据、权限模型或运行环境对验收标准的影响。
- 必须在本次需求中明确的范围内、范围外和自然语言测试用例。

应转入 `plan` 的内容：

- 组件拆分、模块分层、状态管理、缓存、hook、store、事件机制等实现方案。
- API service 组织、mock 放置、错误处理、类型生成、目录调整和代码重构步骤。
- 技术方案比较、任务拆分、实施顺序、写入范围和验证策略。

当用户在 `contract` 对话中进入实施设计时，agent 必须短提醒并收口：

> 这个问题属于实施设计，会在 `plan` 阶段确定。当前 contract 只确认它是否形成业务约束或验收要求：它会影响用户行为、兼容范围、性能目标或交付边界吗？

如果答案影响业务或验收，写入 `contract` 的业务规则、范围或验收标准；如果不影响，则不写入 `contract`，待 contract confirmed 后在 `plan` 中继续展开。

反向规则同样成立：`ruyi-plan` 若发现方案选择实际改变用户行为、业务规则、接口范围或验收标准，必须返回 `ruyi-contract` 重新澄清，不能在 plan 中隐式扩展需求。

## 3. Spec 与 Baseline 迁移

### 3.1 顶层 Spec 结构

项目层 `.ruyi/spec/` 固定包含：

```text
spec/
  INDEX.md
  project-overview.md
  project-structure.md
  development-baseline.md
  coding-baseline.md
  testing-baseline.md
  api.md
  open-questions.md
  docs-registry.md        # 仅完整迁移需要时存在
  interview-bank.md       # 仅完整迁移需要时存在
  references/
    shared/
    modules/
```

不再保留：

```text
spec/frontend-baseline.md
spec/references/shared/INDEX.md
spec/references/modules/INDEX.md
```

### 3.2 `frontend-baseline.md` 拆分

升级发现旧 `frontend-baseline.md` 时，必须读取并迁移其有效内容：

- 开发过程要求进入 `development-baseline.md`，例如 `npm run lint`、构建、单测、浏览器验证、`git add` / 提交前检查。
- 代码编写规则进入 `coding-baseline.md`，例如组件边界、状态管理、样式、类型、请求层与错误处理。
- 无法确认为正式规则、但会影响后续开发判断的长期问题进入 `open-questions.md`。

拆分完成后直接删除 `frontend-baseline.md`，不保留兼容入口。历史追溯依赖 git。

### 3.3 References 检索规则

顶层 baseline 只保存通用约束和到详细规则的索引信息。详细规则继续放在：

```text
references/shared/<domain>/...
references/modules/<module-or-feature>/...
```

同一个公共组件或业务功能只使用一个目录，再按主题拆分文件。

`.ruyi/spec/INDEX.md` 是唯一 spec 检索入口，负责描述：

- 全局必读 baseline。
- 按公共能力触发的 `references/shared/` 规范。
- 按模块、功能或写入范围触发的 `references/modules/` 规范。
- 与开发目标相关的 `open-questions.md` 章节入口。

### 3.4 旧 Spec 中业务事实的迁移

早期接入的成熟项目可能将当前模块业务事实写入正式 spec。schema v3 升级必须重新划定边界：

- 长期开发规则、跨模块约束、项目结构事实和索引继续保留在 spec。
- 模块当前已有的业务行为、业务状态、既有能力与代码观察事实迁入 `.ruyi/contracts/<module>/_baseline/current.md` 或 `.ruyi/contracts/<module>/<feature>/baseline.md`。
- 明显与长期规则混排的文档，应拆出业务事实后保留剩余有效规则，不整体删除。
- 无法可靠判断归属的段落，升级流程内询问用户，取得结论后继续完成迁移。

迁移完成后，`using-ruyi` 仅在路由到具体模块或 feature 后把 baseline contract 作为业务背景读取，不能将其当成本次变更 contract。

## 4. 取消 Explain 与审批归位

### 4.1 删除独立 `explain`

schema v3 不再创建 `.ruyi/explain/`，也不再保留 `ruyi-explain` 主流程阶段。

原因：

- 验证结果与证据已经属于 `test`。
- 审批结论属于 `approve`。
- 长期未知问题属于 `spec/open-questions.md`。
- 单独的交付摘要会重复已有正式信息，并增加迁移与读取成本。

发布结构中 `ruyi-explain` 应移除或仅作为明确废弃提示，不得继续生成新正式文件。

### 4.2 `test` 成为交付与审批载体

正式 `test` 保存：

- contract 锚点；非 tiny 同时保存 plan 锚点。
- 验收结果与验证证据。
- `result: passed | passed-with-notes | failed | pending`。
- 仅当影响本次审批时保留的失败项、未覆盖项或阻断风险。
- 审批字段 `approval: pending | approved | changes-requested`。
- 审批说明和 `changes-requested` 时的返回阶段。
- 已审批需求返工后的状态变更与重测记录。

`ruyi-approve` 改为审批目标 test，不再更新 explain。

### 4.3 风险与 `open-questions.md` 的边界

| 内容 | 归属 |
| --- | --- |
| 某次交付未通过、未覆盖或阻断审批的风险 | 当前 `test` |
| 影响后续开发决策、尚未确认的长期规则或项目事实 | `spec/open-questions.md` |
| 新功能或未来优化诉求 | 新 contract |
| 只影响当前执行恢复的临时判断 | 本地 task checkpoint |

`open-questions.md` 必须进入规范检索链：相关模块进入 contract、implement、test 或 spec-evolve 时，agent 应通过 `spec/INDEX.md` 发现并读取命中问题；问题确认后，应迁移到正式 spec 或 baseline contract，并从 open questions 移除。

## 5. 两层 INDEX 设计

### 5.1 `.ruyi/INDEX.md`：流程索引

`.ruyi/INDEX.md` 是自动生成、提交 git 的团队共享流程索引。

职责：

- 供 `using-ruyi` 在 Ritual 与路由阶段轻量定位活动需求。
- 聚合每个 feature 的 contract、plan、test 和审批状态。
- 避免在未定位 feature 前读取多个正文文件。

来源仅限：

```text
contracts/
plans/
tests/
```

不进入索引：

```text
tasks/
spec-candidates/
explain/            # v3 已删除
```

示例：

```md
# Ruyi Work Index

## orders / keyword-search

- Contract：`.ruyi/contracts/orders/keyword-search/2026-05-23.md`
- Plan：`.ruyi/plans/orders/keyword-search/2026-05-23.md`
- Test：`.ruyi/tests/orders/keyword-search/2026-05-23.md`
- 需求状态：confirmed
- 验证状态：passed
- 审批状态：approved
```

维护规则：

- 由脚本从正式产物重建，不人工维护。
- 正式产物变更、升级完成或合并冲突解决后必须重建。
- 合并冲突时以 `contracts / plans / tests` 为真相来源。

### 5.2 `.ruyi/spec/INDEX.md`：规范检索索引

`.ruyi/spec/INDEX.md` 是提交 git 的正式规范入口。

职责：

- 指向全局 baseline。
- 按触发范围索引具体 reference。
- 索引影响当前开发目标的 open question。

示例：

```md
# Spec Index

## 全局必读

- 开发操作约束：`development-baseline.md`
- 代码编写约束：`coding-baseline.md`
- 测试约束：`testing-baseline.md`

## Shared References

| 触发范围 | 必读规范 |
| --- | --- |
| table 组件 | `references/shared/table/usage.md`、`references/shared/table/columns.md` |
| API 请求 | `references/shared/api/conventions.md` |

## Module References

| 模块或写入范围 | 必读规范 |
| --- | --- |
| orders | `references/modules/orders/search.md` |

## 待确认问题索引

| 影响范围 | 问题入口 |
| --- | --- |
| orders / permission | `open-questions.md#订单权限失败处理` |
```

维护规则：

- 新增、移除、合并或重组正式 reference 时必须同步更新。
- `ruyi-init` 创建基础结构。
- `ruyi-upgrade` 合并旧二级 INDEX 内容并删除二级 INDEX。
- `ruyi-spec-discover` 与 `ruyi-spec-evolve` 在正式 spec 变更落地时维护索引。
- `ruyi-spec-merge` 处理候选并更新正式 spec 后维护索引。

## 6. Skill 读取入口同步

索引变更必须同步所有相关 skill，不允许只改 schema 说明文件。

| Skill | v3 读取或维护入口 |
| --- | --- |
| `using-ruyi` | 路由前只读 `.ruyi/INDEX.md`；不读 spec 正文 |
| `ruyi-init` | 创建两个正式 INDEX，不创建 `explain/` 或二级 spec INDEX |
| `ruyi-upgrade` | 完整迁移资产并重建两个 INDEX |
| `ruyi-contract` | 定位 module/feature 后读取 `.ruyi/spec/INDEX.md`、相关 baseline contract、命中的正式规范与 open questions；识别实施设计话题并提醒转入 plan |
| `ruyi-plan` | 读取 `.ruyi/spec/INDEX.md` 及命中的实现、测试约束；发现需求或验收变化时返回 contract |
| `ruyi-implement` | 修改源码前必须读取 `.ruyi/spec/INDEX.md`、`development-baseline.md`、`coding-baseline.md` 及命中的 references/open questions |
| `ruyi-test` | 验证前必须读取 `.ruyi/spec/INDEX.md`、`development-baseline.md`、`testing-baseline.md` 及命中的 references/open questions |
| `ruyi-approve` | 审批目标改为 test；读取当前 test 的验证与风险信息 |
| `ruyi-spec-discover` | 读取并维护 `.ruyi/spec/INDEX.md`；待审候选仍为本地资产 |
| `ruyi-spec-evolve` | 正式规则确认落地时同步 `.ruyi/spec/INDEX.md` 与 open questions |
| `ruyi-spec-merge` | 处理本地 candidate 并更新正式 spec 后同步 `.ruyi/spec/INDEX.md` |
| `ruyi-explain` | 从主流程和发布结构移除，或仅输出已废弃迁移提示 |

仓库中各 skill 自带的 `references/*.md` 副本必须同步更新，避免某个阶段继续加载旧流程。

项目中的 Ruyi 入口文件也属于升级范围：

| 入口文件 | v3 升级行为 |
| --- | --- |
| `CLAUDE.md` | 更新 Ruyi 管理段落，指向无 explain 的主流程和新 INDEX 入口 |
| `.claude/settings.json` | 更新 Ruyi 管理的 reminder hook，不再提示旧读取范围或旧阶段 |
| `.claude/commands/ruyi.md` | 更新手动触发提示，使其使用 v3 路由与索引协议 |
| `.ruyi/project-actions.md` | 检查并迁移对 `explain`、旧 INDEX 或旧审批路径的项目扩展引用 |

## 7. Upgrade v3 行为

### 7.1 完整迁移职责

`ruyi-upgrade` 必须处理：

1. 将无 `schema_version` 的 legacy v1 或低版本项目直接写入 `schema_version: 3`，同步所需配置与忽略规则。
2. 拆分并删除 `frontend-baseline.md`。
3. 合并二级 spec INDEX 到 `.ruyi/spec/INDEX.md` 后删除二级 INDEX。
4. 检测旧 spec 中误放的模块业务事实，将其迁入对应 baseline contract，仅在 spec 保留长期规则与结构事实。
5. 对 `contract / plan` 做不改变业务语义的结构规整。
6. 按当前 schema 重写 `test`，移除废弃字段和过程噪音。
7. 将旧 `explain` 的有效审批/验证相关信息迁入对应 `test`。
8. 将旧 `explain` 中真正属于长期知识缺口的内容迁入 `open-questions.md`。
9. 删除 `.ruyi/explain/` 及其他废弃目录。
10. 更新 `CLAUDE.md`、`.claude/settings.json`、`.claude/commands/ruyi.md` 及 `.ruyi/project-actions.md` 中由 Ruyi 管理的旧入口或旧流程引用。
11. 重建 `.ruyi/INDEX.md`，并校验 `.ruyi/spec/INDEX.md` 检索入口完整。
12. 提交并推送迁移后的正式 `.ruyi` 资产与必要入口配置，让团队统一使用当前版本。

### 7.2 需要用户判断时的处理

升级中可能遇到无法可靠自动推断的旧语义，例如旧审批结论需要选择新状态，或旧 baseline 段落无法确定归属。此时 agent 应在当前升级任务内向用户询问，得到答案后继续迁移，直到完成。

不得：

- 将项目标记为 v3 后遗留未迁移的正式资产。
- 把未决问题当作长期“升级阻塞状态”丢给后续流程。
- 为保守起见继续保留已确认废弃的正式文档或目录。

### 7.3 提交与推送边界

- 只提交正式共享资产及必要的项目入口配置。
- 不提交 `.ruyi/tasks/`、`.ruyi/spec-candidates/`、脚本验证 fixture 或本地缓存。
- 不覆盖与升级无关的业务代码改动。
- 如果目标分支受保护或推送失败，应明确报告分发阻塞；升级后的本地资产仍应保持完成且可提交状态。

## 8. 框架仓库实施范围

Ruyi 框架仓库后续实现应覆盖：

- `ruyi-init` 的 v3 新目录和索引模板。
- `ruyi-upgrade` 的完整资产迁移、校验和提交/推送引导能力。
- `using-ruyi` 的 v3 门禁及无 explain 路由。
- `ruyi-test` 与 `ruyi-approve` 的新交付审批模型。
- 删除或废弃 `ruyi-explain` 的发布入口。
- `ruyi-contract / plan / implement / spec-*` 的新 spec index 读取与维护规则。
- `README.md`、`docs/install.md`、所有相关 skill-local references 同步更新。

## 9. 验证要求

实现后至少验证：

- 新 init 不创建 `frontend-baseline.md`、`explain/` 或二级 spec INDEX。
- 新 init 创建两个正式 INDEX，且 baseline 包含可发现 references 的入口。
- 没有 `schema_version` 的 legacy v1 fixture 可以直接完整升级到 v3，不遗留 v2 结构或旧入口提示。
- 旧 v2 项目升级后不存在旧 baseline、二级 INDEX、`explain/` 和其他废弃目录。
- 旧 spec 中误放的模块业务事实迁移到 baseline contract，长期规则仍保留在 spec。
- 旧 `test / explain` 迁移后，审批与验证有效信息完整进入新 test；废弃内容消失。
- `CLAUDE.md`、Claude hook、`/ruyi` 命令与 `project-actions.md` 不再引用 explain 或旧 INDEX 规则。
- `using-ruyi` 仅通过根 INDEX 路由，并在低版本项目上先触发 upgrade。
- `ruyi-contract` 遇到实施设计话题时只吸收业务约束并提醒转入 plan；`ruyi-plan` 发现需求变化时返回 contract。
- implement/test 根据 `spec/INDEX.md` 强制加载匹配的 baseline、references 与 open questions。
- 根 INDEX 不发布本地 task/candidate，也不再引用 explain。
- 本地测试和 fixture 保持 ignored；发布提交仅包含正式 skill 与文档资产。
