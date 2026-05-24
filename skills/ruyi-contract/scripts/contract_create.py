"""Create a Ruyi contract document without overwriting existing files."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


CONTRACT_TYPES = ("new-feature", "fix", "refactor", "change")
CONTRACT_STATUSES = ("draft", "confirmed", "reopened")
CONTRACT_SIZES = ("tiny", "standard", "large")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def validate_slug(name: str, value: str) -> None:
    if not SLUG_PATTERN.match(value):
        raise ValueError(f"{name} must use lowercase letters, numbers, and hyphens: {value}")


def validate_payload(payload: dict[str, Any]) -> None:
    required = ("module", "feature", "date", "type", "title", "goal", "story", "acceptance", "test_cases")
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")

    validate_slug("module", payload["module"])
    validate_slug("feature", payload["feature"])

    if payload["type"] not in CONTRACT_TYPES:
        raise ValueError(f"type must be one of: {', '.join(CONTRACT_TYPES)}")
    status = payload.get("status") or "draft"
    if status not in CONTRACT_STATUSES:
        raise ValueError(f"status must be one of: {', '.join(CONTRACT_STATUSES)}")
    size = payload.get("size") or "standard"
    if size not in CONTRACT_SIZES:
        raise ValueError(f"size must be one of: {', '.join(CONTRACT_SIZES)}")
    if payload["type"] == "fix" and size == "tiny":
        raise ValueError("fix contract cannot use tiny size")
    if not DATE_PATTERN.match(payload["date"]):
        raise ValueError("date must use YYYY-MM-DD")

    if not as_list(payload["acceptance"]):
        raise ValueError("acceptance must include at least one item")
    if not as_list(payload["test_cases"]):
        raise ValueError("test_cases must include at least one item")
    if status == "confirmed" and size in ("standard", "large") and len(as_list(payload["test_cases"])) < 3:
        raise ValueError("confirmed standard/large contract requires at least 3 test cases: happy path, boundary, and error/exception")
    if payload["type"] == "fix":
        fix_required = ("problem", "impact", "verification_direction")
        fix_missing = [key for key in fix_required if not payload.get(key)]
        if fix_missing:
            raise ValueError(f"fix contract requires: {', '.join(fix_missing)}")


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def is_initialized(project: Path) -> bool:
    return (project / ".ruyirc").is_file() and (project / ".ruyi" / "contracts").is_dir()


def contract_path(project: Path, payload: dict[str, Any]) -> Path:
    return (
        project
        / ".ruyi"
        / "contracts"
        / payload["module"]
        / payload["feature"]
        / f"{payload['date']}.md"
    )


def bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def rebuild_index_if_available(project: Path) -> dict[str, Any] | None:
    script = Path(__file__).resolve().parents[2] / "using-ruyi" / "scripts" / "index_rebuild.py"
    if not script.is_file():
        return None
    spec = importlib.util.spec_from_file_location("ruyi_index_rebuild", script)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.rebuild_index(project)


def render_contract(payload: dict[str, Any]) -> str:
    scope = as_list(payload.get("scope")) or ["待补充。"]
    acceptance = as_list(payload["acceptance"])
    test_cases = as_list(payload["test_cases"])
    out_of_scope = as_list(payload.get("out_of_scope")) or ["待补充。"]
    fix_section = ""
    api_scope = as_list(payload.get("api_scope"))
    api_section = "\n## 接口范围\n\n本次不涉及接口。\n"
    if api_scope:
        api_section = f"\n## 接口范围\n\n{bullet_list(api_scope)}\n"
    if payload["type"] == "fix":
        fix_section = f"""
## 修复事实

- 问题现象：{payload["problem"]}
- 影响范围：{payload["impact"]}
- 验证方向：{payload["verification_direction"]}
"""

    frontmatter = {
        "type": payload["type"],
        "size": payload.get("size") or "standard",
        "module": payload["module"],
        "feature": payload["feature"],
        "date": payload["date"],
        "status": payload.get("status") or "draft",
    }
    if payload.get("superseded_by"):
        frontmatter["superseded_by"] = payload["superseded_by"]
    frontmatter_text = "\n".join(f"{key}: {value}" for key, value in frontmatter.items())

    return f"""---
{frontmatter_text}
---

# Contract：{payload["title"]}

## 用户故事

{payload["story"]}

## 需求范围

### 范围内

{bullet_list(scope)}

### 范围外

{bullet_list(out_of_scope)}

## 业务规则

- 需求类型：{payload["type"]}
- 业务目标：{payload["goal"]}
- 所属模块：{payload["module"]}
- 功能对象：{payload["feature"]}
{fix_section}
{api_section}

## 验收标准

{bullet_list(acceptance)}

## 测试用例

{bullet_list(test_cases)}
"""


def create_contract(project_path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    project = Path(project_path)
    validate_payload(payload)

    if not is_initialized(project):
        return {
            "created": False,
            "reason": "project-not-initialized",
            "message": "项目未初始化 Ruyi，不能正式创建 contract。",
            "path": None,
        }

    target = contract_path(project, payload)
    if target.exists():
        existing = target.read_text(encoding="utf-8")
        if "status: reopened" in existing and payload.get("status") in ("draft", "confirmed"):
            history_start = existing.find("\n## 返工记录")
            history = existing[history_start:] if history_start != -1 else ""
            target.write_text(render_contract(payload).rstrip() + "\n" + history, encoding="utf-8")
            return {
                "created": False,
                "updated": True,
                "reason": None,
                "message": "已重开的 contract 当前内容已更新。",
                "path": str(target),
                "index": rebuild_index_if_available(project),
            }
        return {
            "created": False,
            "reason": "already-exists",
            "message": "contract 已存在，未覆盖。",
            "path": str(target),
        }

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_contract(payload), encoding="utf-8")
    index_result = rebuild_index_if_available(project)
    return {
        "created": True,
        "reason": None,
        "message": "contract 已创建。",
        "path": str(target),
        "index": index_result,
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Create a Ruyi contract document.")
    parser.add_argument("--project", required=True, help="Project root path")
    parser.add_argument("--module", required=True, help="Module slug")
    parser.add_argument("--feature", required=True, help="Feature slug")
    parser.add_argument("--date", required=True, help="Contract date, YYYY-MM-DD")
    parser.add_argument("--type", required=True, choices=CONTRACT_TYPES, help="Contract type")
    parser.add_argument("--size", default="standard", choices=CONTRACT_SIZES, help="Contract size track")
    parser.add_argument("--status", default="draft", choices=CONTRACT_STATUSES, help="Contract status")
    parser.add_argument("--title", required=True, help="Contract display title")
    parser.add_argument("--goal", required=True, help="Business goal")
    parser.add_argument("--story", required=True, help="User story")
    parser.add_argument("--scope", action="append", default=[], help="In-scope item")
    parser.add_argument("--out-of-scope", action="append", default=[], help="Out-of-scope item")
    parser.add_argument("--acceptance", action="append", required=True, help="Acceptance criterion")
    parser.add_argument("--test-case", action="append", required=True, help="Natural-language test case")
    parser.add_argument("--api-scope", action="append", default=[], help="API scope item for this contract")
    parser.add_argument("--superseded-by", help="Replacement contract path/date for semantic amendments")
    parser.add_argument("--problem", help="Required for fix: observed problem")
    parser.add_argument("--impact", help="Required for fix: impact scope")
    parser.add_argument("--verification-direction", help="Required for fix: verification direction")
    args = parser.parse_args(argv)

    payload = {
        "module": args.module,
        "feature": args.feature,
        "date": args.date,
        "type": args.type,
        "size": args.size,
        "status": args.status,
        "title": args.title,
        "goal": args.goal,
        "story": args.story,
        "scope": args.scope,
        "out_of_scope": args.out_of_scope,
        "acceptance": args.acceptance,
        "test_cases": args.test_case,
        "api_scope": args.api_scope,
        "superseded_by": args.superseded_by,
        "problem": args.problem,
        "impact": args.impact,
        "verification_direction": args.verification_direction,
    }
    output = json.dumps(create_contract(args.project, payload), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
