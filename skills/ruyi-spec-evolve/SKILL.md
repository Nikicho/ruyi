---
name: ruyi-spec-evolve
description: Routed by using-ruyi. Use only after using-ruyi has determined the next stage is knowledge distillation after an approved delivery or code observation.
---

# Ruyi Spec Evolve

## 1. 适用场景

- 某次开发后发现可复用规则。
- approved test 后需要沉淀项目经验。
- 代码反推后需要生成待审 spec candidate。
- 需要评估是否形成 team 层候选规范。

## 2. 硬门禁

- 项目必须已初始化。
- 没有 approved test 或明确 code observation，不进入正式沉淀。
- 不允许把 `contract / task / test / project-actions` 原样转成 spec。
- 不自动回写 team 层。

## 3. 执行原则

- 沉淀是提炼，不是搬运。
- 默认先落项目层。
- team 层升级更谨慎。
- 只更新相关章节，不大面积改写 spec。
- 允许保留少量高价值技术碎片，但要精，不要多。
- 正式 spec 只有一份当前真相；用户当场确认的项目规则直接写入对应正式 spec。
- spec-candidate 只用于用户延后审视或批量代码反推场景，是本地临时层，默认不提交 git。
- candidate 路径跟随目标 spec 路径，不按日期生成版本目录。

## 4. 执行步骤

1. 检查项目是否已初始化。
2. 读取 approved test 或 code observation。
3. 读取 `.ruyi/spec/INDEX.md` 和相关正式 spec。
4. 读取 `references/spec-evolution-discipline.md`。
5. 判断是否有可复用、已验证内容。
6. 项目特有经验向用户展示目标 spec 与修改摘要；用户当场确认后直接更新 `.ruyi/spec/`。
7. 仅在用户明确延后审视时，生成 `.ruyi/spec-candidates/` 候选。
8. 团队共性经验生成 team 层候选说明，不自动回写 team 层。
9. 不确定内容写入候选的“待确认问题”，必要时后续再进入 `.ruyi/spec/open-questions.md`。

## 5. 产物要求

- 用户当场确认：更新 `.ruyi/spec/<target-spec-path>`。
- 用户延后审视：生成 `.ruyi/spec-candidates/<target-layer>/<target-spec-path>`。
- 候选可以指向项目层 spec，也可以作为 team 层候选。
- candidate 只作为待确认信号；冲突时正式 spec 胜出。

## 6. 脚本调用

确认 test 已审批通过、确实有可复用内容且用户选择延后审视后，可以使用脚本生成候选：

```bash
python <skills-dir>/ruyi-spec-evolve/scripts/candidate_create.py --project <project> --module <module> --feature <feature> --date <YYYY-MM-DD> --title <title> --target-layer <project|team> --target-spec <spec-file-or-reference-path> --proposal <item> --evidence <item> --scope <item>
```

脚本职责：

- 校验项目已初始化。
- 校验 test 存在且 `result` 为 `passed` 或 `passed-with-notes`。
- 校验 test 的 `approval: approved`。
- 写入 `.ruyi/spec-candidates/<target-layer>/<target-spec-path>`。
- 按需懒创建本地 candidate 目录。
- 不覆盖已有本地候选。
- 不使用日期做 candidate 版本路径。
- 不改写正式 spec。

## 7. 必读参考

- `references/main-flow.md`
- `references/knowledge-evolution.md`
- `references/spec-schema.md`
- `references/spec-candidate-schema.md`
- `references/spec-evolution-discipline.md`
