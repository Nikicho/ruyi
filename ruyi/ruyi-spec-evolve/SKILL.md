---
name: ruyi-spec-evolve
description: Use when completed Ruyi work should be distilled into project spec updates, team spec candidates, open questions, or frontend development knowledge.
---

# Ruyi Spec Evolve

## 1. 适用场景

- 某次开发后发现可复用规则。
- 某次 explain 后需要沉淀项目经验。
- 需要评估是否形成 team 层候选规范。

## 2. 硬门禁

- 项目必须已初始化。
- 没有结果依据，不进入知识沉淀。
- 没有 explain 或等价结果依据，不进入正式沉淀。
- 不允许把 `contract / task / explain / project-actions / workspace` 原样转成 spec。
- 首版不自动回写 team 层。

## 3. 执行原则

- 沉淀是提炼，不是搬运。
- 默认先落项目层。
- team 层升级更谨慎。
- 只更新相关章节，不大面积改写 spec。
- 允许保留少量高价值技术碎片，但要精，不要多。

## 4. 执行步骤

1. 检查项目是否已初始化。
2. 读取 explain 或等价结果依据。
3. 读取审批结论。
4. 读取 `references/spec-evolution-discipline.md`。
5. 判断是否有可复用、已验证内容。
6. 项目特有经验生成 `.ruyi/spec-candidates/` 候选。
7. 团队共性经验生成 team 层候选说明，不自动回写 team 层。
8. 不确定内容写入候选的“待确认问题”，必要时后续再进入 `.ruyi/spec/open-questions.md`。

## 5. 产物要求

- 生成 `.ruyi/spec-candidates/<module>/<feature>/<contract-date>.md`。
- 候选可以指向项目层 spec，也可以作为 team 层候选。
- 不自动改写 `.ruyi/spec/*.md`。

## 6. 脚本调用

确认 explain 已审批通过，并且确实有可复用内容后，可以使用脚本生成候选：

```bash
python <skills-dir>/ruyi-spec-evolve/scripts/candidate_create.py --project <project> --module <module> --feature <feature> --date <YYYY-MM-DD> --title <title> --target-layer <project|team> --target-spec <spec-file> --proposal <item> --evidence <item> --scope <item>
```

脚本职责：

- 校验项目已初始化。
- 校验 explain 存在且 `approval: approved`。
- 写入 `.ruyi/spec-candidates/<module>/<feature>/<contract-date>.md`。
- 不覆盖已有候选。
- 不改写正式 spec。

## 7. 必读参考

- `../references/main-flow.md`
- `../references/knowledge-evolution.md`
- `../references/spec-schema.md`
- `../references/spec-candidate-schema.md`
- `references/spec-evolution-discipline.md`
