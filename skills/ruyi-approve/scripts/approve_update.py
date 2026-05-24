"""Update a Ruyi test document with an approval decision."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


APPROVAL_STATUSES = ("approved", "changes-requested")
RETURN_STAGES = ("contract", "plan", "implement", "test")
PASSED_TEST_RESULTS = ("passed", "passed-with-notes")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def validate_slug(name: str, value: str) -> None:
    if not SLUG_PATTERN.match(value):
        raise ValueError(f"{name} must use lowercase letters, numbers, and hyphens: {value}")


def validate_payload(payload: dict[str, Any]) -> None:
    required = ("module", "feature", "date", "status", "reason")
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")

    validate_slug("module", payload["module"])
    validate_slug("feature", payload["feature"])

    if not DATE_PATTERN.match(payload["date"]):
        raise ValueError("date must use YYYY-MM-DD")
    if payload["status"] not in APPROVAL_STATUSES:
        raise ValueError(f"status must be one of: {', '.join(APPROVAL_STATUSES)}")

    return_stage = payload.get("return_stage")
    if payload["status"] != "approved":
        if not return_stage:
            raise ValueError("return_stage is required when approval is not approved")
        if return_stage not in RETURN_STAGES:
            raise ValueError(f"return_stage must be one of: {', '.join(RETURN_STAGES)}")
    elif return_stage:
        raise ValueError("return_stage is not allowed for approved")


def is_initialized(project: Path) -> bool:
    return (project / ".ruyirc").is_file() and (project / ".ruyi" / "tests").is_dir()


def test_path(project: Path, payload: dict[str, Any]) -> Path:
    return (
        project
        / ".ruyi"
        / "tests"
        / payload["module"]
        / payload["feature"]
        / f"{payload['date']}.md"
    )


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


def parse_frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    if not text.startswith("---\n"):
        return None

    end = text.find("\n---\n", 4)
    if end == -1:
        return None

    raw = text[4:end]
    body = text[end + len("\n---\n") :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data, body


def render_frontmatter(data: dict[str, str]) -> str:
    ordered = ["contract", "plan", "module", "feature", "date", "result", "approval", "return_stage"]
    lines: list[str] = []
    for key in ordered:
        if key in data:
            lines.append(f"{key}: {data[key]}")
    for key in sorted(key for key in data if key not in ordered):
        lines.append(f"{key}: {data[key]}")
    return "---\n" + "\n".join(lines) + "\n---\n"


def render_approval_section(payload: dict[str, Any]) -> str:
    return_stage = payload.get("return_stage") or "无需返回。"
    lines = [
        "## 审批结论",
        "",
        f"- 审批状态：{payload['status']}",
        f"- 审批说明：{payload['reason']}",
        f"- 返回阶段：{return_stage}",
    ]

    if payload.get("follow_up"):
        lines.append(f"- 后续动作：{payload['follow_up']}")

    return "\n".join(lines) + "\n"


def remove_existing_approval_section(body: str) -> str:
    marker = "## 审批结论"
    start = body.find(marker)
    if start == -1:
        return body.strip()

    next_section = body.find("\n## ", start + len(marker))
    if next_section == -1:
        return body[:start].strip()
    return (body[:start] + body[next_section:]).strip()


def update_approval(project_path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    project = Path(project_path)
    validate_payload(payload)

    if not is_initialized(project):
        return {
            "updated": False,
            "reason": "project-not-initialized",
            "message": "项目未初始化 Ruyi，不能记录审批结论。",
            "path": None,
        }

    target = test_path(project, payload)
    if not target.is_file():
        return {
            "updated": False,
            "reason": "test-not-found",
            "message": "对应 test 不存在，不能记录审批结论。",
            "path": str(target),
        }

    text = target.read_text(encoding="utf-8")
    parsed = parse_frontmatter(text)
    if not parsed:
        return {
            "updated": False,
            "reason": "missing-frontmatter",
            "message": "test 缺少头部元信息，不能安全记录审批结论。",
            "path": str(target),
        }

    frontmatter, body = parsed
    if not frontmatter.get("contract"):
        return {
            "updated": False,
            "reason": "missing-contract-anchor",
            "message": "test 缺少对应 contract，不能审批。",
            "path": str(target),
        }

    if not frontmatter.get("plan"):
        return {
            "updated": False,
            "reason": "missing-plan-anchor",
            "message": "test 缺少对应 plan，不能审批。",
            "path": str(target),
        }

    test_result = frontmatter.get("result")
    if test_result not in PASSED_TEST_RESULTS:
        return {
            "updated": False,
            "reason": "test-not-passed",
            "message": "test 未通过，不能审批。",
            "path": str(target),
            "result": test_result,
        }

    current_approval = frontmatter.get("approval")
    if current_approval != "pending":
        return {
            "updated": False,
            "reason": "approval-not-pending",
            "message": "test 审批状态不是 pending，未重复审批。",
            "path": str(target),
            "approval": current_approval,
        }

    frontmatter["approval"] = payload["status"]
    if payload.get("return_stage"):
        frontmatter["return_stage"] = payload["return_stage"]
    else:
        frontmatter.pop("return_stage", None)

    cleaned_body = remove_existing_approval_section(body)
    new_text = render_frontmatter(frontmatter) + "\n" + cleaned_body + "\n\n" + render_approval_section(payload)
    target.write_text(new_text, encoding="utf-8")
    index_result = rebuild_index_if_available(project)

    return {
        "updated": True,
        "reason": None,
        "message": "审批结论已记录。",
        "path": str(target),
        "index": index_result,
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Update a Ruyi test document with an approval decision.")
    parser.add_argument("--project", required=True, help="Project root path")
    parser.add_argument("--module", required=True, help="Module slug")
    parser.add_argument("--feature", required=True, help="Feature slug")
    parser.add_argument("--date", required=True, help="Contract date, YYYY-MM-DD")
    parser.add_argument("--status", required=True, choices=APPROVAL_STATUSES, help="Approval status")
    parser.add_argument("--reason", required=True, help="Approval reason")
    parser.add_argument("--return-stage", choices=RETURN_STAGES, help="Return stage for non-approved decisions")
    parser.add_argument("--follow-up", help="Follow-up action")
    args = parser.parse_args(argv)

    payload = {
        "module": args.module,
        "feature": args.feature,
        "date": args.date,
        "status": args.status,
        "reason": args.reason,
        "return_stage": args.return_stage,
        "follow_up": args.follow_up,
    }
    output = json.dumps(update_approval(args.project, payload), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
