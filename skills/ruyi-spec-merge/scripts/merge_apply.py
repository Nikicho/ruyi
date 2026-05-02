from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from merge_common import archive_path, parse_frontmatter_text, render_frontmatter, section_bullets


DECISIONS = ("merged", "rejected", "superseded")


def candidate_relative_path(project: Path, candidate: Path) -> Path:
    return candidate.relative_to(project / ".ruyi" / "spec-candidates")


def patch_path(project: Path, candidate: Path) -> Path:
    rel = candidate_relative_path(project, candidate)
    return project / ".ruyi" / "spec-patches" / rel.with_suffix(".patch.md")


def render_manual_patch(
    *,
    project: Path,
    candidate: Path,
    target_layer: str | None,
    target_spec: str | None,
    proposals: list[str],
    reason: str,
) -> str:
    source = ".ruyi/spec-candidates/" + candidate_relative_path(project, candidate).as_posix()
    proposal_lines = "\n".join(f"- {item}" for item in proposals)
    target = f".ruyi/spec/{target_spec}" if target_layer == "project" else str(target_spec or "")
    return f"""---
source_candidate: {source}
target_layer: {target_layer or ""}
target_spec: {target_spec or ""}
decision: merged
status: pending-manual-merge
reason: {reason}
---

# Ruyi Spec Patch

## 目标

- 目标层级：{target_layer or ""}
- 目标 Spec：{target}
- 候选来源：{source}

## 建议补丁

以下内容来自 candidate 的“沉淀建议”，需要用户或维护者人工评估后合入目标 spec：

{proposal_lines}

## 操作要求

- 不要自动写入正式 spec。
- 人工确认后，只合入可长期复用的规则或事实。
- 合入后可保留本 patch 作为审计记录，或按团队约定归档。
"""


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
    generated_patch: Path | None = None
    if decision == "merged" and target_layer == "project":
        proposals = section_bullets(body, "沉淀建议")
        if not proposals:
            return {"updated": False, "reason": "proposal-not-found", "path": str(candidate)}
        generated_patch = patch_path(project, candidate)
        generated_patch.parent.mkdir(parents=True, exist_ok=True)
        generated_patch.write_text(
            render_manual_patch(
                project=project,
                candidate=candidate,
                target_layer=target_layer,
                target_spec=target_spec,
                proposals=proposals,
                reason=reason,
            ),
            encoding="utf-8",
        )

    frontmatter["status"] = decision
    frontmatter["merge_reason"] = reason
    if generated_patch is not None:
        frontmatter["patch"] = ".ruyi/spec-patches/" + generated_patch.relative_to(project / ".ruyi" / "spec-patches").as_posix()
    archived = archive_path(project, candidate, decision)
    archived.parent.mkdir(parents=True, exist_ok=True)
    archived.write_text(render_frontmatter(frontmatter) + "\n" + body.lstrip(), encoding="utf-8")
    candidate.unlink()
    index_result = rebuild_index_if_available(project)
    result = {"updated": True, "decision": decision, "archive": str(archived), "index": index_result}
    if generated_patch is not None:
        result["patch"] = str(generated_patch)
    return result


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
