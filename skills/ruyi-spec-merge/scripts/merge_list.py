from __future__ import annotations

import argparse
import json
from pathlib import Path

from merge_common import PENDING_STATUSES, candidate_files, parse_frontmatter_text


def list_candidates(project_path: str | Path) -> dict:
    project = Path(project_path)
    items = []
    for path in candidate_files(project):
        frontmatter, _ = parse_frontmatter_text(path.read_text(encoding="utf-8"))
        status = frontmatter.get("status", "")
        if status in PENDING_STATUSES:
            items.append(
                {
                    "path": str(path),
                    "target_layer": frontmatter.get("target_layer"),
                    "target_spec": frontmatter.get("target_spec"),
                    "status": status or "pending",
                }
            )
    return {"candidates": items}


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="List pending Ruyi spec candidates.")
    parser.add_argument("--project", required=True)
    args = parser.parse_args(argv)
    output = json.dumps(list_candidates(args.project), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
