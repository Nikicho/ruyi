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
- `api/README.md`

项目层 `.ruyi/spec/api/` 用于长期 API 约定和外部权威源入口，不维护完整接口列表。建议包含：

- `api-source.md`：Swagger / Apifox / Yapi / OpenAPI 等权威源入口和访问方式。
- `response-envelope.md`：统一响应结构约定。
- `error-codes.md`：错误码约定。
- `auth-flow.md`：鉴权流程约定。
- `conventions.md`：命名、分页、排序等通用约定。

禁止把完整 Swagger JSON、完整接口字段表、临时 mock 数据放入 `spec/api/`。Ruyi 只引用 API 权威源，不重新维护后端 API 文档。

## 3. 章节规则

- 合并最小单位是章节。
- 合并键是 `文件名 + 标题路径`。
- 标题层级限制为 `#`、`##`、`###`。
- 标题应表达稳定主题，避免临时结论式命名。

## 4. 合并规则

支持：

- 继承
- 补充
- 收窄
- 替代

首版不支持显式删除。

## 5. 演进规则

- 项目事实和长期规则进入 `spec`。
- 一次性需求内容进入 `contract`。
- 执行安排进入 `task`。
- 交付结果进入 `explain`。
- 不确定但影响理解的问题进入 `open-questions.md`。
- 首版知识沉淀先生成 `spec-candidate`，不自动改写正式 `spec`。
