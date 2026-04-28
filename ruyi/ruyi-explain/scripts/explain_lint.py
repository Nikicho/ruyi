"""Lint a Ruyi explain document against its test evidence."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def validate_slug(name: str, value: str) -> None:
    if not SLUG_PATTERN.match(value):
        raise ValueError(f"{name} must use lowercase letters, numbers, and hyphens: {value}")


def validate_payload(payload: dict[str, Any]) -> None:
    required = ("module", "feature", "date")
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    validate_slug("module", payload["module"])
    validate_slug("feature", payload["feature"])
    if not DATE_PATTERN.match(payload["date"]):
        raise ValueError("date must use YYYY-MM-DD")


def explain_path(project: Path, payload: dict[str, Any]) -> Path:
    return project / ".ruyi" / "explain" / payload["module"] / payload["feature"] / f"{payload['date']}.md"


def test_path(project: Path, payload: dict[str, Any]) -> Path:
    return project / ".ruyi" / "tests" / payload["module"] / payload["feature"] / f"{payload['date']}.md"


def section_lines(text: str, heading: str) -> list[str]:
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return []
    next_heading = text.find("\n## ", start + len(marker))
    section = text[start + len(marker) : next_heading if next_heading != -1 else len(text)]
    return [line.strip()[2:].strip() for line in section.splitlines() if line.strip().startswith("- ")]


def lint_explain(project_path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    project = Path(project_path)
    validate_payload(payload)

    explain = explain_path(project, payload)
    test = test_path(project, payload)
    if not explain.is_file():
        return {"ok": False, "reason": "explain-not-found", "path": str(explain), "violations": []}
    if not test.is_file():
        return {"ok": False, "reason": "test-not-found", "path": str(test), "violations": []}

    explain_text = explain.read_text(encoding="utf-8")
    test_text = test.read_text(encoding="utf-8")
    risks = section_lines(explain_text, "风险与遗留问题")
    violations = [
        item
        for item in risks
        if item
        and item not in ("暂无。", "暂无")
        and "待确认" not in item
        and item not in test_text
    ]
    return {
        "ok": not violations,
        "reason": None if not violations else "risk-not-backed-by-test",
        "path": str(explain),
        "violations": violations,
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Lint a Ruyi explain against test evidence.")
    parser.add_argument("--project", required=True, help="Project root path")
    parser.add_argument("--module", required=True, help="Module slug")
    parser.add_argument("--feature", required=True, help="Feature slug")
    parser.add_argument("--date", required=True, help="Contract date, YYYY-MM-DD")
    args = parser.parse_args(argv)

    payload = {"module": args.module, "feature": args.feature, "date": args.date}
    output = json.dumps(lint_explain(args.project, payload), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
