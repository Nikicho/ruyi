# Script Runtime Protocol

## 1. 入口

Python 可用时，使用 `scripts/upgrade_project.py` 执行确定性迁移并输出 JSON 结果。

## 2. 回退

脚本不可用时，agent 只能按 `upgrade-discipline.md` 人工执行机械更新，并逐项报告改动；不得因此扩大到业务语义改写。

## 3. 删除规则

任何废弃目录删除都要求用户明确确认，不得将升级命令本身视为删除授权。
