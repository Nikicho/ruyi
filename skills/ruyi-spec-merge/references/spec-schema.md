# Spec Schema

## 1. 对象定位

`spec` 记录项目长期规则、跨模块约束、项目结构事实和索引，不记录单次功能历史，也不按日期区分版本。

成熟项目完整迁移蒸馏出的模块业务事实不进入正式 spec，应按模块进入 baseline contract。

正式 spec 只有一份当前真相：对的就是对的，应该被持续遵守；历史变化交给 git 记录。

## 2. 唯一入口

`.ruyi/spec/INDEX.md` 是唯一正式 spec 检索入口，必须提交 git。

agent 需要读取项目规范时，必须先读 `.ruyi/spec/INDEX.md`，再按 INDEX 链接按需读取顶层 baseline、`references/shared/` 或 `references/modules/` 下的细分规范。

只要请求可能修改源码，就必须先执行渐进式 spec 加载。这个规则不只属于 implement 阶段，也适用于 bugfix、重构、微重构、格式调整、文件架构调整、lint 修复等任何源码改动。

禁止把 `references/shared/INDEX.md` 或 `references/modules/INDEX.md` 作为二级索引；schema v3 不创建、不维护这些文件。

## 3. 项目层文件

项目层 `.ruyi/spec/` 首版固定包含：

- `INDEX.md`
- `project-overview.md`
- `project-structure.md`
- `development-baseline.md`
- `coding-baseline.md`
- `testing-baseline.md`
- `api.md`
- `open-questions.md`
- `docs-registry.md`（完整迁移且确认有可复用外部入口时生成）
- `interview-bank.md`（完整迁移且完成澄清时生成）

顶层文件只放项目级核心规则、概述和索引。详细规则放入 `references/`，并从 `.ruyi/spec/INDEX.md` 或顶层 baseline 链接过去。

## 4. References 组织

`references/` 只有两类目录：

- `references/shared/`：跨模块共享规范，例如 `api/`、`components/`、`routing/`、`errors/`。
- `references/modules/`：具体模块、页面、业务功能或公共组件的规范。

同一功能、同一公共组件、同一领域对象必须放在同一个文件夹下，再按主题拆分文件。

示例：

```text
references/shared/table/
  simple-usage.md
  usage.md
  columns.md
  internals.md
```

禁止为同一功能按日期、交付批次或临时讨论拆出多个平级目录。

## 5. Baseline 拆分

- `development-baseline.md`：开发过程约束，例如必须运行 `lint`、构建、单测、UI 自动化验证、提交前检查。
- `coding-baseline.md`：代码编写约束，例如组件边界、状态管理、样式约定、错误处理、数据访问方式。
- `testing-baseline.md`：测试策略、验收证据和失败回流规则。

顶层 baseline 只保留最通用规则和索引摘要；模块级、组件级、接口级细则必须链接到 `references/shared/` 或 `references/modules/` 的具体文件。开发过程中不能只读 baseline 而忽略其链接的 references。

## 5.1 渐进式加载规则

代码改动前按写入边界加载，不全量读取：

1. 先读 `.ruyi/spec/INDEX.md`。
2. 总是读取 `development-baseline.md` 和 `coding-baseline.md` 的核心约束；涉及测试、验证、bugfix 时读取 `testing-baseline.md`。
3. 根据 contract、plan、维护目标和写入边界读取相关 `references/modules/`。
4. 涉及公共组件、组件 props/slots/events、组件封装、组件使用、Table、Form、Modal、Drawer、Button、Select 等 UI 基础能力时，读取相关 `references/shared/` 组件 spec。
5. 涉及 API、权限、路由、错误处理、状态管理等跨模块能力时，读取相关 `references/shared/<主题>/`。
6. 读取目标相关 `.ruyi/spec-candidates/`，只作为待确认补充信号，不能覆盖正式 spec。
7. 如果 INDEX 没有直接列出相关 shared spec，但写入边界显示会碰公共组件或共享能力，先列对应 `references/shared/` 子目录，再读取最相关文件。

禁止：

- 一次性读取整个 `.ruyi/spec/`。
- 只读 baseline 就改公共组件。
- 只读模块 spec，不读被使用的 shared component spec。
- 因为不是 implement 阶段就跳过 spec。

## 6. API 归位

`api.md` 只维护长期 API 对接原则和权威源入口，不维护完整接口列表。

详细 API 约定建议放入：

- `references/shared/api/source.md`
- `references/shared/api/response-envelope.md`
- `references/shared/api/error-codes.md`
- `references/shared/api/auth-flow.md`
- `references/shared/api/conventions.md`

禁止把完整 Swagger JSON、完整接口字段表、临时 mock 数据放入 `.ruyi/spec/`。Ruyi 只引用 API 权威源，不重新维护后端 API 文档。

## 7. Spec Candidates 读取规则

`.ruyi/spec-candidates/` 是本地临时候选层，默认应被 git 忽略。

agent 在需要读取正式 spec 时，应同时按需读取相关 `.ruyi/spec-candidates/`：

1. 先读取正式 `.ruyi/spec/INDEX.md`。
2. 按 INDEX 读取相关正式 spec。
3. 再读取目标相关的 `.ruyi/spec-candidates/`。
4. candidate 只能作为“待确认的补充信号”，不能覆盖正式 spec。
5. candidate 与正式 spec 冲突时，正式 spec 胜出，并提示 candidate 需要评审或废弃。

只有经过人工评审并手动合入后的内容，才进入正式 `.ruyi/spec/` 并提交给团队。

## 8. Confidence frontmatter

所有 spec 文件必须带 confidence frontmatter：

```yaml
---
confidence: observed | distilled | claimed | open | confirmed_by_user
source: <来源描述>
verified_at: <YYYY-MM-DD>
needs_review: true | false
---
```

| confidence | 含义 | 引用规则 |
| --- | --- | --- |
| `observed` | 从代码 / 配置 / 文件结构观察到的硬事实 | 可直接引用 |
| `confirmed_by_user` | 用户在澄清问卷或对话中明确确认 | 可直接引用 |
| `distilled` | 从外部文档蒸馏出的关键事实 | 引用前提示用户复核 |
| `claimed` | 文档声称但未验证 | contract 阶段二次确认 |
| `open` | 知识缺口 | 不能作为事实引用，遇到必须问用户 |

## 9. 章节规则

- 合并最小单位是章节。
- 合并键是 `文件路径 + 标题路径`。
- 标题层级限制为 `#`、`##`、`###`。
- 标题应表达稳定主题，避免临时结论式命名。

## 10. 演进规则

- 项目结构事实、长期规则和跨模块约束进入 `spec`。
- 模块业务事实进入 baseline contract。
- 一次性需求内容进入 `contract`。
- 跨轮次执行恢复点进入本地 `task`，不作为团队规范依据。
- 交付结果、验证证据和审批状态进入 `test`。
- 不确定但影响理解的问题进入 `open-questions.md`。
- 用户确认的项目层长期规则直接更新当前正式 `spec`；只有延后审视或代码反推待审内容进入本地 `spec-candidate`。
