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

## 模块：待补充

### 待补充

- 业务目标：待补充
- 类型：待补充
- 状态：待补充
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
        "api/README.md": """# API 相关 Spec

本目录维护项目层长期 API 约定。**不维护完整接口列表**，权威源是后端。

建议添加：

- `api-source.md`：外部权威 API 文档入口。
- `response-envelope.md`：统一响应结构。
- `error-codes.md`：错误码约定。
- `auth-flow.md`：鉴权流程。
- `conventions.md`：命名 / 分页 / 排序通用约定。

Ruyi 只引用 API 权威源，不拷贝完整 Swagger / OpenAPI / Apifox 字段表。
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


def claude_activation_block() -> str:
    return """## Ruyi 主流程激活

本项目使用 Ruyi 作为开发协作框架。

任何代码改动、bug 修复、新增功能、测试、审批、知识沉淀的请求，必须先加载 `using-ruyi` skill 走 Ritual：

1. 检查 `.ruyi/` 状态。
2. 仅读取 `.ruyi/INDEX.md`，不读 contract / plan / explain 正文。
3. 路由到对应子 skill 后，才读取该 feature 的具体产物。

不允许跳过 `using-ruyi` 直接编辑代码或执行 shell 命令。
不允许在路由确定前读取多个 feature 的 contract 正文。
"""


def append_claude_md(project: Path, created: list[str], skipped: list[str], updated: list[str]) -> None:
    target = project / "CLAUDE.md"
    block = claude_activation_block().strip() + "\n"
    if not target.exists():
        target.write_text(block, encoding="utf-8")
        created.append("CLAUDE.md")
        return

    existing = target.read_text(encoding="utf-8")
    if "## Ruyi 主流程激活" in existing:
        skipped.append("CLAUDE.md")
        return

    prefix = existing
    if prefix and not prefix.endswith("\n"):
        prefix += "\n"
    if prefix and not prefix.endswith("\n\n"):
        prefix += "\n"
    target.write_text(prefix + block, encoding="utf-8")
    updated.append("CLAUDE.md")


def slash_command() -> str:
    return """---
description: Manually load the Ruyi pipeline router (using-ruyi)
---

Load the using-ruyi skill and execute its Ritual:

1. Detect `.ruyi/` state.
2. Read `.ruyi/INDEX.md` only. Do NOT read contract / plan / explain bodies.
3. List up to 5 active feature candidates from INDEX.
4. Route my next message to the correct sub-skill.
5. Only after routing to a specific feature, read that feature's latest contract.

Do not edit code, run shell commands, or generate stage artifacts before completing the Ritual.
"""


def ruyi_hook_command() -> str:
    reminder = (
        "<system-reminder>This project uses Ruyi. You MUST load the using-ruyi skill "
        "and execute its Ritual before any code edit, file write, shell command, or stage execution. "
        "Read .ruyi/INDEX.md only before routing; do not scan contract / plan / explain bodies. "
        "Failure to do so violates the Ruyi main flow.</system-reminder>"
    )
    return f"sh -c \"[ -d .ruyi ] || [ -f .ruyirc ]\" && echo '{reminder}' || true"


def merge_claude_settings(project: Path, skipped: list[str], updated: list[str], notes: list[str]) -> None:
    target = project / ".claude" / "settings.json"
    hook = {"type": "command", "command": ruyi_hook_command()}
    entry = {"matcher": "*", "hooks": [hook]}

    if target.exists():
        try:
            data = json.loads(target.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError:
            skipped.append(".claude/settings.json")
            notes.append(".claude/settings.json 不是合法 JSON，未自动合并 Ruyi hook。")
            return
    else:
        data = {}

    hooks = data.setdefault("hooks", {})
    submit = hooks.setdefault("UserPromptSubmit", [])
    existing_commands: list[str | None] = []
    for group in submit:
        if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
            continue
        for item in group["hooks"]:
            if isinstance(item, dict):
                existing_commands.append(item.get("command"))
    if hook["command"] in existing_commands:
        skipped.append(".claude/settings.json")
        return

    submit.append(entry)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    updated.append(".claude/settings.json")


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
    create_file(project, ".claude/commands/ruyi.md", slash_command(), created, skipped)
    append_claude_md(project, created, skipped, updated)

    for filename, content in spec_contents(facts).items():
        create_file(project, f".ruyi/spec/{filename}", content, created, skipped)

    if not facts.get("no_hook"):
        merge_claude_settings(project, skipped, updated, notes)
    else:
        skipped.append(".claude/settings.json")
        notes.append("用户选择跳过 Ruyi 入口保护 hook；auto-trigger 可靠性会下降。")

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
    parser.add_argument("--no-hook", action="store_true", help="Skip Claude Code UserPromptSubmit hook")
    args = parser.parse_args(argv)

    facts = json.loads(Path(args.facts).read_text(encoding="utf-8-sig"))
    if args.no_hook:
        facts["no_hook"] = True
    output = json.dumps(write_init(args.project, facts), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
