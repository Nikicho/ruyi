"""Create a Ruyi test result document without overwriting existing files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


RESULT_TYPES = ("passed", "passed-with-notes", "failed")
PLAN_READY_STATUSES = ("confirmed",)
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
    required = ("module", "feature", "date", "title", "result", "methods", "evidence", "acceptance_results", "conclusion")
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")

    validate_slug("module", payload["module"])
    validate_slug("feature", payload["feature"])

    if not DATE_PATTERN.match(payload["date"]):
        raise ValueError("date must use YYYY-MM-DD")
    if payload["result"] not in RESULT_TYPES:
        raise ValueError(f"result must be one of: {', '.join(RESULT_TYPES)}")
    if not as_list(payload["methods"]):
        raise ValueError("methods must include at least one item")
    if not as_list(payload["evidence"]):
        raise ValueError("evidence must include at least one item")
    if not as_list(payload["acceptance_results"]):
        raise ValueError("acceptance_results must include at least one item")
    if payload["result"] in ("failed", "passed-with-notes") and not as_list(payload.get("risks")):
        raise ValueError("failed or passed-with-notes result must include risks or uncovered items")
    if payload["result"] == "failed" and not as_list(payload.get("failures")):
        raise ValueError("failed result must include at least one failure item")


def is_initialized(project: Path) -> bool:
    return (project / ".ruyirc").is_file() and (project / ".ruyi" / "tests").is_dir()


def contract_path(project: Path, payload: dict[str, Any]) -> Path:
    return (
        project
        / ".ruyi"
        / "contracts"
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


def test_path(project: Path, payload: dict[str, Any]) -> Path:
    return (
        project
        / ".ruyi"
        / "tests"
        / payload["module"]
        / payload["feature"]
        / f"{payload['date']}.md"
    )


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


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


def render_test_result(payload: dict[str, Any]) -> str:
    contract = f".ruyi/contracts/{payload['module']}/{payload['feature']}/{payload['date']}.md"
    plan = f".ruyi/plans/{payload['module']}/{payload['feature']}/{payload['date']}.md"
    risks = as_list(payload.get("risks")) or ["暂无。"]
    failures = as_list(payload.get("failures")) or ["暂无。"]
    ui_automation = as_list(payload.get("ui_automation")) or ["未执行 UI 自动化；原因待说明。"]

    return f"""---
contract: {contract}
plan: {plan}
module: {payload["module"]}
feature: {payload["feature"]}
date: {payload["date"]}
result: {payload["result"]}
---

# Test：{payload["title"]}

## 验证对象

{payload.get("target") or f"对应 contract：`{contract}`。"}

## 验证方式

{bullet_list(as_list(payload["methods"]))}

## UI 自动化验证

{bullet_list(ui_automation)}

## 验证证据

{bullet_list(as_list(payload["evidence"]))}

## 与验收标准对照

{bullet_list(as_list(payload["acceptance_results"]))}

## 失败项

{bullet_list(failures)}

## 风险与未覆盖项

{bullet_list(risks)}

## 结论

{payload["conclusion"]}
"""


def create_test_result(project_path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    project = Path(project_path)
    validate_payload(payload)

    if not is_initialized(project):
        return {
            "created": False,
            "reason": "project-not-initialized",
            "message": "项目未初始化 Ruyi，不能正式创建 test。",
            "path": None,
        }

    contract = contract_path(project, payload)
    if not contract.is_file():
        return {
            "created": False,
            "reason": "contract-not-found",
            "message": "对应 contract 不存在，不能创建 test。",
            "path": None,
            "contract": str(contract),
        }

    plan = plan_path(project, payload)
    if not plan.is_file():
        return {
            "created": False,
            "reason": "plan-not-found",
            "message": "对应 plan 不存在，不能创建 test。",
            "path": None,
            "plan": str(plan),
        }

    plan_status = parse_frontmatter(plan).get("status")
    if plan_status not in PLAN_READY_STATUSES:
        return {
            "created": False,
            "reason": "plan-not-confirmed",
            "message": "plan 未确认，不能创建 test。",
            "path": None,
            "plan": str(plan),
        }

    target = test_path(project, payload)
    if target.exists():
        return {
            "created": False,
            "reason": "already-exists",
            "message": "test 已存在，未覆盖。",
            "path": str(target),
        }

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_test_result(payload), encoding="utf-8")
    return {
        "created": True,
        "reason": None,
        "message": "test 已创建。",
        "path": str(target),
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Create a Ruyi test result document.")
    parser.add_argument("--project", required=True, help="Project root path")
    parser.add_argument("--module", required=True, help="Module slug")
    parser.add_argument("--feature", required=True, help="Feature slug")
    parser.add_argument("--date", required=True, help="Contract date, YYYY-MM-DD")
    parser.add_argument("--title", required=True, help="Test result display title")
    parser.add_argument("--result", required=True, choices=RESULT_TYPES, help="Verification result")
    parser.add_argument("--target", help="Verification target summary")
    parser.add_argument("--method", action="append", required=True, help="Verification method")
    parser.add_argument("--ui-automation", action="append", default=[], help="UI automation evidence or non-automation reason")
    parser.add_argument("--evidence", action="append", required=True, help="Verification evidence")
    parser.add_argument("--acceptance-result", action="append", required=True, help="Acceptance criterion result")
    parser.add_argument("--failure", action="append", default=[], help="Failure item")
    parser.add_argument("--risk", action="append", default=[], help="Risk or uncovered item")
    parser.add_argument("--conclusion", required=True, help="Verification conclusion")
    args = parser.parse_args(argv)

    payload = {
        "module": args.module,
        "feature": args.feature,
        "date": args.date,
        "title": args.title,
        "result": args.result,
        "target": args.target,
        "methods": args.method,
        "ui_automation": args.ui_automation,
        "evidence": args.evidence,
        "acceptance_results": args.acceptance_result,
        "failures": args.failure,
        "risks": args.risk,
        "conclusion": args.conclusion,
    }
    output = json.dumps(create_test_result(args.project, payload), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
