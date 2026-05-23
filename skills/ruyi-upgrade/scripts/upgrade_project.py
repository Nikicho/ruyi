"""Upgrade an initialized Ruyi project to the current structural schema."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
from pathlib import Path
from typing import Any


CURRENT_SCHEMA_VERSION = 2
OBSOLETE_DIRS = (
    ".ruyi/workspace",
    ".ruyi/spec-archive",
    ".ruyi/spec-patches",
)
OBSOLETE_IGNORE_RULES = (
    ".ruyi/workspace/**",
    "!.ruyi/workspace/README.md",
    ".ruyi/spec-archive/**",
    ".ruyi/spec-patches/**",
)
LOCAL_IGNORE_RULES = (
    ".ruyi/tasks/**",
    ".ruyi/spec-candidates/**",
)


def schema_version(ruyirc_text: str) -> int:
    match = re.search(r"^schema_version:\s*(\d+)\s*$", ruyirc_text, re.MULTILINE)
    return int(match.group(1)) if match else 1


def write_schema_version(target: Path, text: str) -> bool:
    current = schema_version(text)
    if current > CURRENT_SCHEMA_VERSION:
        raise ValueError(f"project schema {current} is newer than supported schema {CURRENT_SCHEMA_VERSION}")
    if current == CURRENT_SCHEMA_VERSION and "schema_version:" in text:
        return False
    if re.search(r"^schema_version:\s*\d+\s*$", text, re.MULTILINE):
        updated = re.sub(
            r"^schema_version:\s*\d+\s*$",
            f"schema_version: {CURRENT_SCHEMA_VERSION}",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        updated = f"schema_version: {CURRENT_SCHEMA_VERSION}\n\n{text.lstrip()}"
    target.write_text(updated, encoding="utf-8")
    return True


def update_gitignore(target: Path) -> bool:
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    lines = existing.splitlines()
    kept = [line for line in lines if line not in OBSOLETE_IGNORE_RULES]
    for rule in LOCAL_IGNORE_RULES:
        if rule not in kept:
            kept.append(rule)
    updated = "\n".join(kept).rstrip() + "\n"
    if updated == existing:
        return False
    target.write_text(updated, encoding="utf-8")
    return True


def find_manual_review(project: Path) -> list[str]:
    results: list[str] = []
    contracts = project / ".ruyi" / "contracts"
    if contracts.is_dir():
        for path in contracts.rglob("*.md"):
            if "derived_from:" in path.read_text(encoding="utf-8"):
                results.append(f"{path.relative_to(project).as_posix()}: derived_from 需判断是否属于返工重开")
    explains = project / ".ruyi" / "explain"
    if explains.is_dir():
        for path in explains.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            if "approval: conditionally-approved" in text or "approval: rejected" in text:
                results.append(f"{path.relative_to(project).as_posix()}: 旧审批状态需人工决策")
    return sorted(results)


def rebuild_index(project: Path) -> dict[str, Any] | None:
    script = Path(__file__).resolve().parents[2] / "using-ruyi" / "scripts" / "index_rebuild.py"
    if not script.is_file():
        return None
    spec = importlib.util.spec_from_file_location("ruyi_index_rebuild", script)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.rebuild_index(project)


def upgrade_project(project_path: str | Path, *, remove_obsolete: bool = False) -> dict[str, Any]:
    """Upgrade deterministic Ruyi structure without changing business semantics."""
    project = Path(project_path)
    ruyirc = project / ".ruyirc"
    ruyi = project / ".ruyi"
    if not ruyirc.is_file() or not ruyi.is_dir():
        raise ValueError("project is not initialized with .ruyirc and .ruyi")

    ruyirc_text = ruyirc.read_text(encoding="utf-8")
    from_schema = schema_version(ruyirc_text)
    updated: list[str] = []
    if write_schema_version(ruyirc, ruyirc_text):
        updated.append(".ruyirc")
    if update_gitignore(project / ".gitignore"):
        updated.append(".gitignore")

    obsolete_dirs = [relative for relative in OBSOLETE_DIRS if (project / relative).is_dir()]
    deleted: list[str] = []
    if remove_obsolete:
        for relative in obsolete_dirs:
            shutil.rmtree(project / relative)
            deleted.append(relative)

    index_result = rebuild_index(project)
    if index_result and index_result.get("updated"):
        updated.append(".ruyi/INDEX.md")

    return {
        "from_schema": from_schema,
        "to_schema": CURRENT_SCHEMA_VERSION,
        "updated": updated,
        "obsolete_dirs": [] if remove_obsolete else obsolete_dirs,
        "deleted": deleted,
        "manual_review": find_manual_review(project),
        "index": index_result,
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Upgrade a Ruyi project schema.")
    parser.add_argument("--project", required=True, help="Initialized project root")
    parser.add_argument("--remove-obsolete", action="store_true", help="Delete reported obsolete Ruyi directories")
    args = parser.parse_args(argv)
    output = json.dumps(
        upgrade_project(args.project, remove_obsolete=args.remove_obsolete),
        ensure_ascii=False,
        indent=2,
    )
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
