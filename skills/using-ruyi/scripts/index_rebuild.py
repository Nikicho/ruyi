"""Rebuild .ruyi/INDEX.md from formal Ruyi artifacts."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


SECTIONS = {
    "contracts": "contract",
    "plans": "plan",
    "tasks": "task",
    "tests": "test",
    "explain": "explain",
    "spec-candidates": "spec-candidate",
}


def artifact_identity(project: Path, path: Path) -> tuple[str, str, str, str] | None:
    rel = path.relative_to(project / ".ruyi")
    parts = rel.parts
    if len(parts) < 4:
        return None
    section = parts[0]
    if section not in SECTIONS:
        return None
    if section == "tasks" and len(parts) >= 5:
        module, feature, date = parts[1], parts[2], parts[3]
        return module, feature, date, SECTIONS[section]
    if len(parts) == 4:
        module, feature, filename = parts[1], parts[2], parts[3]
        return module, feature, Path(filename).stem, SECTIONS[section]
    return None


def rebuild_index(project_path: str | Path) -> dict:
    project = Path(project_path)
    ruyi = project / ".ruyi"
    if not ruyi.is_dir():
        return {"updated": False, "reason": "ruyi-not-found", "path": None}

    grouped: dict[str, dict[str, list[tuple[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for section in SECTIONS:
        root = ruyi / section
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*.md")):
            if path.name == "EXPECTED.md":
                continue
            identity = artifact_identity(project, path)
            if not identity:
                continue
            module, feature, date, kind = identity
            grouped[module][feature].append((date, kind))

    lines = ["# Ruyi Index", "", "> 自动生成，请勿手工编辑。", ""]
    for module in sorted(grouped):
        lines.extend([f"## 模块：{module}", ""])
        for feature in sorted(grouped[module]):
            lines.extend([f"### {feature}", ""])
            for date, kind in sorted(grouped[module][feature]):
                lines.append(f"- {date} {kind}")
            lines.append("")

    target = ruyi / "INDEX.md"
    target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"updated": True, "reason": None, "path": str(target)}


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Rebuild Ruyi INDEX.md.")
    parser.add_argument("--project", required=True)
    args = parser.parse_args(argv)
    output = json.dumps(rebuild_index(args.project), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
