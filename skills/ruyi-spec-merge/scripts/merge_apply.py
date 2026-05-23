from __future__ import annotations

import argparse
import json
from pathlib import Path

from merge_common import parse_frontmatter_text


DECISIONS = ("merged", "deleted")


def apply_merge(project_path: str | Path, candidate_path: str | Path, decision: str, reason: str) -> dict:
    if decision not in DECISIONS:
        raise ValueError(f"decision must be one of: {', '.join(DECISIONS)}")
    if not reason.strip():
        raise ValueError("reason is required")

    project = Path(project_path)
    candidate = Path(candidate_path)
    if not candidate.is_file():
        return {"updated": False, "reason": "candidate-not-found", "path": str(candidate)}
    frontmatter, _body = parse_frontmatter_text(candidate.read_text(encoding="utf-8"))
    status = frontmatter.get("status", "pending")
    if status not in ("pending", "candidate", ""):
        return {"updated": False, "reason": "candidate-not-pending", "path": str(candidate), "status": status}

    target_layer = frontmatter.get("target_layer")
    target_spec = frontmatter.get("target_spec")
    target: Path | None = None
    if decision == "merged" and target_layer == "project":
        target = project / ".ruyi" / "spec" / str(target_spec or "")
        if not target.is_file():
            return {
                "updated": False,
                "reason": "formal-spec-not-updated",
                "path": str(candidate),
                "target": str(target),
            }

    candidate.unlink()
    return {
        "updated": True,
        "decision": decision,
        "reason": reason,
        "deleted_candidate": str(candidate),
        "target": str(target) if target else None,
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Resolve a local Ruyi spec candidate after review.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--decision", required=True, choices=DECISIONS)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args(argv)
    output = json.dumps(apply_merge(args.project, args.candidate, args.decision, args.reason), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
