# Main Flow

## 1. 标准主流程

```text
using-ruyi -> init/upgrade -> contract -> plan -> implement -> test -> approve -> complete
```

阶段含义：

- 入口：`using-ruyi`
- 初始化或升级：`ruyi-init` / `ruyi-upgrade`
- 需求定义：`ruyi-contract`
- 实施计划：`ruyi-plan`
- 编码实现：`ruyi-implement`
- 验证与证据：`ruyi-test`
- 审批：`ruyi-approve`，直接更新 test 的 `approval`
- 知识沉淀：approved test 后按需进入 `ruyi-spec-evolve`

## 2. Tiny 流程

```text
using-ruyi -> contract -> implement -> test -> complete
```

`tiny` 不是绕过 Ruyi。tiny 只是省略 plan 和 approve，仍必须有已确认 contract 和 test 证据。如改动范围扩大，必须升级为 `standard` 并补 plan。

## 3. 轻量维护模式

用于代码优化、代码微重构等无行为变化维护：

- 不生成 contract / plan / task。
- 不生成 explain。
- 不生成 spec-candidate，除非用户明确要求延后审视。
- 必须确认不改变用户可感知行为、业务规则、接口语义、状态语义、权限、路由或验收标准。
- 如发现行为变化，返回 `ruyi-contract`。

## 4. 本地恢复点

长 plan 的本地执行恢复点保存在 `.ruyi/tasks/`，只使用 `pending / in-progress / done`，不提交 git，也不作为正式 test 或 approve 门禁。

## 5. 返工类型

| 类型 | 场景 | 处理 |
| --- | --- | --- |
| A | 非语义修订 | 原地修订当前 contract，追加修订记录 |
| B | 中途变更影响计划 | 原地修订当前 contract，返回 plan 重评 |
| C | 新语义需求 | 新建日期 contract，旧 contract 标记 `superseded_by` |
| D | 审批后返工 | 重开同一 contract，记录返工原因；按返回阶段重置当前 plan/test 状态 |

类型 D 不新增 contract，也不追加一份并行 contract。当前文件状态唯一；重新进入流程时，contract / plan / test 的状态也必须回退。

## 6. 索引入口

- Ritual 阶段只读 `.ruyi/INDEX.md`。
- 需要项目规范时，先读 `.ruyi/spec/INDEX.md`，再按索引读取相关 spec 和 references。
- 路由确定到具体 feature 前，不读取多个 contract / plan / test 正文。
