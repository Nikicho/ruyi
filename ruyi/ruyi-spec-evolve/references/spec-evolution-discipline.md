# Spec Evolution Discipline

## 1. 目标

spec-evolve 阶段负责把一次开发中已经被验证的、可复用的经验提炼为项目规范或团队规范候选。

它不是备份开发过程，也不是把 contract/explain 原文搬进 spec。

本纪律内化自 Superpowers 的 `finishing-a-development-branch`、`writing-skills` 和 `verification-before-completion`：

- 吸收 `finishing-a-development-branch` 的收口判断，只沉淀值得复用的稳定经验。
- 吸收 `writing-skills` 的表达纪律，候选规范应短、准、可复用，避免长篇过程叙述。
- 吸收 `verification-before-completion` 的证据要求，候选规范必须说明证据来源。

## 2. 硬门禁

- 没有结果依据，不进入知识沉淀。
- 没有 explain 或等价交付说明，不进入正式沉淀。
- 未审批通过时，不自动沉淀正式规范。
- explain 缺少 contract、plan 或 test 锚点时，不生成候选。
- 没有证据来源或适用范围时，不生成候选。
- 不允许把 `contract / task / explain / project-actions / workspace` 原样转成 spec。
- 首版不自动回写 team 层。
- 没有复用价值的内容，不沉淀。

## 3. 最小流程

1. 读取 explain 和审批结论。
2. 判断是否有可沉淀内容。
3. 区分项目特有经验和团队共性经验。
4. 项目特有经验生成 `.ruyi/spec-candidates/` 候选。
5. 团队共性经验只形成 team 候选说明。
6. 无法确认的内容进入候选的“待确认问题”。
7. 不自动改写正式 spec。

## 4. 可沉淀内容

允许沉淀：

- 已验证的实现边界。
- 稳定的项目结构事实。
- 可复用的测试基线。
- 可复用的前端数据访问约定。
- 对后续开发有明确指导价值的技术债或架构演进建议。

禁止沉淀：

- 一次性需求内容。
- 临时调试流水账。
- 未验证猜测。
- 审批意见原文。
- 纯粹过程记录。

## 5. 反模式

| 反模式 | 正确处理 |
| --- | --- |
| 每次开发都更新 spec | 先生成候选，只有可复用、已验证内容才考虑合入 |
| 把 explain 复制进 spec | 提炼规则，不搬运过程 |
| 发现团队共性就直接写 team | 首版只形成候选说明 |
| 技术碎片越多越好 | 精简，只保留高价值内容 |
| 没把不确定内容标出来 | 写入 open-questions |

## 6. 检查清单

沉淀前检查：

- 是否有 explain 或等价依据？
- 是否已通过审批或形成稳定结论？
- 内容是否可复用？
- 内容是否已验证？
- 应落项目层还是团队候选？
- 是否只生成候选而非直接改写正式 spec？
