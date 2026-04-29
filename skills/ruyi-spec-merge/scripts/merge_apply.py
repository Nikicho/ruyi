from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from merge_common import archive_path, parse_frontmatter_text, render_frontmatter, section_bullets


DECISIONS = ("merged", "rejected", "superseded")


def rebuild_index_if_available(project: Path) -> dict | None:
    script = Path(__file__).resolve().parents[2] / "using-ruyi" / "scripts" / "index_rebuild.py"
    if not script.is_file():
        return None
    spec = importlib.util.spec_from_file_location("ruyi_index_rebuild", script)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.rebuild_index(project)


def apply_merge(project_path: str | Path, candidate_path: str | Path, decision: str, reason: str) -> dict:
    if decision not in DECISIONS:
        raise ValueError(f"decision must be one of: {', '.join(DECISIONS)}")
    if not reason.strip():
        raise ValueError("reason is required")

    project = Path(project_path)
    candidate = Path(candidate_path)
    if not candidate.is_file():
        return {"updated": False, "reason": "candidate-not-found", "path": str(candidate)}

    frontmatter, body = parse_frontmatter_text(candidate.read_text(encoding="utf-8"))
    status = frontmatter.get("status", "pending")
    if status not in ("pending", "candidate", ""):
        return {"updated": False, "reason": "candidate-not-pending", "path": str(candidate), "status": status}

    target_spec = frontmatter.get("target_spec")
    target_layer = frontmatter.get("target_layer")
    if decision == "merged" and target_layer == "project":
        target = project / ".ruyi" / "spec" / str(target_spec)
        proposals = section_bullets(body, "沉淀建议")
        if not proposals:
            return {"updated": False, "reason": "proposal-not-found", "path": str(candidate)}
        existing = target.read_text(encoding="utf-8") if target.exists() else ""
        addition = "\n\n## 候选合入\n\n" + "\n".join(f"- {item}" for item in proposals) + "\n"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(existing.rstrip() + addition, encoding="utf-8")

    frontmatter["status"] = decision
    frontmatter["merge_reason"] = reason
    archived = archive_path(project, candidate, decision)
    archived.parent.mkdir(parents=True, exist_ok=True)
    archived.write_text(render_frontmatter(frontmatter) + "\n" + body.lstrip(), encoding="utf-8")
    candidate.unlink()
    index_result = rebuild_index_if_available(project)
    return {"updated": True, "decision": decision, "archive": str(archived), "index": index_result}


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Apply a Ruyi spec candidate merge decision.")
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
