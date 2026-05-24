"""Rebuild .ruyi/INDEX.md from formal Ruyi artifacts."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SECTIONS = {
    "contracts": "contract",
    "plans": "plan",
    "tests": "test",
}


def artifact_identity(project: Path, path: Path) -> tuple[str, str, str, str] | None:
    rel = path.relative_to(project / ".ruyi")
    parts = rel.parts
    if len(parts) < 4:
        return None
    section = parts[0]
    if section not in SECTIONS:
        return None
    if len(parts) == 4:
        module, feature, filename = parts[1], parts[2], parts[3]
        return module, feature, Path(filename).stem, SECTIONS[section]
    return None


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def section_text(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return ""
    body_start = text.find("\n", start)
    if body_start == -1:
        return ""
    next_heading = text.find("\n## ", body_start + 1)
    if next_heading == -1:
        return text[body_start:].strip()
    return text[body_start:next_heading].strip()


def first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped.removeprefix("- ").strip()
    return ""


def contract_summary(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)
    business_rules = section_text(text, "业务规则")
    goal = frontmatter.get("goal", "")
    if not goal:
        for line in business_rules.splitlines():
            stripped = line.strip()
            if stripped.startswith("- 业务目标："):
                goal = stripped.split("：", 1)[1].strip()
                break
    if not goal:
        goal = first_non_empty_line(section_text(text, "用户故事"))
    return {
        "goal": goal or "待补充",
        "type": frontmatter.get("type", "待补充"),
        "size": frontmatter.get("size", ""),
        "requirement_status": frontmatter.get("status", "待补充"),
        "superseded_by": frontmatter.get("superseded_by", ""),
    }


def test_summary(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
    return {
        "verification_status": frontmatter.get("result", ""),
        "approval_status": frontmatter.get("approval", ""),
    }


def status_rank(status: str) -> int:
    ranks = {
        "approved": 90,
        "completed": 70,
        "confirmed": 60,
        "reopened": 55,
        "passed": 50,
        "pending": 20,
        "draft": 10,
        "待补充": 0,
    }
    return ranks.get(status, 0)


def merge_feature_meta(current: dict[str, str], candidate: dict[str, str]) -> dict[str, str]:
    if not current:
        return candidate
    if candidate.get("goal") and current.get("goal") in ("", "待补充"):
        current["goal"] = candidate["goal"]
    if candidate.get("type") and current.get("type") in ("", "待补充"):
        current["type"] = candidate["type"]
    if candidate.get("size") and not current.get("size"):
        current["size"] = candidate["size"]
    for key in ("requirement_status", "verification_status", "approval_status"):
        if candidate.get(key) and status_rank(candidate.get(key, "")) >= status_rank(current.get(key, "")):
            current[key] = candidate[key]
    for key in ("superseded_by",):
        if candidate.get(key):
            current[key] = candidate[key]
    return current


def rebuild_index(project_path: str | Path) -> dict:
    project = Path(project_path)
    ruyi = project / ".ruyi"
    if not ruyi.is_dir():
        return {"updated": False, "reason": "ruyi-not-found", "path": None}

    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(
        lambda: defaultdict(lambda: {"artifacts": defaultdict(list), "meta": {}})
    )
    warnings: list[str] = []
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
            grouped[module][feature]["artifacts"][date].append(kind)
            if section == "contracts":
                meta = contract_summary(path)
                grouped[module][feature]["meta"] = merge_feature_meta(grouped[module][feature]["meta"], meta)
                if meta.get("goal") == "待补充":
                    warnings.append(f"{module}/{feature}/{date} 缺少可抽取的业务目标")
            if section == "tests":
                grouped[module][feature]["meta"] = merge_feature_meta(
                    grouped[module][feature]["meta"],
                    test_summary(path),
                )

    lines = ["# Ruyi Index", "", "> 自动生成，请勿手工编辑。", ""]
    for module in sorted(grouped):
        lines.extend([f"## 模块：{module}", ""])
        for feature in sorted(grouped[module]):
            lines.extend([f"### {feature}", ""])
            meta = grouped[module][feature]["meta"] or {}
            type_text = meta.get("type") or "待补充"
            if meta.get("size"):
                type_text = f"{type_text}, size: {meta['size']}"
            lines.append(f"- 业务目标：{meta.get('goal') or '待补充'}")
            lines.append(f"- 类型：{type_text}")
            lines.append(f"- 需求状态：{meta.get('requirement_status') or '待补充'}")
            lines.append(f"- 验证状态：{meta.get('verification_status') or '待补充'}")
            lines.append(f"- 审批状态：{meta.get('approval_status') or '待补充'}")
            if meta.get("superseded_by"):
                lines.append(f"- 已被取代：{meta['superseded_by']}")
            for date in sorted(grouped[module][feature]["artifacts"]):
                kinds = " / ".join(sorted(set(grouped[module][feature]["artifacts"][date])))
                lines.append(f"- {date} {kinds}")
            lines.append("")

    target = ruyi / "INDEX.md"
    target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"updated": True, "reason": None, "path": str(target), "warnings": warnings}


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
