from __future__ import annotations

import argparse
import json
from pathlib import Path

from merge_common import parse_frontmatter_text, section_bullets


def preview_merge(project_path: str | Path, candidate_path: str | Path) -> dict:
    project = Path(project_path)
    candidate = Path(candidate_path)
    frontmatter, body = parse_frontmatter_text(candidate.read_text(encoding="utf-8"))
    target_spec = frontmatter.get("target_spec")
    target = project / ".ruyi" / "spec" / target_spec if target_spec else None
    proposals = section_bullets(body, "沉淀建议")
    return {
        "candidate": str(candidate),
        "target_spec": str(target) if target else None,
        "target_exists": bool(target and target.is_file()),
        "proposals": proposals,
        "preview": "\n".join(f"- {item}" for item in proposals),
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Preview a Ruyi spec candidate merge.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args(argv)
    output = json.dumps(preview_merge(args.project, args.candidate), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
