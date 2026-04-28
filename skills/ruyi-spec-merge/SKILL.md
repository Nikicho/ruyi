---
name: ruyi-spec-merge
description: Use when Ruyi spec candidates need periodic human review, merge previews, accepted/rejected decisions, or project spec updates outside the main feature delivery flow.
---

# Ruyi Spec Merge

## 1. 适用场景

- 用户要求查看可合入的规范候选。
- 用户要求把某个 spec-candidate 合入正式 spec。
- 用户要求拒绝或归档候选。

## 2. 硬门禁

- 项目必须已初始化。
- 只能处理 `.ruyi/spec-candidates/` 中的候选。
- 合入正式 spec 前必须展示 diff/预览并获得用户确认。
- 不自动写入 team 层。
- 不属于单次需求主流程。

## 3. 执行步骤

1. 读取 `../../references/spec-merge-protocol.md`。
2. 使用 `merge_list.py` 列出 pending candidates。
3. 使用 `merge_diff.py` 预览候选会如何影响目标 spec。
4. 用户确认后，使用 `merge_apply.py` 合入或拒绝。
5. 合入后候选进入 `.ruyi/spec-archive/merged/`；拒绝后进入 `.ruyi/spec-archive/rejected/`。

## 4. 脚本调用

```bash
python skills/ruyi-spec-merge/scripts/merge_list.py --project <project>
python skills/ruyi-spec-merge/scripts/merge_diff.py --project <project> --candidate <path>
python skills/ruyi-spec-merge/scripts/merge_apply.py --project <project> --candidate <path> --decision <merged|rejected> --reason <reason>
```

脚本只处理 Markdown 协议文件，不判断业务正确性。

## 5. 必读参考

- `../../references/spec-candidate-schema.md`
- `../../references/spec-merge-protocol.md`
- `../ruyi-spec-evolve/references/spec-evolution-discipline.md`
