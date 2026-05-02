---
name: ruyi-spec-merge
description: Use when Ruyi spec candidates need periodic human review, merge previews, accepted/rejected decisions, or manual spec patch generation outside the main feature delivery flow.
---

# Ruyi Spec Merge

## 1. 适用场景

- 用户要求查看可合入的规范候选。
- 用户要求评审某个 `spec-candidate` 是否应该进入正式 spec。
- 用户要求拒绝、取代或归档候选。

## 2. 硬门禁

- 项目必须已初始化。
- 只能处理 `.ruyi/spec-candidates/` 中的候选。
- 合入前必须展示预览，并获得用户确认。
- `merged` 不直接写正式 spec，只生成 `.ruyi/spec-patches/` 下的人工合入 patch。
- 不自动写入 team 层。
- 该 skill 不属于单次需求主流程。

## 3. 执行步骤

1. 读取 `references/spec-merge-protocol.md`。
2. 使用 `merge_list.py` 列出 pending candidates。
3. 使用 `merge_diff.py` 预览 candidate 对目标 spec 的影响。
4. 用户确认后，使用 `merge_apply.py` 标记为 `merged`、`rejected` 或 `superseded`。
5. `merged` 会生成 patch 并归档到 `.ruyi/spec-archive/merged/`；`rejected` 归档到 `.ruyi/spec-archive/rejected/`；`superseded` 归档到 `.ruyi/spec-archive/superseded/`。
6. 用户或维护者后续手动打开 patch，把真正可长期复用的内容合入正式 spec。

## 4. 脚本调用

```bash
python <skills-dir>/ruyi-spec-merge/scripts/merge_list.py --project <project>
python <skills-dir>/ruyi-spec-merge/scripts/merge_diff.py --project <project> --candidate <path>
python <skills-dir>/ruyi-spec-merge/scripts/merge_apply.py --project <project> --candidate <path> --decision <merged|rejected|superseded> --reason <reason>
```

脚本只处理 Markdown 协议文件，不判断业务正确性。

## 5. 必读参考

- `references/spec-candidate-schema.md`
- `references/spec-merge-protocol.md`
- `references/spec-evolution-discipline.md`
- `references/merge-discipline.md`
