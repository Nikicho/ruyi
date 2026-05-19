---
name: ruyi-spec-discover
description: Routed by using-ruyi. Use when an initialized Ruyi project needs to infer possible specs from existing code, component usage, module conventions, or repeated patterns. Creates or proposes local spec candidates only; never writes formal spec directly.
---

# Ruyi Spec Discover

## 1. 适用场景

- 成熟项目已经有大量代码，但没有对应 spec。
- 用户希望从现有代码反推组件、模块、API、状态、路由、测试等长期规则。
- 用户希望把重复出现的代码约定整理成本地 `spec-candidate`，再人工评审是否进入正式 spec。

## 2. 硬门禁

- 项目必须已经初始化 Ruyi。
- 必须由 `using-ruyi` 路由进入。
- 不能直接写入 `.ruyi/spec/`。
- 不能把大段源码搬进 candidate。
- 不能把一次性实现细节当成长期规范。
- `spec-candidates` 是本地临时层，默认不提交 git。

## 3. 执行原则

- 先读正式 spec，再读相关本地 candidates，避免重复推断。
- 只读取与目标模块、组件或问题相关的代码。
- 优先从多处重复模式、公共组件 API、模块边界、接口封装、错误处理、状态管理和测试约定中提炼。
- 发现冲突时，以正式 spec 为准，把冲突写入 candidate 的“待确认问题”。
- 同一功能或公共组件的候选应指向同一个目标目录，例如 `references/shared/table/columns.md`。

## 4. 执行步骤

1. 检查 `.ruyi/` 和 `.ruyirc` 是否存在。
2. 读取 `references/spec-schema.md` 和 `references/spec-candidate-schema.md`。
3. 读取 `.ruyi/spec/INDEX.md`、相关正式 spec 和相关 `.ruyi/spec-candidates/`。
4. 按用户指定范围读取代码；没有明确范围时，先让用户指定模块、组件或目录。
5. 提炼可复用规则，并标出证据路径。
6. 向用户展示候选摘要和目标 spec 路径。
7. 用户确认后，只写入 `.ruyi/spec-candidates/<target-layer>/<target-spec-path>`。

## 5. Candidate 要求

反推 candidate 必须包含：

- 来源：代码路径、组件名、模块名或测试路径。
- 目标 spec：顶层文件，或 `references/shared/` / `references/modules/` 下的文件。
- 沉淀建议：可长期复用的规则。
- 依据：简短列出观察到的代码证据。
- 适用范围：哪些模块、组件或场景适用。
- 不应沉淀内容：本次不要进入长期规范的实现细节。
- 待确认问题：需要用户或团队确认的点。

## 6. 输出要求

- 若用户只是要分析，输出候选建议，不落盘。
- 若用户确认写入，写入本地 `.ruyi/spec-candidates/`。
- 收口时说明候选仍需 `ruyi-spec-merge` 人工评审，正式 spec 不会自动变化。

## 7. 必读参考

- `references/spec-discover-discipline.md`
- `references/spec-schema.md`
- `references/spec-candidate-schema.md`
