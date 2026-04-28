"""Create a Ruyi spec evolution candidate without updating formal spec files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


TARGET_LAYERS = ("project", "team")
TARGET_SPECS = (
    "project-overview.md",
    "project-structure.md",
    "frontend-baseline.md",
    "testing-baseline.md",
    "open-questions.md",
)
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def validate_slug(name: str, value: str) -> None:
    if not SLUG_PATTERN.match(value):
        raise ValueError(f"{name} must use lowercase letters, numbers, and hyphens: {value}")


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def validate_payload(payload: dict[str, Any]) -> None:
    required = ("module", "feature", "date", "title", "target_layer", "target_spec", "proposals", "evidence", "scope")
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")

    validate_slug("module", payload["module"])
    validate_slug("feature", payload["feature"])

    if not DATE_PATTERN.match(payload["date"]):
        raise ValueError("date must use YYYY-MM-DD")
    if payload["target_layer"] not in TARGET_LAYERS:
        raise ValueError(f"target_layer must be one of: {', '.join(TARGET_LAYERS)}")
    if payload["target_spec"] not in TARGET_SPECS:
        raise ValueError(f"target_spec must be one of: {', '.join(TARGET_SPECS)}")
    if not as_list(payload["proposals"]):
        raise ValueError("proposals must include at least one item")
    if not as_list(payload["evidence"]):
        raise ValueError("evidence must include at least one item")
    if not as_list(payload["scope"]):
        raise ValueError("scope must include at least one item")


def is_initialized(project: Path) -> bool:
    return (project / ".ruyirc").is_file() and (project / ".ruyi" / "spec-candidates").is_dir()


def explain_path(project: Path, payload: dict[str, Any]) -> Path:
    return (
        project
        / ".ruyi"
        / "explain"
        / payload["module"]
        / payload["feature"]
        / f"{payload['date']}.md"
    )


def candidate_path(project: Path, payload: dict[str, Any]) -> Path:
    return (
        project
        / ".ruyi"
        / "spec-candidates"
        / payload["module"]
        / payload["feature"]
        / f"{payload['date']}.md"
    )


def parse_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None

    end = text.find("\n---\n", 4)
    if end == -1:
        return None

    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def render_candidate(payload: dict[str, Any]) -> str:
    explain = f".ruyi/explain/{payload['module']}/{payload['feature']}/{payload['date']}.md"
    excluded = as_list(payload.get("excluded")) or ["暂无。"]
    open_questions = as_list(payload.get("open_questions")) or ["暂无。"]

    return f"""---
source_explain: {explain}
module: {payload["module"]}
feature: {payload["feature"]}
date: {payload["date"]}
target_layer: {payload["target_layer"]}
target_spec: {payload["target_spec"]}
status: pending
---

# Spec Candidate：{payload["title"]}

## 沉淀建议

{bullet_list(as_list(payload["proposals"]))}

## 依据

{bullet_list(as_list(payload["evidence"]))}

## 适用范围

{bullet_list(as_list(payload["scope"]))}

## 不应沉淀内容

{bullet_list(excluded)}

## 待确认问题

{bullet_list(open_questions)}
"""


def create_candidate(project_path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    project = Path(project_path)
    validate_payload(payload)

    if not is_initialized(project):
        return {
            "created": False,
            "reason": "project-not-initialized",
            "message": "项目未初始化 Ruyi，不能创建 spec candidate。",
            "path": None,
        }

    explain = explain_path(project, payload)
    if not explain.is_file():
        return {
            "created": False,
            "reason": "explain-not-found",
            "message": "对应 explain 不存在，不能创建 spec candidate。",
            "path": None,
            "explain": str(explain),
        }

    frontmatter = parse_frontmatter(explain.read_text(encoding="utf-8"))
    approval = frontmatter.get("approval") if frontmatter else None
    missing_anchors = [
        key for key in ("contract", "plan", "test") if not frontmatter or not frontmatter.get(key)
    ]
    if missing_anchors:
        return {
            "created": False,
            "reason": "explain-missing-anchors",
            "message": "explain 缺少 contract、plan 或 test 锚点，不能创建 spec candidate。",
            "path": None,
            "missing": missing_anchors,
        }
    if approval != "approved":
        return {
            "created": False,
            "reason": "approval-not-approved",
            "message": "explain 未审批通过，不能创建 spec candidate。",
            "path": None,
            "approval": approval,
        }

    target = candidate_path(project, payload)
    if target.exists():
        return {
            "created": False,
            "reason": "already-exists",
            "message": "spec candidate 已存在，未覆盖。",
            "path": str(target),
        }

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_candidate(payload), encoding="utf-8")
    return {
        "created": True,
        "reason": None,
        "message": "spec candidate 已创建。",
        "path": str(target),
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Create a Ruyi spec evolution candidate.")
    parser.add_argument("--project", required=True, help="Project root path")
    parser.add_argument("--module", required=True, help="Module slug")
    parser.add_argument("--feature", required=True, help="Feature slug")
    parser.add_argument("--date", required=True, help="Contract date, YYYY-MM-DD")
    parser.add_argument("--title", required=True, help="Candidate display title")
    parser.add_argument("--target-layer", required=True, choices=TARGET_LAYERS, help="Target layer")
    parser.add_argument("--target-spec", required=True, choices=TARGET_SPECS, help="Target spec file")
    parser.add_argument("--proposal", action="append", required=True, help="Reusable rule or fact candidate")
    parser.add_argument("--evidence", action="append", required=True, help="Evidence supporting the candidate")
    parser.add_argument("--scope", action="append", required=True, help="Applicable scope")
    parser.add_argument("--excluded", action="append", default=[], help="Content that should not be promoted")
    parser.add_argument("--open-question", action="append", default=[], help="Open question")
    args = parser.parse_args(argv)

    payload = {
        "module": args.module,
        "feature": args.feature,
        "date": args.date,
        "title": args.title,
        "target_layer": args.target_layer,
        "target_spec": args.target_spec,
        "proposals": args.proposal,
        "evidence": args.evidence,
        "scope": args.scope,
        "excluded": args.excluded,
        "open_questions": args.open_question,
    }
    output = json.dumps(create_candidate(args.project, payload), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
