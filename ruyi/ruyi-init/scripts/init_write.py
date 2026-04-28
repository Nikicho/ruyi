"""Write the initial .ruyi and .ruyirc structure for a supported project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from common import (
    REQUIRED_RUYI_DIRS,
    append_gitignore_rules,
    ensure_dir,
    write_if_missing,
)


RUYIRC_CONTENT = """layers:
  - name: team
    path: .ruyi-team
    optional: true

  - name: project
    path: .ruyi
    optional: false
"""


def project_readme() -> str:
    return """# Ruyi Project Layer

该目录保存当前项目的 Ruyi 协议层文档。

## 启用规则

当前项目已启用 Ruyi。

当项目根目录存在 `.ruyi/` 或 `.ruyirc` 时，agent 应优先使用 Ruyi 作为开发协作主流程。

除非用户明确要求不用 Ruyi，否则新功能、修复、重构、测试验证、开发简报、审批和知识沉淀都应进入 Ruyi 对应阶段。

- `spec/`：项目长期有效的事实和规范。
- `contracts/`：每次需求的设计与验收定义。
- `plans/`：由 contract 转化出的开发计划、测试策略和 task 拆分。
- `tasks/`：由 plan 拆分出的开发任务。
- `tests/`：每次 contract 对应的正式验证结果。
- `explain/`：面向 PM 的开发简报。
- `spec-candidates/`：审批通过后的知识沉淀候选，不自动改写正式 spec。
- `workspace/`：临时过程材料，不提交正式内容。
"""


def workspace_readme() -> str:
    return """# Ruyi Workspace

该目录用于临时分析、草稿和过程材料。

除本 README 外，`workspace/` 默认不应提交到 git。
"""


def project_actions() -> str:
    return """# Project Actions

当前项目暂无自定义动作。

项目动作只能挂接在 Ruyi 固定主流程阶段前后，不能替代主流程阶段产物。
"""


def project_index() -> str:
    return """# Ruyi Index

> 自动生成，请勿手工编辑。
"""


def spec_contents(facts: dict[str, Any]) -> dict[str, str]:
    modules = facts.get("module_candidates") or []
    tests = facts.get("test_signals") or []
    questions = facts.get("open_questions") or []

    return {
        "project-overview.md": f"""# 项目概览

## 技术栈

- 前端框架：{facts.get("framework") or "待确认"}
- 构建工具：{facts.get("bundler") or "待确认"}
- 主要语言：{facts.get("language") or "待确认"}

## 业务概览

待补充。
""",
        "project-structure.md": f"""# 项目结构

## 初步模块候选

{format_list(modules) if modules else "待确认。"}
""",
        "frontend-baseline.md": """# 前端基线

## 框架约定

待补充。

## 数据访问方式

待补充。
""",
        "testing-baseline.md": f"""# 测试基线

## 已识别测试信号

{format_list(tests) if tests else "待确认。"}
""",
        "open-questions.md": f"""# 待确认问题

{format_list(questions) if questions else "暂无。"}
""",
    }


def format_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def create_dir(project: Path, relative: str, created: list[str], skipped: list[str]) -> None:
    if ensure_dir(project / relative):
        created.append(relative)
    else:
        skipped.append(relative)


def create_file(project: Path, relative: str, content: str, created: list[str], skipped: list[str]) -> None:
    if write_if_missing(project / relative, content):
        created.append(relative)
    else:
        skipped.append(relative)


def write_init(project_path: str | Path, facts: dict[str, Any]) -> dict[str, Any]:
    project = Path(project_path)
    created: list[str] = []
    skipped: list[str] = []
    updated: list[str] = []
    notes: list[str] = []

    for directory in REQUIRED_RUYI_DIRS:
        create_dir(project, directory, created, skipped)

    create_file(project, ".ruyirc", RUYIRC_CONTENT, created, skipped)
    create_file(project, ".ruyi/README.md", project_readme(), created, skipped)
    create_file(project, ".ruyi/INDEX.md", project_index(), created, skipped)
    create_file(project, ".ruyi/project-actions.md", project_actions(), created, skipped)
    create_file(project, ".ruyi/workspace/README.md", workspace_readme(), created, skipped)

    for filename, content in spec_contents(facts).items():
        create_file(project, f".ruyi/spec/{filename}", content, created, skipped)

    if append_gitignore_rules(project / ".gitignore"):
        updated.append(".gitignore")
    else:
        skipped.append(".gitignore")

    if facts.get("open_questions"):
        notes.extend(facts["open_questions"])

    return {
        "created": created,
        "skipped": skipped,
        "updated": updated,
        "notes": notes,
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Write Ruyi initialization files.")
    parser.add_argument("--project", required=True, help="Project root path")
    parser.add_argument("--facts", required=True, help="JSON facts file from init_read.py")
    args = parser.parse_args(argv)

    facts = json.loads(Path(args.facts).read_text(encoding="utf-8-sig"))
    output = json.dumps(write_init(args.project, facts), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
