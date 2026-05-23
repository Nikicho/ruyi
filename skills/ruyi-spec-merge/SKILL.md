---
name: ruyi-spec-merge
description: Use when local Ruyi spec candidates need human review, adoption into formal spec, or deletion outside the main feature delivery flow.
---

# Ruyi Spec Merge

## 1. 适用场景

- 用户要求查看可合入的规范候选。
- 用户要求评审某个 `spec-candidate` 是否应该进入正式 spec。
- 用户要求拒绝或删除候选。

## 2. 硬门禁

- 项目必须已初始化。
- 只能处理 `.ruyi/spec-candidates/` 中的候选。
- 合入前必须展示预览，并获得用户确认。
- 用户接受项目层候选时，先更新对应正式 spec，再将 candidate 标记为已处理并删除。
- 不自动写入 team 层。
- 该 skill 不属于单次需求主流程。
- `.ruyi/spec-candidates/` 是本地临时层，默认不提交 git；处理完成后删除，不保留本地归档。

## 3. 执行步骤

1. 读取 `references/spec-merge-protocol.md`。
2. 使用 `merge_list.py` 列出 pending candidates。
3. 使用 `merge_diff.py` 预览 candidate 对目标 spec 的影响。
4. 用户接受项目层候选时，直接编辑当前唯一正式 spec，写入确认后的规则。
5. 使用 `merge_apply.py` 记录处理动作并删除 candidate；拒绝或已被替代的候选也直接删除。

## 4. 脚本调用

```bash
python <skills-dir>/ruyi-spec-merge/scripts/merge_list.py --project <project>
python <skills-dir>/ruyi-spec-merge/scripts/merge_diff.py --project <project> --candidate <path>
python <skills-dir>/ruyi-spec-merge/scripts/merge_apply.py --project <project> --candidate <path> --decision <merged|rejected|superseded> --reason <reason>
```

脚本不判断业务正确性；`decision: merged` 对项目层候选要求对应正式 spec 已存在，避免未合入正式规则便删除候选。

## 5. 必读参考

- `references/spec-candidate-schema.md`
- `references/spec-merge-protocol.md`
- `references/spec-evolution-discipline.md`
- `references/merge-discipline.md`
