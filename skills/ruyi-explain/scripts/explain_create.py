"""Compatibility notice for the deprecated Ruyi explain stage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEPRECATED_REASON = "deprecated-in-schema-v3"


def create_explain(project_path: str | Path, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    _ = Path(project_path)
    _ = payload or {}
    return {
        "created": False,
        "updated": False,
        "reason": DEPRECATED_REASON,
        "message": "Ruyi schema v3 不再生成 explain；请使用 test 承载验证摘要，并由 approve 更新 test 审批状态。",
        "path": None,
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Deprecated: Ruyi schema v3 no longer creates explain documents.")
    parser.add_argument("--project", required=True, help="Project root path")
    parser.add_argument("--module", help="Module slug")
    parser.add_argument("--feature", help="Feature slug")
    parser.add_argument("--date", help="Contract date, YYYY-MM-DD")
    parser.add_argument("--title", help="Explain display title")
    parser.add_argument("--completed", action="append", default=[], help="Deprecated")
    parser.add_argument("--requirement-result", action="append", default=[], help="Deprecated")
    parser.add_argument("--verification", action="append", default=[], help="Deprecated")
    parser.add_argument("--code-quality", action="append", default=[], help="Deprecated")
    parser.add_argument("--code-quality-source", action="append", default=[], help="Deprecated")
    parser.add_argument("--risk", action="append", default=[], help="Deprecated")
    parser.add_argument("--technical-note", action="append", default=[], help="Deprecated")
    args = parser.parse_args(argv)

    payload = {
        "module": args.module,
        "feature": args.feature,
        "date": args.date,
        "title": args.title,
    }
    output = json.dumps(create_explain(args.project, payload), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
