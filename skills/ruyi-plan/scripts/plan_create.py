"""Create a Ruyi plan document without overwriting existing files."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


PLAN_STATUSES = ("draft", "confirmed", "blocked")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
OLD_TASK_DETAIL_MARKERS = ("目标：", "范围：", "写入边界", "完成条件", "步骤：")


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
        "solution",
        "architecture",
        "spec_constraints",
        "test_strategy",
        "tasks",
    )
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")

    validate_slug("module", payload["module"])
    validate_slug("feature", payload["feature"])

    if not DATE_PATTERN.match(payload["date"]):
        raise ValueError("date must use YYYY-MM-DD")
    if payload["status"] not in PLAN_STATUSES:
        raise ValueError(f"status must be one of: {', '.join(PLAN_STATUSES)}")
    if not as_list(payload["test_strategy"]):
        raise ValueError("test_strategy must include at least one item")
    if not as_list(payload["tasks"]):
        raise ValueError("tasks must include at least one item")
    invalid_tasks = [
        item
        for item in as_list(payload["tasks"])
        if any(marker in item for marker in OLD_TASK_DETAIL_MARKERS)
    ]
    if invalid_tasks:
        raise ValueError("task items must be title-only; detailed steps belong in local task checkpoints")


def contract_requires_data_interface(path: Path) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    marker = "## 接口范围"
    start = text.find(marker)
    if start == -1:
        return False
    body_start = text.find("\n", start)
    if body_start == -1:
        return False
    next_heading = text.find("\n## ", body_start + 1)
    body = text[body_start: next_heading if next_heading != -1 else None].strip()
    return bool(body and "本次不涉及接口" not in body)


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


def is_initialized(project: Path) -> bool:
    return (project / ".ruyirc").is_file() and (project / ".ruyi" / "plans").is_dir()


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


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def numbered_list(items: list[str]) -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1))


def plain_block(items: list[str]) -> str:
    return "\n".join(items)


def render_plan(payload: dict[str, Any]) -> str:
    contract = f".ruyi/contracts/{payload['module']}/{payload['feature']}/{payload['date']}.md"
    data_interface = as_list(payload.get("data_interface")) or ["本次不涉及接口变化。"]
    unresolved = as_list(payload.get("unresolved"))
    unresolved_section = ""
    if unresolved:
        unresolved_section = f"\n\n## 未决项\n\n{bullet_list(unresolved)}"

    return f"""---
status: {payload["status"]}
contract: {contract}
module: {payload["module"]}
feature: {payload["feature"]}
date: {payload["date"]}
---

# Plan：{payload["title"]}

## 方案概述

{plain_block(as_list(payload["solution"]))}

## 文件/模块架构

```text
{plain_block(as_list(payload["architecture"]))}
```

## 接口与数据

{bullet_list(data_interface)}

## Spec 约束

{bullet_list(as_list(payload["spec_constraints"]))}

## Task 拆分

{numbered_list(as_list(payload["tasks"]))}

## 验证策略

{bullet_list(as_list(payload["test_strategy"]))}{unresolved_section}
"""


def create_plan(project_path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    project = Path(project_path)
    validate_payload(payload)

    if not is_initialized(project):
        return {
            "created": False,
            "reason": "project-not-initialized",
            "message": "项目未初始化 Ruyi，不能正式创建 plan。",
            "path": None,
        }

    contract = contract_path(project, payload)
    if not contract.is_file():
        return {
            "created": False,
            "reason": "contract-not-found",
            "message": "对应 contract 不存在，不能创建 plan。",
            "path": None,
            "contract": str(contract),
        }

    contract_status = parse_frontmatter(contract).get("status")
    if contract_status != "confirmed":
        return {
            "created": False,
            "reason": "contract-not-confirmed",
            "message": "contract 未确认，不能创建 plan。",
            "path": None,
            "contract": str(contract),
        }
    if contract_requires_data_interface(contract) and not as_list(payload.get("data_interface")):
        return {
            "created": False,
            "reason": "data-interface-required",
            "message": "contract 存在接口范围，plan 必须包含接口与数据判断。",
            "path": None,
            "contract": str(contract),
        }

    target = plan_path(project, payload)
    if target.exists():
        existing = target.read_text(encoding="utf-8")
        if "status: draft" in existing and "## 状态变更记录" in existing:
            history_start = existing.find("\n## 状态变更记录")
            history = existing[history_start:] if history_start != -1 else ""
            target.write_text(render_plan(payload).rstrip() + "\n" + history, encoding="utf-8")
            return {
                "created": False,
                "updated": True,
                "reason": None,
                "message": "返工后的 plan 当前内容已更新。",
                "path": str(target),
                "index": rebuild_index_if_available(project),
            }
        return {
            "created": False,
            "reason": "already-exists",
            "message": "plan 已存在，未覆盖。",
            "path": str(target),
        }

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_plan(payload), encoding="utf-8")
    index_result = rebuild_index_if_available(project)
    return {
        "created": True,
        "reason": None,
        "message": "plan 已创建。",
        "path": str(target),
        "index": index_result,
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Create a Ruyi plan document.")
    parser.add_argument("--project", required=True, help="Project root path")
    parser.add_argument("--module", required=True, help="Module slug")
    parser.add_argument("--feature", required=True, help="Feature slug")
    parser.add_argument("--date", required=True, help="Contract date, YYYY-MM-DD")
    parser.add_argument("--title", required=True, help="Plan display title")
    parser.add_argument("--status", default="draft", choices=PLAN_STATUSES, help="Plan status")
    parser.add_argument("--solution", action="append", required=True, help="Architecture direction and key tradeoff")
    parser.add_argument("--architecture", action="append", required=True, help="File/module structure line")
    parser.add_argument("--data-interface", action="append", default=[], help="Minimal interface and data decision")
    parser.add_argument("--spec", action="append", required=True, help="Required spec with short label")
    parser.add_argument("--test-strategy", action="append", required=True, help="Test strategy item")
    parser.add_argument("--task", action="append", required=True, help="Task title only")
    parser.add_argument("--unresolved", action="append", default=[], help="Blocking unresolved item")
    args = parser.parse_args(argv)

    payload = {
        "module": args.module,
        "feature": args.feature,
        "date": args.date,
        "title": args.title,
        "status": args.status,
        "solution": args.solution,
        "architecture": args.architecture,
        "data_interface": args.data_interface,
        "spec_constraints": args.spec,
        "test_strategy": args.test_strategy,
        "tasks": args.task,
        "unresolved": args.unresolved,
    }
    output = json.dumps(create_plan(args.project, payload), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
