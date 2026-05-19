# Spec Schema

## 1. 对象定位

`spec` 记录项目长期规则与项目事实，不记录单次功能历史，也不按日期区分版本。

正式 spec 只有一份当前真相：对的就是对的，应该被持续遵守；历史变化交给 git 记录。

## 2. 项目层文件

项目层 `.ruyi/spec/` 首版固定包含：

- `INDEX.md`
- `project-overview.md`
- `project-structure.md`
- `development-baseline.md`
- `coding-baseline.md`
- `testing-baseline.md`
- `api.md`
- `open-questions.md`
- `docs-registry.md`（完整迁移时生成）
- `interview-bank.md`（完整迁移时生成）
- `references/shared/INDEX.md`
- `references/modules/INDEX.md`

顶层文件只放项目级核心规则、概述和索引。详细规则放入 `references/`。

## 3. References 组织

`references/` 只有两类入口：

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

## 4. Baseline 拆分

- `development-baseline.md`：开发过程约束，例如必须运行 `lint`、构建、单测、UI 自动化验证、提交前检查。
- `coding-baseline.md`：代码编写约束，例如组件边界、状态管理、样式约定、错误处理、数据访问方式。
- `testing-baseline.md`：测试策略、验收证据和失败回流规则。

顶层 baseline 可以保留最通用规则，并通过链接索引到 `references/shared/` 或 `references/modules/` 的细分规则。

## 5. API 归位

`api.md` 只维护长期 API 对接原则和权威源入口，不维护完整接口列表。

详细 API 约定建议放入：

- `references/shared/api/source.md`
- `references/shared/api/response-envelope.md`
- `references/shared/api/error-codes.md`
- `references/shared/api/auth-flow.md`
- `references/shared/api/conventions.md`

禁止把完整 Swagger JSON、完整接口字段表、临时 mock 数据放入 `.ruyi/spec/`。Ruyi 只引用 API 权威源，不重新维护后端 API 文档。

## 6. Spec Candidates 读取规则

`.ruyi/spec-candidates/` 是本地临时候选层，默认应被 git 忽略。

agent 在需要读取正式 spec 时，应同时按需读取相关 `.ruyi/spec-candidates/`：

1. 先读取正式 `.ruyi/spec/`。
2. 再读取目标相关的 `.ruyi/spec-candidates/`。
3. candidate 只能作为“待确认的补充信号”，不能覆盖正式 spec。
4. candidate 与正式 spec 冲突时，正式 spec 胜出，并提示 candidate 需要评审或废弃。

只有经过人工评审并手动合入后的内容，才进入正式 `.ruyi/spec/` 并提交给团队。

## 7. Confidence frontmatter

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

## 8. 章节规则

- 合并最小单位是章节。
- 合并键是 `文件路径 + 标题路径`。
- 标题层级限制为 `#`、`##`、`###`。
- 标题应表达稳定主题，避免临时结论式命名。

## 9. 演进规则

- 项目事实和长期规则进入 `spec`。
- 一次性需求内容进入 `contract`。
- 执行安排进入 `task`。
- 交付结果进入 `explain`。
- 不确定但影响理解的问题进入 `open-questions.md`。
- 首版知识沉淀先生成本地 `spec-candidate`，不自动改写正式 `spec`。
