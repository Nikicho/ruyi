"""Create a Ruyi explain document without overwriting existing files."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


APPROVAL_STATES = ("pending",)
TEST_PASSING_RESULTS = ("passed", "passed-with-notes")
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
    required = (
        "module",
        "feature",
        "date",
        "title",
        "completed",
        "requirement_results",
        "verification",
        "code_quality",
        "code_quality_sources",
    )
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")

    validate_slug("module", payload["module"])
    validate_slug("feature", payload["feature"])

    if not DATE_PATTERN.match(payload["date"]):
        raise ValueError("date must use YYYY-MM-DD")

    approval = payload.get("approval") or "pending"
    if approval not in APPROVAL_STATES:
        raise ValueError("approval must be pending; approval conclusions belong to ruyi-approve")

    if not as_list(payload["completed"]):
        raise ValueError("completed must include at least one item")
    if not as_list(payload["requirement_results"]):
        raise ValueError("requirement_results must include at least one item")
    if not as_list(payload["verification"]):
        raise ValueError("verification must include at least one item")
    if not as_list(payload["code_quality"]):
        raise ValueError("code_quality must include at least one item")
    if not as_list(payload["code_quality_sources"]):
        raise ValueError("code_quality_sources must include plan, implement self-review, or code fact source")


def is_initialized(project: Path) -> bool:
    return (project / ".ruyirc").is_file() and (project / ".ruyi" / "explain").is_dir()


def contract_path(project: Path, payload: dict[str, Any]) -> Path:
    return (
        project
        / ".ruyi"
        / "contracts"
        / payload["module"]
        / payload["feature"]
        / f"{payload['date']}.md"
    )


def test_path(project: Path, payload: dict[str, Any]) -> Path:
    return (
        project
        / ".ruyi"
        / "tests"
        / payload["module"]
        / payload["feature"]
        / f"{payload['date']}.md"
    )


def plan_path(project: Path, payload: dict[str, Any]) -> Path:
    return (
        project
        / ".ruyi"
        / "plans"
        / payload["module"]
        / payload["feature"]
        / f"{payload['date']}.md"
    )


def explain_path(project: Path, payload: dict[str, Any]) -> Path:
    return (
        project
        / ".ruyi"
        / "explain"
        / payload["module"]
        / payload["feature"]
        / f"{payload['date']}.md"
    )


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def rebuild_index_if_available(project: Path) -> dict[str, Any] | None:
    script = Path(__file__).resolve().parents[2] / "using-ruyi" / "scripts" / "index_rebuild.py"
    if not script.is_file():
        return None
    spec = importlib.util.spec_from_file_location("ruyi_index_rebuild", script)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.rebuild_index(project)


def parse_frontmatter(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}

    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def render_explain(payload: dict[str, Any]) -> str:
    contract = f".ruyi/contracts/{payload['module']}/{payload['feature']}/{payload['date']}.md"
    plan = f".ruyi/plans/{payload['module']}/{payload['feature']}/{payload['date']}.md"
    test = f".ruyi/tests/{payload['module']}/{payload['feature']}/{payload['date']}.md"
    summary = bullet_list([f"完成：{item}" for item in as_list(payload["completed"])])
    requirements = bullet_list([f"需求对照：{item}" for item in as_list(payload["requirement_results"])])
    quality = bullet_list([f"代码质量：{item}" for item in as_list(payload["code_quality"])])
    quality_sources = bullet_list([f"质量依据：{item}" for item in as_list(payload["code_quality_sources"])])
    delivery_summary = "\n".join((summary, requirements, quality, quality_sources))
    verification = bullet_list(as_list(payload["verification"]))
    followups = [
        *[f"风险：{item}" for item in as_list(payload.get("risks"))],
        *[f"备注：{item}" for item in as_list(payload.get("technical_notes"))],
    ]
    followup_section = f"\n## 风险与后续\n\n{bullet_list(followups)}\n" if followups else ""

    return f"""---
approval: pending
contract: {contract}
plan: {plan}
test: {test}
---

# Explain：{payload["title"]}

## 交付摘要

{delivery_summary}

## 验证结论

- 证据文件：`{test}`
{verification}
{followup_section}
"""


def create_explain(project_path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    project = Path(project_path)
    validate_payload(payload)

    if not is_initialized(project):
        return {
            "created": False,
            "reason": "project-not-initialized",
            "message": "项目未初始化 Ruyi，不能正式创建 explain。",
            "path": None,
        }

    contract = contract_path(project, payload)
    if not contract.is_file():
        return {
            "created": False,
            "reason": "contract-not-found",
            "message": "对应 contract 不存在，不能创建 explain。",
            "path": None,
            "contract": str(contract),
        }

    plan = plan_path(project, payload)
    if not plan.is_file():
        return {
            "created": False,
            "reason": "plan-not-found",
            "message": "对应 plan 不存在，不能创建 explain。",
            "path": None,
            "plan": str(plan),
        }

    test = test_path(project, payload)
    if not test.is_file():
        return {
            "created": False,
            "reason": "test-not-found",
            "message": "对应 test 不存在，不能创建 explain。",
            "path": None,
            "test": str(test),
        }

    test_result = parse_frontmatter(test).get("result")
    if test_result not in TEST_PASSING_RESULTS:
        return {
            "created": False,
            "reason": "test-not-passed",
            "message": "test 未通过，不能创建 explain。",
            "path": None,
            "test": str(test),
        }

    target = explain_path(project, payload)
    if target.exists():
        existing = target.read_text(encoding="utf-8")
        if parse_frontmatter(target).get("approval") == "pending" and "## 状态变更记录" in existing:
            history_start = existing.find("\n## 状态变更记录")
            history = existing[history_start:] if history_start != -1 else ""
            target.write_text(render_explain(payload).rstrip() + "\n" + history, encoding="utf-8")
            return {
                "created": False,
                "updated": True,
                "reason": None,
                "message": "返工后的 explain 当前内容已更新。",
                "path": str(target),
                "index": rebuild_index_if_available(project),
            }
        return {
            "created": False,
            "reason": "already-exists",
            "message": "explain 已存在，未覆盖。",
            "path": str(target),
        }

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_explain(payload), encoding="utf-8")
    index_result = rebuild_index_if_available(project)
    return {
        "created": True,
        "reason": None,
        "message": "explain 已创建。",
        "path": str(target),
        "index": index_result,
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Create a Ruyi explain document.")
    parser.add_argument("--project", required=True, help="Project root path")
    parser.add_argument("--module", required=True, help="Module slug")
    parser.add_argument("--feature", required=True, help="Feature slug")
    parser.add_argument("--date", required=True, help="Contract date, YYYY-MM-DD")
    parser.add_argument("--title", required=True, help="Explain display title")
    parser.add_argument("--completed", action="append", required=True, help="Completed delivery item")
    parser.add_argument("--requirement-result", action="append", required=True, help="Requirement comparison item")
    parser.add_argument("--verification", action="append", required=True, help="Verification summary item")
    parser.add_argument("--code-quality", action="append", required=True, help="Code quality brief item")
    parser.add_argument("--code-quality-source", action="append", required=True, help="Source for code quality brief")
    parser.add_argument("--risk", action="append", default=[], help="Risk or remaining issue")
    parser.add_argument("--technical-note", action="append", default=[], help="Technical note")
    args = parser.parse_args(argv)

    payload = {
        "module": args.module,
        "feature": args.feature,
        "date": args.date,
        "title": args.title,
        "approval": "pending",
        "completed": args.completed,
        "requirement_results": args.requirement_result,
        "verification": args.verification,
        "code_quality": args.code_quality,
        "code_quality_sources": args.code_quality_source,
        "risks": args.risk,
        "technical_notes": args.technical_note,
    }
    output = json.dumps(create_explain(args.project, payload), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
