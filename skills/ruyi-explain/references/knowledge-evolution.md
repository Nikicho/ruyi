# Knowledge Evolution

## 1. 定位

知识沉淀只处理可复用、长期有效、已经验证或明确待审的规则，不搬运过程文档。

## 2. 来源

默认在 approved test 后考虑沉淀。另一个来源是 `ruyi-spec-discover` 从现有代码反推出的 code observation。

可作为来源：

- approved test 中的验证结论、风险和审批信息。
- contract 中已经确认的业务边界。
- plan 中可复用的实施约束。
- 代码反推得到的稳定模式。

不能整体升级为 spec：

- contract 原文。
- test 原文。
- task checkpoint。
- project-actions。

## 3. 输出

- 用户当场确认的项目长期规则：直接更新 `.ruyi/spec/`。
- 用户延后审视：写入本地 `.ruyi/spec-candidates/`。
- 团队层候选：只生成候选说明，不自动写入 team 层。

## 4. open questions

不能确认但影响后续理解的问题，进入 `.ruyi/spec/open-questions.md` 或 candidate 的“待确认问题”。
