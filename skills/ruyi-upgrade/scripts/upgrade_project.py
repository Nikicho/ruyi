"""Upgrade an initialized Ruyi project to the current structural schema."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
from pathlib import Path, PurePosixPath
from typing import Any


CURRENT_SCHEMA_VERSION = 3
OBSOLETE_DIRS = (
    ".ruyi/explain",
    ".ruyi/workspace",
    ".ruyi/spec-archive",
    ".ruyi/spec-patches",
)
REMOVED_IGNORE_RULES = (
    "!.ruyi/workspace/README.md",
)
LOCAL_IGNORE_RULES = (
    ".ruyi/tasks/**",
    ".ruyi/spec-candidates/**",
    ".ruyi/explain/**",
    ".ruyi/workspace/**",
    ".ruyi/spec-archive/**",
    ".ruyi/spec-patches/**",
)
SPEC_DIRS = (
    ".ruyi/spec",
    ".ruyi/spec/references",
    ".ruyi/spec/references/shared",
    ".ruyi/spec/references/modules",
    ".ruyi/contracts",
    ".ruyi/plans",
    ".ruyi/tests",
)
PROCESS_KEYWORDS = (
    "lint",
    "build",
    "test",
    "npm run",
    "pnpm",
    "yarn",
    "git",
    "commit",
    "fast-browser",
    "验证",
    "测试",
    "构建",
    "检查",
    "提交",
)
BUSINESS_FACT_PATTERNS = (
    "business facts",
    "current behavior",
    "existing behavior",
    "当前业务事实",
    "现状",
    "已有能力",
)


def schema_version(ruyirc_text: str) -> int:
    match = re.search(r"^schema_version:\s*(\d+)\s*$", ruyirc_text, re.MULTILINE)
    return int(match.group(1)) if match else 1


def write_schema_version(target: Path, text: str, result: dict[str, Any]) -> None:
    current = schema_version(text)
    if current > CURRENT_SCHEMA_VERSION:
        raise ValueError(f"project schema {current} is newer than supported schema {CURRENT_SCHEMA_VERSION}")
    if current == CURRENT_SCHEMA_VERSION and "schema_version:" in text:
        return
    if re.search(r"^schema_version:\s*\d+\s*$", text, re.MULTILINE):
        updated = re.sub(
            r"^schema_version:\s*\d+\s*$",
            f"schema_version: {CURRENT_SCHEMA_VERSION}",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        updated = f"schema_version: {CURRENT_SCHEMA_VERSION}\n\n{text.lstrip()}"
    target.write_text(updated, encoding="utf-8")
    result["updated"].append(".ruyirc")


def parse_frontmatter_text(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data, text[end + len("\n---\n") :]


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    if not path.is_file():
        return {}, ""
    return parse_frontmatter_text(path.read_text(encoding="utf-8"))


def render_frontmatter(data: dict[str, str]) -> str:
    ordered = ["type", "status", "contract", "plan", "module", "feature", "date", "result", "approval", "return_stage"]
    lines: list[str] = []
    for key in ordered:
        if key in data:
            lines.append(f"{key}: {data[key]}")
    for key in sorted(key for key in data if key not in ordered):
        lines.append(f"{key}: {data[key]}")
    return "---\n" + "\n".join(lines) + "\n---\n"


def relative_to_project(project: Path, path: Path) -> str:
    return path.relative_to(project).as_posix()


def ensure_v3_dirs(project: Path, result: dict[str, Any]) -> None:
    for relative in SPEC_DIRS:
        target = project / relative
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            result["created"].append(relative)


def migrate_gitignore(project: Path, result: dict[str, Any]) -> None:
    target = project / ".gitignore"
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    lines = existing.splitlines()
    kept = [line for line in lines if line not in REMOVED_IGNORE_RULES]
    for rule in LOCAL_IGNORE_RULES:
        if rule not in kept:
            kept.append(rule)
    updated = "\n".join(kept).rstrip() + "\n"
    if updated != existing:
        target.write_text(updated, encoding="utf-8")
        result["updated"].append(".gitignore")


def default_frontmatter(source: str, *, needs_review: bool = True) -> str:
    review = "\nneeds_review: true" if needs_review else ""
    return f"---\nconfidence: open\nsource: {source}\nverified_at: unknown{review}\n---\n\n"


def ensure_spec_index(project: Path, result: dict[str, Any]) -> None:
    target = project / ".ruyi" / "spec" / "INDEX.md"
    if target.exists():
        return
    target.write_text(
        default_frontmatter("ruyi-upgrade") +
        """# Spec Index

## 核心文件

- `project-overview.md`
- `project-structure.md`
- `development-baseline.md`
- `coding-baseline.md`
- `testing-baseline.md`
- `api.md`
- `open-questions.md`

## 详细规范

- `references/shared/`
- `references/modules/`
""",
        encoding="utf-8",
    )
    result["created"].append(".ruyi/spec/INDEX.md")


def classify_frontend_baseline(text: str) -> tuple[str, str]:
    _frontmatter, body = parse_frontmatter_text(text)
    process_lines: list[str] = []
    coding_lines: list[str] = []
    for line in body.splitlines():
        lowered = line.lower()
        if any(keyword in lowered or keyword in line for keyword in PROCESS_KEYWORDS):
            process_lines.append(line)
        else:
            coding_lines.append(line)
    process = "\n".join(process_lines).strip() or "待补充。"
    coding = "\n".join(coding_lines).strip() or "待补充。"
    return process, coding


def write_if_missing_or_empty(target: Path, content: str, result: dict[str, Any]) -> None:
    if target.exists() and target.read_text(encoding="utf-8").strip():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    result["updated" if target.exists() else "created"].append(relative_to_project(target.parents[2], target))


def migrate_spec_baselines(project: Path, result: dict[str, Any]) -> None:
    spec = project / ".ruyi" / "spec"
    old = spec / "frontend-baseline.md"
    if old.is_file():
        process, coding = classify_frontend_baseline(old.read_text(encoding="utf-8"))
        for name, title, body in (
            ("development-baseline.md", "开发过程基线", process),
            ("coding-baseline.md", "代码编写基线", coding),
        ):
            target = spec / name
            if not target.exists():
                target.write_text(default_frontmatter("frontend-baseline split") + f"# {title}\n\n{body}\n", encoding="utf-8")
                result["created"].append(relative_to_project(project, target))
        old.unlink()
        result["deleted"].append(relative_to_project(project, old))

    for name, title in (
        ("development-baseline.md", "开发过程基线"),
        ("coding-baseline.md", "代码编写基线"),
        ("testing-baseline.md", "测试基线"),
        ("api.md", "API 相关 Spec"),
        ("open-questions.md", "待确认问题"),
    ):
        target = spec / name
        if not target.exists():
            target.write_text(default_frontmatter("ruyi-upgrade") + f"# {title}\n\n待补充。\n", encoding="utf-8")
            result["created"].append(relative_to_project(project, target))


def merge_spec_indexes(project: Path, result: dict[str, Any]) -> None:
    root_index = project / ".ruyi" / "spec" / "INDEX.md"
    existing = root_index.read_text(encoding="utf-8") if root_index.exists() else ""
    merged_sections: list[str] = []
    for relative in ("references/shared/INDEX.md", "references/modules/INDEX.md"):
        target = project / ".ruyi" / "spec" / relative
        if not target.is_file():
            continue
        text = target.read_text(encoding="utf-8").strip()
        if text:
            merged_sections.append(f"## Legacy {relative}\n\n{text}")
        target.unlink()
        result["deleted"].append(relative_to_project(project, target))
    if merged_sections:
        addition = "\n\n## 合并的旧二级索引\n\n" + "\n\n".join(merged_sections) + "\n"
        root_index.write_text(existing.rstrip() + addition, encoding="utf-8")
        result["updated"].append(relative_to_project(project, root_index))


def safe_contract_segment(value: str) -> str:
    text = value.strip().replace("\\", "/").strip("/")
    if "/" in text:
        text = text.split("/")[-1]
    cleaned = "".join(char if char.isalnum() or char in ("-", "_") else "-" for char in text.lower())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned or "project"


def migrate_spec_business_facts(project: Path, result: dict[str, Any]) -> None:
    spec = project / ".ruyi" / "spec"
    if not spec.is_dir():
        return
    for path in spec.rglob("*.md"):
        relative = path.relative_to(spec).as_posix()
        if relative in {
            "INDEX.md",
            "project-overview.md",
            "project-structure.md",
            "development-baseline.md",
            "coding-baseline.md",
            "testing-baseline.md",
            "api.md",
            "open-questions.md",
        }:
            continue
        text = path.read_text(encoding="utf-8")
        signal = f"{relative}\n{text[:500]}".lower()
        if not any(pattern in signal for pattern in BUSINESS_FACT_PATTERNS):
            continue
        module = safe_contract_segment(path.parent.name if path.parent != spec else "project")
        target = project / ".ruyi" / "contracts" / module / "_baseline" / "current.md"
        if target.exists():
            result["needs_user_decision"].append(
                f"{relative}: detected business facts but baseline contract already exists"
            )
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            f"""---
type: baseline
status: draft
module: {module}
feature: _baseline
confidence: distilled
source: migrated from .ruyi/spec/{relative}
verified_at: unknown
needs_review: true
---

# Baseline Contract：{module}/_baseline

## 当前业务事实

{text.strip()}

## 已知不确定项

- 本文件由旧 spec 中的业务事实迁移而来，引用前必须请用户确认。
""",
            encoding="utf-8",
        )
        result["created"].append(relative_to_project(project, target))


def test_path_from_explain(project: Path, explain: Path, frontmatter: dict[str, str]) -> Path:
    explicit = frontmatter.get("test")
    if explicit:
        return project / explicit.replace("/", "\\")
    relative = explain.relative_to(project / ".ruyi" / "explain")
    return project / ".ruyi" / "tests" / relative


def ensure_test_for_explain(project: Path, explain: Path, frontmatter: dict[str, str], result: dict[str, Any]) -> Path:
    target = test_path_from_explain(project, explain, frontmatter)
    if target.exists():
        return target
    relative = explain.relative_to(project / ".ruyi" / "explain")
    module, feature, filename = relative.parts[0], relative.parts[1], relative.name
    date = filename.removesuffix(".md")
    target.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "contract": frontmatter.get("contract", f".ruyi/contracts/{module}/{feature}/{date}.md"),
        "plan": frontmatter.get("plan", f".ruyi/plans/{module}/{feature}/{date}.md"),
        "module": module,
        "feature": feature,
        "date": date,
        "result": "passed-with-notes",
        "approval": "pending",
    }
    target.write_text(
        render_frontmatter(data)
        + f"\n# Test：{feature}\n\n## 验收与证据\n\n- 由旧 explain 迁移，原始验证证据需复核。\n\n## 结论\n\n旧 explain 存在，升级时补充最小 test 占位。\n",
        encoding="utf-8",
    )
    result["created"].append(relative_to_project(project, target))
    return target


def extract_approval_reason(body: str) -> str:
    if "## 审批结论" not in body:
        return "由旧 explain 迁移。"
    section = body.split("## 审批结论", 1)[1]
    next_section = section.find("\n## ")
    if next_section != -1:
        section = section[:next_section]
    for line in section.splitlines():
        if "审批说明" in line or "原因" in line:
            return line.strip().lstrip("- ").split("：", 1)[-1].strip() or "由旧 explain 迁移。"
    return "由旧 explain 迁移。"


def remove_existing_approval_section(body: str) -> str:
    marker = "## 审批结论"
    start = body.find(marker)
    if start == -1:
        return body.strip()
    next_section = body.find("\n## ", start + len(marker))
    if next_section == -1:
        return body[:start].strip()
    return (body[:start] + body[next_section:]).strip()


def migrate_explain_to_tests(project: Path, result: dict[str, Any]) -> None:
    explains = project / ".ruyi" / "explain"
    if not explains.is_dir():
        return
    for explain in sorted(explains.rglob("*.md")):
        frontmatter, body = parse_frontmatter(explain)
        target = ensure_test_for_explain(project, explain, frontmatter, result)
        test_frontmatter, test_body = parse_frontmatter(target)
        approval = frontmatter.get("approval")
        if approval in ("approved", "changes-requested"):
            test_frontmatter["approval"] = approval
            if frontmatter.get("return_stage"):
                test_frontmatter["return_stage"] = frontmatter["return_stage"]
        else:
            test_frontmatter.setdefault("approval", "pending")
        test_frontmatter.setdefault("result", "passed-with-notes")
        test_frontmatter.setdefault("contract", frontmatter.get("contract", ""))
        test_frontmatter.setdefault("plan", frontmatter.get("plan", ""))
        cleaned = remove_existing_approval_section(test_body)
        approval_section = ""
        if test_frontmatter.get("approval") in ("approved", "changes-requested"):
            return_stage = test_frontmatter.get("return_stage") or "无需返回。"
            approval_section = (
                "\n\n## 审批结论\n\n"
                f"- 审批状态：{test_frontmatter['approval']}\n"
                f"- 审批说明：{extract_approval_reason(body)}\n"
                f"- 返回阶段：{return_stage}\n"
            )
        target.write_text(render_frontmatter(test_frontmatter) + "\n" + cleaned + approval_section, encoding="utf-8")
        result["updated"].append(relative_to_project(project, target))


def migrate_entry_files(project: Path, result: dict[str, Any]) -> None:
    replacements = {
        "contract / plan / test / explain": "contract / plan / test",
        "contract / plan / explain": "contract / plan / test",
        "plan/test/explain": "plan/test",
        "explain 审批状态": "test 审批状态",
        "更新 explain": "更新 test",
        "生成 explain": "记录 test 验证摘要",
        ".ruyi/explain/": ".ruyi/tests/",
    }
    for relative in ("CLAUDE.md", ".claude/commands/ruyi.md", ".ruyi/project-actions.md", ".ruyi/README.md"):
        target = project / relative
        if not target.is_file():
            continue
        text = target.read_text(encoding="utf-8")
        updated = text
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != text:
            target.write_text(updated, encoding="utf-8")
            result["updated"].append(relative)


def remove_obsolete_dirs(project: Path, result: dict[str, Any], *, remove_obsolete: bool) -> list[str]:
    obsolete_dirs = [relative for relative in OBSOLETE_DIRS if (project / relative).is_dir()]
    if not remove_obsolete:
        return obsolete_dirs
    for relative in obsolete_dirs:
        shutil.rmtree(project / relative)
        result["deleted"].append(relative)
    return []


def rebuild_indexes(project: Path, result: dict[str, Any]) -> None:
    script = Path(__file__).resolve().parents[2] / "using-ruyi" / "scripts" / "index_rebuild.py"
    if not script.is_file():
        return
    spec = importlib.util.spec_from_file_location("ruyi_index_rebuild", script)
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    index_result = module.rebuild_index(project)
    result["index"] = index_result
    if index_result and index_result.get("updated"):
        result["updated"].append(".ruyi/INDEX.md")


def upgrade_project(project_path: str | Path, *, remove_obsolete: bool = False) -> dict[str, Any]:
    """Upgrade deterministic Ruyi structure without changing business semantics."""
    project = Path(project_path)
    ruyirc = project / ".ruyirc"
    ruyi = project / ".ruyi"
    if not ruyirc.is_file() or not ruyi.is_dir():
        raise ValueError("project is not initialized with .ruyirc and .ruyi")

    ruyirc_text = ruyirc.read_text(encoding="utf-8")
    from_schema = schema_version(ruyirc_text)
    result: dict[str, Any] = {
        "from_schema": from_schema,
        "to_schema": CURRENT_SCHEMA_VERSION,
        "completed": False,
        "needs_confirmation": False,
        "updated": [],
        "created": [],
        "deleted": [],
        "obsolete_dirs": [],
        "needs_user_decision": [],
        "index": None,
    }

    ensure_v3_dirs(project, result)
    migrate_gitignore(project, result)
    ensure_spec_index(project, result)
    migrate_spec_baselines(project, result)
    merge_spec_indexes(project, result)
    migrate_spec_business_facts(project, result)
    migrate_explain_to_tests(project, result)
    migrate_entry_files(project, result)
    remaining_obsolete = remove_obsolete_dirs(project, result, remove_obsolete=remove_obsolete)
    result["obsolete_dirs"] = remaining_obsolete
    result["needs_confirmation"] = bool(remaining_obsolete)

    if not remaining_obsolete:
        write_schema_version(ruyirc, ruyirc.read_text(encoding="utf-8"), result)
        result["completed"] = True

    rebuild_indexes(project, result)
    for key in ("updated", "created", "deleted", "obsolete_dirs", "needs_user_decision"):
        result[key] = sorted(dict.fromkeys(result[key]))
    return result


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Upgrade a Ruyi project schema.")
    parser.add_argument("--project", required=True, help="Initialized project root")
    parser.add_argument("--remove-obsolete", action="store_true", help="Delete reported obsolete Ruyi directories")
    args = parser.parse_args(argv)
    output = json.dumps(
        upgrade_project(args.project, remove_obsolete=args.remove_obsolete),
        ensure_ascii=False,
        indent=2,
    )
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
