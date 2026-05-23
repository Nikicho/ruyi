from __future__ import annotations

from pathlib import Path


PENDING_STATUSES = ("pending", "candidate", "")


def parse_frontmatter_text(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data, text[end + len("\n---\n") :]


def section_bullets(text: str, heading: str) -> list[str]:
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return []
    next_heading = text.find("\n## ", start + len(marker))
    section = text[start + len(marker) : next_heading if next_heading != -1 else len(text)]
    return [line.strip()[2:].strip() for line in section.splitlines() if line.strip().startswith("- ")]


def candidate_files(project: Path) -> list[Path]:
    root = project / ".ruyi" / "spec-candidates"
    if not root.is_dir():
        return []
    return sorted(path for path in root.rglob("*.md") if path.name != "EXPECTED.md")
