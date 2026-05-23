"""Write the initial .ruyi and .ruyirc structure for a supported project."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path, PurePosixPath
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
- `spec-candidates/`：本地临时知识沉淀候选，默认不提交 git，不自动改写正式 spec。
- `spec-archive/`：本地 candidate 处理归档，默认不提交 git。
- `spec-patches/`：本地人工合入补丁，默认不提交 git。
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


def today() -> str:
    return date.today().isoformat()


def frontmatter(confidence: str, source: str, *, needs_review: bool = False) -> str:
    extra = "\nneeds_review: true" if needs_review else ""
    return f"""---
confidence: {confidence}
source: {source}
verified_at: {today()}{extra}
---

"""


def spec_contents(facts: dict[str, Any]) -> dict[str, str]:
    modules = facts.get("module_candidates") or []
    tests = facts.get("test_signals") or []
    questions = facts.get("open_questions") or []

    contents = {
        "INDEX.md": frontmatter("open", "init spec 索引", needs_review=True) + """# Spec Index

本目录只放长期有效的项目事实和项目规则。

## 核心文件

- `project-overview.md`：项目目标、技术栈和业务概况。
- `project-structure.md`：项目目录、模块边界和代码组织。
- `development-baseline.md`：开发过程约束，例如必须运行的检查。
- `coding-baseline.md`：代码编写约束，例如组件、状态、样式、错误处理规则。
- `testing-baseline.md`：测试策略和验收证据要求。
- `api.md`：API 权威源和长期对接原则。
- `open-questions.md`：不能作为事实引用的知识缺口。

## 详细规范

- `references/shared/`：跨模块共享规范。
- `references/modules/`：具体模块或功能的规范。
""",
        "project-overview.md": frontmatter("observed", "init 项目事实读取") + f"""# 项目概览

## 技术栈

- 前端框架：{facts.get("framework") or "待确认"}
- 构建工具：{facts.get("bundler") or "待确认"}
- 主要语言：{facts.get("language") or "待确认"}

## 业务概览

待补充。
""",
        "project-structure.md": frontmatter("observed", "init 项目目录扫描") + f"""# 项目结构

## 初步模块候选

{format_list(modules) if modules else "待确认。"}
""",
        "development-baseline.md": frontmatter("open", "init 占位", needs_review=True) + """# 开发过程基线

## 必跑检查

待补充。

## 变更前后自检

待补充。
""",
        "coding-baseline.md": frontmatter("open", "init 占位", needs_review=True) + """# 代码编写基线

## 组件与状态

待补充。

## 样式与交互

待补充。
""",
        "testing-baseline.md": frontmatter("observed" if tests else "open", "init package.json 检测", needs_review=not bool(tests)) + f"""# 测试基线

## 已识别测试信号

{format_list(tests) if tests else "待确认。"}
""",
        "open-questions.md": frontmatter("open", "init 待确认问题", needs_review=True) + f"""# 待确认问题

{format_list(questions) if questions else "暂无。"}
""",
        "api.md": frontmatter("open", "init API 占位", needs_review=True) + """# API 相关 Spec

本文件维护项目层长期 API 约定和权威源入口。**不维护完整接口列表**，权威源是后端。

建议添加：

- `references/shared/api/source.md`：外部权威 API 文档入口。
- `references/shared/api/response-envelope.md`：统一响应结构。
- `references/shared/api/error-codes.md`：错误码约定。
- `references/shared/api/auth-flow.md`：鉴权流程。
- `references/shared/api/conventions.md`：命名 / 分页 / 排序通用约定。

Ruyi 只引用 API 权威源，不拷贝完整 Swagger / OpenAPI / Apifox 字段表。
""",
        "references/shared/INDEX.md": frontmatter("open", "init shared references 索引", needs_review=True) + """# Shared Spec References

跨模块共享规范放在这里。

建议按领域建文件夹，例如：

- `api/`
- `components/`
- `routing/`
- `errors/`
""",
        "references/modules/INDEX.md": frontmatter("open", "init module references 索引", needs_review=True) + """# Module Spec References

具体模块、页面或功能规范放在这里。

同一功能或公共组件只建一个文件夹，在文件夹内按主题拆分文件，例如：

```text
table/
  simple-usage.md
  usage.md
  columns.md
  internals.md
```
""",
    }
    if is_full_migration(facts):
        contents["docs-registry.md"] = docs_registry(facts)
        contents["interview-bank.md"] = interview_bank(facts)
    return contents


def format_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def brownfield_facts(facts: dict[str, Any]) -> dict[str, Any]:
    value = facts.get("brownfield")
    return value if isinstance(value, dict) else {}


def brownfield_mode(facts: dict[str, Any]) -> str:
    raw_mode = brownfield_facts(facts).get("mode")
    if not raw_mode:
        raise ValueError("brownfield.mode must be explicitly set to quick-start or full-migration before writing init files")
    mode = str(raw_mode).strip().lower()
    return "full-migration" if mode in ("full", "full-migration", "migration", "complete") else "quick-start"


def is_full_migration(facts: dict[str, Any]) -> bool:
    return brownfield_mode(facts) == "full-migration"


def document_sources(facts: dict[str, Any]) -> list[dict[str, Any]]:
    items = brownfield_facts(facts).get("document_sources") or []
    return [item for item in items if isinstance(item, dict)]


def quality_of(source: dict[str, Any]) -> str:
    return str(source.get("quality") or source.get("decision") or "unreviewed").lower()


def useful_sources(facts: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in document_sources(facts) if quality_of(item) in ("useful", "high", "medium")]


def partial_sources(facts: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in document_sources(facts) if quality_of(item) in ("partial", "distill", "low")]


def discarded_sources(facts: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in document_sources(facts) if quality_of(item) in ("discard", "garbage", "deprecated")]


def docs_registry(facts: dict[str, Any]) -> str:
    sources = useful_sources(facts)
    sections = []
    for source in sources:
        title = source.get("title") or source.get("path") or "未命名文档"
        category = source.get("category") or "项目文档"
        path = source.get("url") or source.get("path") or "待补充"
        content = source.get("content") or source.get("summary") or "待补充。"
        usage = source.get("recommended_usage") or source.get("usage") or "按需查阅，引用前结合当前代码判断。"
        sections.append(
            f"""## {category}

### {title}
- 链接：{path}
- 内容：{content}
- 推荐用法：{usage}
"""
        )

    body = "\n".join(sections) if sections else "暂无已确认仍有参考价值的外部文档入口。\n"
    return frontmatter("confirmed_by_user" if sources else "open", "init 文档评估", needs_review=not bool(sources)) + f"""# 项目外部文档入口

> 只记录已评估并确认仍有参考价值的入口；陈旧 / 已废文档不录入。
> 完整评估痕迹见 `.ruyi/workspace/init-evaluation-notes.md`。

{body}"""


def interview_bank(facts: dict[str, Any]) -> str:
    answers = brownfield_facts(facts).get("interview_answers") or {}
    if not isinstance(answers, dict) or not answers:
        return frontmatter("open", "init 澄清问卷", needs_review=True) + """# 澄清问卷答案

暂无已确认问卷答案。
"""

    sections = []
    for topic, values in answers.items():
        sections.append(f"## {topic}")
        if isinstance(values, dict):
            for key, value in values.items():
                sections.append(f"- {key}：{value}")
        else:
            sections.append(f"- {values}")
        sections.append("")
    return frontmatter("confirmed_by_user", "init 澄清问卷") + "# 澄清问卷答案\n\n" + "\n".join(sections)


def evaluation_notes(facts: dict[str, Any]) -> str:
    registered = useful_sources(facts)
    partial = partial_sources(facts)
    discarded = discarded_sources(facts)

    def source_lines(items: list[dict[str, Any]], empty: str) -> str:
        if not items:
            return empty
        lines: list[str] = []
        for item in items:
            path = item.get("path") or item.get("url") or "未知来源"
            reason = item.get("reason") or item.get("summary") or item.get("content") or "未填写评估说明。"
            lines.append(f"### {path}\n- 评估：{reason}")
            if item.get("distilled_to") or item.get("baseline_contract") or item.get("contract_target"):
                target = safe_baseline_contract_target(item, facts)
                lines.append(f"- 蒸馏目标：contracts/{target}")
        return "\n\n".join(lines)

    return f"""# Init 评估笔记（{today()}）
> 一次性记录，不进 agent 默认上下文。仅供后续 init 复盘或团队回顾。

## 已录入 docs-registry（{len(registered)} 条）

{source_lines(registered, "暂无。")}

## 已蒸馏关键事实进 baseline contract（{len(partial)} 条）

{source_lines(partial, "暂无。")}

## 未录入也未蒸馏（{len(discarded)} 条）

{source_lines(discarded, "暂无。")}
"""


def baseline_contracts(facts: dict[str, Any]) -> dict[str, str]:
    if not is_full_migration(facts):
        return {}
    contracts: dict[str, dict[str, list[str]]] = {}
    for source in partial_sources(facts):
        facts_list = source.get("distilled_facts") or []
        observed_list = source.get("observed_facts") or source.get("code_observed_facts") or []
        if not facts_list:
            continue
        target = safe_baseline_contract_target(source, facts)
        entry = contracts.setdefault(target, {"titles": [], "distilled": [], "observed": []})
        entry["titles"].append(str(source.get("title") or "文档蒸馏"))
        entry["distilled"].extend(str(item) for item in facts_list)
        entry["observed"].extend(str(item) for item in observed_list)
    return {target: render_baseline_contract(target, data) for target, data in contracts.items()}


def safe_baseline_contract_target(source: dict[str, Any], facts: dict[str, Any]) -> str:
    default_module = safe_contract_segment(
        source.get("module")
        or source.get("target_module")
        or brownfield_facts(facts).get("default_module")
        or "project"
    )
    default = f"{default_module}/_baseline/current.md"
    value = source.get("baseline_contract") or source.get("contract_target") or source.get("distilled_to")
    raw = str(value or default).replace("\\", "/").lstrip("/")
    if raw.startswith("contracts/"):
        raw = raw.removeprefix("contracts/")
    target = PurePosixPath(raw)
    if not target.parts or any(part in ("", ".", "..") for part in target.parts):
        return default
    if len(target.parts) != 3 or target.suffix != ".md":
        return default
    module, feature, filename = target.parts
    if not all(safe_contract_segment(part) == part for part in (module, feature, filename.removesuffix(".md"))):
        return default
    return target.as_posix()


def safe_contract_segment(value: Any) -> str:
    text = str(value or "").strip().replace("\\", "/").strip("/")
    if "/" in text:
        text = text.split("/")[-1]
    cleaned = "".join(char if char.isalnum() or char in ("-", "_") else "-" for char in text.lower())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned or "project"


def render_baseline_contract(target: str, data: dict[str, list[str]]) -> str:
    module, feature, _filename = PurePosixPath(target).parts
    titles = sorted(set(data.get("titles") or []))
    distilled = sorted(set(data.get("distilled") or []))
    observed = sorted(set(data.get("observed") or []))
    observed_section = format_list(observed) if observed else "- 暂无代码观察事实；后续可由代码反推补充。"
    return f"""---
type: baseline
status: draft
module: {module}
feature: {feature}
confidence: distilled
source: init full-migration
verified_at: {today()}
needs_review: true
---

# Baseline Contract：{module}/{feature}

## 定位

本文件记录成熟项目接入 Ruyi 时，从历史文档蒸馏和现有代码观察得到的当前业务事实。

它不是一次新需求，不直接进入 plan / implement / test；后续相关变更应先读取本 baseline，再创建本次变更 contract。

## 来源摘要

{format_list(titles) if titles else "- init full-migration"}

## 当前业务事实

{format_list(distilled) if distilled else "- 暂无。"}

## 代码观察

{observed_section}

## 已知不确定项

- 本文件为 `draft` 且 `needs_review: true` 时，引用前必须请用户确认。

## 维护规则

- 后续变更如果改变当前业务事实，应在交付后更新本 baseline 或生成 baseline patch。
- 稳定的开发约束进入 `.ruyi/spec/`；模块业务事实保留在 baseline contract。
"""


def unknown_answer_count(facts: dict[str, Any]) -> int:
    value = brownfield_facts(facts).get("unknown_answers") or 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def fallback_required(facts: dict[str, Any]) -> bool:
    if not is_full_migration(facts):
        return False
    brownfield = brownfield_facts(facts)
    return bool(brownfield.get("fallback")) or unknown_answer_count(facts) >= 3


def fallback_specs() -> dict[str, str]:
    return {
        "references/shared/auth/flow.md": frontmatter("open", "init fallback", needs_review=True) + """# 鉴权流程

待确认。init 阶段未能确认当前项目鉴权方式。
agent 在涉及鉴权的 contract / implement 阶段必须先询问。
""",
        "references/shared/errors/handling.md": frontmatter("open", "init fallback", needs_review=True) + """# 错误处理

待确认。init 阶段未能确认当前项目错误处理约定。
agent 在涉及接口、异常提示或状态处理时必须先询问。
""",
        "references/shared/routing/conventions.md": frontmatter("open", "init fallback", needs_review=True) + """# 路由约定

待确认。init 阶段未能确认当前项目路由组织方式。
agent 在新增页面、权限或导航逻辑前必须先询问。
""",
    }


def brownfield_result(facts: dict[str, Any]) -> dict[str, Any]:
    if not is_full_migration(facts):
        return {"mode": "quick-start"}
    return {
        "mode": "full-migration",
        "registered_docs": [str(item.get("path") or item.get("url") or item.get("title")) for item in useful_sources(facts)],
        "distilled_docs": [str(item.get("path") or item.get("title")) for item in partial_sources(facts) if item.get("distilled_facts")],
        "baseline_contracts": sorted(baseline_contracts(facts).keys()),
        "interview_answer_count": sum(len(value) if isinstance(value, dict) else 1 for value in (brownfield_facts(facts).get("interview_answers") or {}).values()),
        "open_topics": brownfield_facts(facts).get("open_topics") or [],
        "fallback": fallback_required(facts),
        "evaluation_notes": ".ruyi/workspace/init-evaluation-notes.md",
    }


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
    brownfield_mode(facts)
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

    for filename, content in baseline_contracts(facts).items():
        create_file(project, f".ruyi/contracts/{filename}", content, created, skipped)

    if fallback_required(facts):
        for filename, content in fallback_specs().items():
            create_file(project, f".ruyi/spec/{filename}", content, created, skipped)
        notes.append("知识基线非常薄弱：本次 init 只记录 observed/open 事实，后续 contract 阶段必须更仔细澄清。")

    if is_full_migration(facts):
        create_file(project, ".ruyi/workspace/init-evaluation-notes.md", evaluation_notes(facts), created, skipped)

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
        "brownfield": brownfield_result(facts),
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
