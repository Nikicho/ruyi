"""Compatibility notice for the deprecated Ruyi explain lint stage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEPRECATED_REASON = "deprecated-in-schema-v3"


def lint_explain(project_path: str | Path, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    _ = Path(project_path)
    _ = payload or {}
    return {
        "ok": False,
        "reason": DEPRECATED_REASON,
        "message": "Ruyi schema v3 不再 lint explain；请检查 test 的验收证据与 approval 状态。",
        "path": None,
        "violations": [],
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Deprecated: Ruyi schema v3 no longer lints explain documents.")
    parser.add_argument("--project", required=True, help="Project root path")
    parser.add_argument("--module", help="Module slug")
    parser.add_argument("--feature", help="Feature slug")
    parser.add_argument("--date", help="Contract date, YYYY-MM-DD")
    args = parser.parse_args(argv)

    payload = {"module": args.module, "feature": args.feature, "date": args.date}
    output = json.dumps(lint_explain(args.project, payload), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
