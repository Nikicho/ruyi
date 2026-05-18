# Spec Schema

## 1. 对象定位

`spec` 记录项目长期规则与项目事实，不记录单次功能历史。

## 2. 项目层文件

项目层 `.ruyi/spec/` 首版固定包含：

- `project-overview.md`
- `project-structure.md`
- `frontend-baseline.md`
- `testing-baseline.md`
- `open-questions.md`
- `docs-registry.md`
- `interview-bank.md`
- `api/README.md`

项目层 `.ruyi/spec/api/` 用于长期 API 约定和外部权威源入口，不维护完整接口列表。建议包含：

- `api-source.md`：Swagger / Apifox / Yapi / OpenAPI 等权威源入口和访问方式。
- `response-envelope.md`：统一响应结构约定。
- `error-codes.md`：错误码约定。
- `auth-flow.md`：鉴权流程约定。
- `conventions.md`：命名、分页、排序等通用约定。

禁止把完整 Swagger JSON、完整接口字段表、临时 mock 数据放入 `spec/api/`。Ruyi 只引用 API 权威源，不重新维护后端 API 文档。

## 3. Confidence frontmatter

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

## 4. 章节规则

- 合并最小单位是章节。
- 合并键是 `文件名 + 标题路径`。
- 标题层级限制为 `#`、`##`、`###`。
- 标题应表达稳定主题，避免临时结论式命名。

## 5. 合并规则

支持：

- 继承
- 补充
- 收窄
- 替代

首版不支持显式删除。

## 6. 演进规则

- 项目事实和长期规则进入 `spec`。
- 一次性需求内容进入 `contract`。
- 执行安排进入 `task`。
- 交付结果进入 `explain`。
- 不确定但影响理解的问题进入 `open-questions.md`。
- 首版知识沉淀先生成 `spec-candidate`，不自动改写正式 `spec`。
