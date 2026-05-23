"""Shared helpers for Ruyi init scripts."""

from __future__ import annotations

from pathlib import Path


FRONTEND_ROOT_FILES = ("package.json",)

SPEC_FILES = (
    "INDEX.md",
    "project-overview.md",
    "project-structure.md",
    "development-baseline.md",
    "coding-baseline.md",
    "testing-baseline.md",
    "api.md",
    "open-questions.md",
)

FULL_MIGRATION_SPEC_FILES = (
    "docs-registry.md",
    "interview-bank.md",
)

REQUIRED_RUYI_DIRS = (
    ".ruyi",
    ".ruyi/spec",
    ".ruyi/spec/references",
    ".ruyi/spec/references/shared",
    ".ruyi/spec/references/modules",
    ".ruyi/contracts",
    ".ruyi/plans",
    ".ruyi/tests",
    ".ruyi/explain",
)

REQUIRED_RUYI_FILES = (
    ".ruyirc",
    ".ruyi/README.md",
    ".ruyi/INDEX.md",
    ".ruyi/project-actions.md",
    "CLAUDE.md",
    ".claude/settings.json",
    ".claude/commands/ruyi.md",
    *tuple(f".ruyi/spec/{name}" for name in SPEC_FILES),
)

LOCAL_GITIGNORE_RULES = (
    ".ruyi/tasks/**",
    ".ruyi/spec-candidates/**",
)


def read_text(path: str | Path) -> str:
    """Read UTF-8 text."""
    return Path(path).read_text(encoding="utf-8")


def ensure_dir(path: str | Path) -> bool:
    """Create a directory if missing. Return True when created."""
    directory = Path(path)
    existed = directory.is_dir()
    directory.mkdir(parents=True, exist_ok=True)
    return not existed


def write_if_missing(path: str | Path, content: str) -> bool:
    """Write UTF-8 content only when the file does not already exist."""
    target = Path(path)
    if target.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return True


def append_gitignore_rules(path: str | Path) -> bool:
    """Append Ruyi local runtime ignore rules if they are absent."""
    target = Path(path)
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    lines = existing.splitlines()
    missing = [rule for rule in LOCAL_GITIGNORE_RULES if rule not in lines]
    if not missing:
        return False

    prefix = existing
    if prefix and not prefix.endswith("\n"):
        prefix += "\n"
    if prefix and not prefix.endswith("\n\n"):
        prefix += "\n"

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(prefix + "\n".join(missing) + "\n", encoding="utf-8")
    return True


def safe_join(root: str | Path, *parts: str) -> Path:
    """Join paths and reject traversal outside the project root."""
    base = Path(root).resolve()
    target = base.joinpath(*parts).resolve()
    if target != base and base not in target.parents:
        raise ValueError(f"path escapes project root: {target}")
    return Path(root).joinpath(*parts)


def list_tree(root: str | Path, max_depth: int) -> list[str]:
    """Return a deterministic relative tree up to max_depth.

    Depth is counted by path parts from root. A direct child has depth 1.
    Directories include a trailing slash.
    """
    base = Path(root)
    if max_depth < 1 or not base.exists():
        return []

    entries: list[str] = []
    for path in sorted(base.rglob("*"), key=lambda item: item.relative_to(base).as_posix()):
        relative = path.relative_to(base)
        if len(relative.parts) > max_depth:
            continue
        text = relative.as_posix()
        entries.append(f"{text}/" if path.is_dir() else text)
    return entries
