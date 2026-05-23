"""Update progress in a local Ruyi task checkpoint."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


CHECKPOINT_STATUSES = ("pending", "in-progress", "done")


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def task_target(project: Path, task_path: str | Path) -> Path:
    target = Path(task_path)
    if not target.is_absolute():
        target = project / target
    target = target.resolve()
    task_root = (project / ".ruyi" / "tasks").resolve()
    if task_root != target.parent and task_root not in target.parents:
        raise ValueError("task path must be inside .ruyi/tasks")
    if not target.is_file():
        raise ValueError("task checkpoint does not exist")
    return target


def render_progress(payload: dict[str, Any]) -> str:
    lines = [f"- 状态：{payload['status']}"]
    labels = (
        ("completed_steps", "已完成"),
        ("current", "当前处理"),
        ("next_step", "下一步"),
        ("modified_files", "已修改文件"),
        ("verification", "验证"),
        ("blockers", "阻塞"),
    )
    for key, label in labels:
        for item in as_list(payload.get(key)):
            lines.append(f"- {label}：{item}")
    return "## 当前进度\n\n" + "\n".join(lines) + "\n"


def update_checkpoint(project_path: str | Path, task_path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Update local execution progress; never update formal Ruyi artifacts or INDEX."""
    project = Path(project_path)
    status = payload.get("status")
    if status not in CHECKPOINT_STATUSES:
        raise ValueError(f"status must be one of: {', '.join(CHECKPOINT_STATUSES)}")
    target = task_target(project, task_path)
    text = target.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("task checkpoint must contain frontmatter")
    text = re.sub(r"^status:\s*.*$", f"status: {status}", text, count=1, flags=re.MULTILINE)
    progress = render_progress(payload)
    marker = "## 当前进度"
    start = text.find(marker)
    if start == -1:
        text = text.rstrip() + "\n\n" + progress
    else:
        end = text.find("\n## ", start + len(marker))
        if end == -1:
            text = text[:start].rstrip() + "\n\n" + progress
        else:
            text = text[:start].rstrip() + "\n\n" + progress + "\n" + text[end + 1 :]
    target.write_text(text, encoding="utf-8")
    return {"updated": True, "path": str(target), "status": status}


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Update a local Ruyi task checkpoint.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--status", required=True, choices=CHECKPOINT_STATUSES)
    parser.add_argument("--completed-step", action="append", default=[])
    parser.add_argument("--current", action="append", default=[])
    parser.add_argument("--next-step", action="append", default=[])
    parser.add_argument("--modified-file", action="append", default=[])
    parser.add_argument("--verification", action="append", default=[])
    parser.add_argument("--blocker", action="append", default=[])
    args = parser.parse_args(argv)
    payload = {
        "status": args.status,
        "completed_steps": args.completed_step,
        "current": args.current,
        "next_step": args.next_step,
        "modified_files": args.modified_file,
        "verification": args.verification,
        "blockers": args.blocker,
    }
    output = json.dumps(update_checkpoint(args.project, args.task, payload), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
