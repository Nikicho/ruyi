"""Reopen an approved Ruyi delivery in its existing formal artifact paths."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


RETURN_STAGES = ("contract", "plan", "implement", "test")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def artifact_path(project: Path, section: str, payload: dict[str, Any]) -> Path:
    return project / ".ruyi" / section / payload["module"] / payload["feature"] / f"{payload['date']}.md"


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def set_frontmatter_value(text: str, key: str, value: str) -> str:
    pattern = rf"^{re.escape(key)}:\s*.*$"
    if re.search(pattern, text, re.MULTILINE):
        return re.sub(pattern, f"{key}: {value}", text, count=1, flags=re.MULTILINE)
    end = text.find("\n---\n", 4)
    return text[:end] + f"\n{key}: {value}" + text[end:]


def remove_frontmatter_values(text: str, keys: tuple[str, ...]) -> str:
    for key in keys:
        text = re.sub(rf"^{re.escape(key)}:\s*.*\n?", "", text, count=1, flags=re.MULTILINE)
    return text


def append_record(text: str, heading: str, lines: list[str]) -> str:
    record = f"\n\n## {heading}\n\n" + "\n".join(f"- {line}" for line in lines) + "\n"
    return text.rstrip() + record


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


def validate_payload(payload: dict[str, Any]) -> None:
    for key in ("module", "feature", "date", "reason", "return_stage"):
        if not payload.get(key):
            raise ValueError(f"missing required field: {key}")
    for key in ("module", "feature"):
        if not SLUG_PATTERN.match(str(payload[key])):
            raise ValueError(f"{key} must use lowercase letters, numbers, and hyphens")
    if not DATE_PATTERN.match(str(payload["date"])):
        raise ValueError("date must use YYYY-MM-DD")
    if payload["return_stage"] not in RETURN_STAGES:
        raise ValueError(f"return_stage must be one of: {', '.join(RETURN_STAGES)}")


def reopen_delivery(project_path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    project = Path(project_path)
    validate_payload(payload)
    contract = artifact_path(project, "contracts", payload)
    test = artifact_path(project, "tests", payload)
    if not contract.is_file() or not test.is_file():
        return {"updated": False, "reason": "approved-delivery-not-found", "path": str(contract)}
    contract_text = contract.read_text(encoding="utf-8")
    test_text = test.read_text(encoding="utf-8")
    if parse_frontmatter(contract_text).get("status") != "confirmed" or parse_frontmatter(test_text).get("approval") != "approved":
        return {"updated": False, "reason": "delivery-not-approved", "path": str(contract)}

    changed_on = date.today().isoformat()
    record = [f"{changed_on}：审批后返工重开", f"原因：{payload['reason']}", f"返回阶段：{payload['return_stage']}"]
    contract_text = set_frontmatter_value(contract_text, "status", "reopened")
    contract.write_text(append_record(contract_text, "返工记录", record), encoding="utf-8")
    updated = [str(contract.relative_to(project).as_posix())]

    plan = artifact_path(project, "plans", payload)
    if plan.is_file() and payload["return_stage"] in ("contract", "plan", "implement"):
        plan_text = set_frontmatter_value(plan.read_text(encoding="utf-8"), "status", "draft")
        plan.write_text(append_record(plan_text, "状态变更记录", record), encoding="utf-8")
        updated.append(str(plan.relative_to(project).as_posix()))

    if test.is_file():
        test_text = set_frontmatter_value(test.read_text(encoding="utf-8"), "result", "pending")
        test_text = set_frontmatter_value(test_text, "approval", "pending")
        test_text = remove_frontmatter_values(test_text, ("return_stage", "condition"))
        test.write_text(append_record(test_text, "状态变更记录", record), encoding="utf-8")
        updated.append(str(test.relative_to(project).as_posix()))

    return {
        "updated": True,
        "reason": None,
        "updated_files": updated,
        "index": rebuild_index_if_available(project),
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Reopen an approved Ruyi delivery.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--module", required=True)
    parser.add_argument("--feature", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--return-stage", required=True, choices=RETURN_STAGES)
    args = parser.parse_args(argv)
    payload = {
        "module": args.module,
        "feature": args.feature,
        "date": args.date,
        "reason": args.reason,
        "return_stage": args.return_stage,
    }
    output = json.dumps(reopen_delivery(args.project, payload), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
