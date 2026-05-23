"""Create a Ruyi implementation task for a confirmed plan."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


TASK_STATUSES = ("pending", "in-progress", "done")
PLAN_READY_STATUSES = ("confirmed",)
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TASK_FILE_PATTERN = re.compile(r"^task-(\d{2})\.md$")


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
        "status",
        "goal",
        "scope",
        "write_scope",
        "steps",
        "completion",
    )
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")

    validate_slug("module", payload["module"])
    validate_slug("feature", payload["feature"])

    if not DATE_PATTERN.match(payload["date"]):
        raise ValueError("date must use YYYY-MM-DD")
    if payload["status"] not in TASK_STATUSES:
        raise ValueError(f"status must be one of: {', '.join(TASK_STATUSES)}")
    if not as_list(payload["scope"]):
        raise ValueError("scope must include at least one item")
    if not as_list(payload["write_scope"]):
        raise ValueError("write_scope must include at least one item")
    if not as_list(payload["steps"]):
        raise ValueError("steps must include at least one item")
    if not as_list(payload["completion"]):
        raise ValueError("completion must include at least one item")
    if payload["status"] == "done" and not as_list(payload.get("self_review")):
        raise ValueError("done task must include self_review")


def is_initialized(project: Path) -> bool:
    return (project / ".ruyirc").is_file() and (project / ".ruyi").is_dir()


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


def task_dir(project: Path, payload: dict[str, Any]) -> Path:
    return project / ".ruyi" / "tasks" / payload["module"] / payload["feature"] / payload["date"]


def next_task_path(project: Path, payload: dict[str, Any]) -> Path:
    directory = task_dir(project, payload)
    existing_numbers: list[int] = []
    if directory.exists():
        for item in directory.iterdir():
            match = TASK_FILE_PATTERN.match(item.name)
            if match:
                existing_numbers.append(int(match.group(1)))

    number = max(existing_numbers, default=0) + 1
    return directory / f"task-{number:02d}.md"


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


def render_task(payload: dict[str, Any]) -> str:
    contract = f".ruyi/contracts/{payload['module']}/{payload['feature']}/{payload['date']}.md"
    plan = f".ruyi/plans/{payload['module']}/{payload['feature']}/{payload['date']}.md"
    preconditions = as_list(payload.get("preconditions")) or ["暂无。"]
    risks = as_list(payload.get("risks")) or ["暂无。"]
    self_review = as_list(payload.get("self_review")) or ["任务未完成时暂不填写。"]

    frontmatter_lines = "\n".join(
        line
        for line in [
            f"status: {payload['status']}",
            f"contract: {contract}",
            f"plan: {plan}",
        ]
        if line
    )

    return f"""---
{frontmatter_lines}
---

# Task：{payload["title"]}

## 目标

{payload["goal"]}

## 范围

{bullet_list(as_list(payload["scope"]))}

## 写入边界

{bullet_list(as_list(payload["write_scope"]))}

## 前置条件

{bullet_list(preconditions)}

## 执行步骤

{bullet_list(as_list(payload["steps"]))}

## 风险与关注点

{bullet_list(risks)}

## 完成标准

{bullet_list(as_list(payload["completion"]))}

## 当前进度

- 状态：{payload["status"]}
- 下一步：按执行步骤继续。

## 本地自检记录

{bullet_list(self_review)}
"""


def create_task(project_path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    project = Path(project_path)
    validate_payload(payload)

    if not is_initialized(project):
        return {
            "created": False,
            "reason": "project-not-initialized",
            "message": "项目未初始化 Ruyi，不能创建 task。",
            "path": None,
        }

    contract = contract_path(project, payload)
    if not contract.is_file():
        return {
            "created": False,
            "reason": "contract-not-found",
            "message": "对应 contract 不存在，不能创建 task。",
            "path": None,
            "contract": str(contract),
        }

    plan = plan_path(project, payload)
    if not plan.is_file():
        return {
            "created": False,
            "reason": "plan-not-found",
            "message": "对应 plan 不存在，不能创建 task。",
            "path": None,
            "plan": str(plan),
        }

    plan_status = parse_frontmatter(plan).get("status")
    if plan_status not in PLAN_READY_STATUSES:
        return {
            "created": False,
            "reason": "plan-not-confirmed",
            "message": "plan 未确认，不能创建 task。",
            "path": None,
            "plan": str(plan),
        }

    target = next_task_path(project, payload)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_task(payload), encoding="utf-8")
    return {
        "created": True,
        "reason": None,
        "message": "task 已创建。",
        "path": str(target),
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Create a Ruyi implementation task.")
    parser.add_argument("--project", required=True, help="Project root path")
    parser.add_argument("--module", required=True, help="Module slug")
    parser.add_argument("--feature", required=True, help="Feature slug")
    parser.add_argument("--date", required=True, help="Contract date, YYYY-MM-DD")
    parser.add_argument("--title", required=True, help="Task title")
    parser.add_argument("--status", default="pending", choices=TASK_STATUSES, help="Task status")
    parser.add_argument("--goal", required=True, help="Task goal")
    parser.add_argument("--scope", action="append", required=True, help="Task scope item")
    parser.add_argument("--write-scope", action="append", required=True, help="Task write scope item")
    parser.add_argument("--precondition", action="append", default=[], help="Task precondition")
    parser.add_argument("--step", action="append", required=True, help="Implementation step")
    parser.add_argument("--risk", action="append", default=[], help="Risk or concern")
    parser.add_argument("--completion", action="append", required=True, help="Completion criterion")
    parser.add_argument("--self-review", action="append", default=[], help="Implementation self-review or code review conclusion")
    args = parser.parse_args(argv)

    payload = {
        "module": args.module,
        "feature": args.feature,
        "date": args.date,
        "title": args.title,
        "status": args.status,
        "goal": args.goal,
        "scope": args.scope,
        "write_scope": args.write_scope,
        "preconditions": args.precondition,
        "steps": args.step,
        "risks": args.risk,
        "completion": args.completion,
        "self_review": args.self_review,
    }
    output = json.dumps(create_task(args.project, payload), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
