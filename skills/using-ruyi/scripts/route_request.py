"""Route a user request to the next Ruyi stage based on project artifacts.

Deprecated as a mandatory entry point: using-ruyi/SKILL.md contains the
authoritative routing table. Keep this script as an optional consistency check.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


INTENTS = ("init", "contract", "plan", "implement", "test", "explain", "approve", "spec-evolve", "continue")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CONTRACT_READY_STATUSES = ("confirmed",)
PLAN_STATUSES = ("confirmed",)
TASK_READY_STATUSES = ("done",)
TEST_PASSING_RESULTS = ("passed", "passed-with-notes")
EXPLAIN_REQUIRED_LINKS = ("contract", "plan", "test")
TINY_SIZE = "tiny"

STAGE_SKILLS = {
    "init": "ruyi-init",
    "contract": "ruyi-contract",
    "plan": "ruyi-plan",
    "implement": "ruyi-implement",
    "test": "ruyi-test",
    "explain": "ruyi-explain",
    "approve": "ruyi-approve",
    "spec-evolve": "ruyi-spec-evolve",
    "complete": None,
}


def validate_slug(name: str, value: str) -> None:
    if not SLUG_PATTERN.match(value):
        raise ValueError(f"{name} must use lowercase letters, numbers, and hyphens: {value}")


def validate_intent(payload: dict[str, Any]) -> None:
    intent = payload.get("intent")
    if intent not in INTENTS:
        raise ValueError(f"intent must be one of: {', '.join(INTENTS)}")


def validate_stage_payload(payload: dict[str, Any]) -> None:
    intent = payload.get("intent")
    if intent == "continue" and not has_stage_identity(payload):
        return
    if intent in ("plan", "implement", "test", "explain", "approve", "spec-evolve", "continue"):
        required = ("module", "feature", "date")
        missing = [key for key in required if not payload.get(key)]
        if missing:
            raise ValueError(f"missing required fields for {intent}: {', '.join(missing)}")
        validate_slug("module", payload["module"])
        validate_slug("feature", payload["feature"])
        if not DATE_PATTERN.match(payload["date"]):
            raise ValueError("date must use YYYY-MM-DD")


def has_stage_identity(payload: dict[str, Any]) -> bool:
    return all(payload.get(key) for key in ("module", "feature", "date"))


def is_initialized(project: Path) -> bool:
    return (project / ".ruyirc").is_file() and (project / ".ruyi").is_dir()


def contract_path(project: Path, payload: dict[str, Any]) -> Path:
    return project / ".ruyi" / "contracts" / payload["module"] / payload["feature"] / f"{payload['date']}.md"


def task_dir(project: Path, payload: dict[str, Any]) -> Path:
    return project / ".ruyi" / "tasks" / payload["module"] / payload["feature"] / payload["date"]


def plan_path(project: Path, payload: dict[str, Any]) -> Path:
    return project / ".ruyi" / "plans" / payload["module"] / payload["feature"] / f"{payload['date']}.md"


def test_path(project: Path, payload: dict[str, Any]) -> Path:
    return project / ".ruyi" / "tests" / payload["module"] / payload["feature"] / f"{payload['date']}.md"


def explain_path(project: Path, payload: dict[str, Any]) -> Path:
    return project / ".ruyi" / "explain" / payload["module"] / payload["feature"] / f"{payload['date']}.md"


def candidate_path(project: Path, payload: dict[str, Any]) -> Path:
    return project / ".ruyi" / "spec-candidates" / payload["module"] / payload["feature"] / f"{payload['date']}.md"


def has_task(project: Path, payload: dict[str, Any]) -> bool:
    directory = task_dir(project, payload)
    return directory.is_dir() and any(directory.glob("task-*.md"))


def has_done_task(project: Path, payload: dict[str, Any]) -> bool:
    directory = task_dir(project, payload)
    if not directory.is_dir():
        return False
    for path in directory.glob("task-*.md"):
        status = parse_frontmatter(path).get("status")
        if status in TASK_READY_STATUSES:
            return True
    return False


def explain_has_required_links(project: Path, payload: dict[str, Any]) -> bool:
    frontmatter = parse_frontmatter(explain_path(project, payload))
    return all(frontmatter.get(key) for key in EXPLAIN_REQUIRED_LINKS)


def contract_size(project: Path, payload: dict[str, Any]) -> str:
    return parse_frontmatter(contract_path(project, payload)).get("size") or "standard"


def section_has_content(text: str, heading: str) -> bool:
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return False
    next_heading = text.find("\n## ", start + len(marker))
    section = text[start + len(marker) : next_heading if next_heading != -1 else len(text)]
    content = [line.strip() for line in section.splitlines() if line.strip()]
    return any(line not in ("待补充。", "- 待补充。") for line in content)


def contract_has_required_content(path: Path) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    return section_has_content(text, "验收标准") and section_has_content(text, "测试用例")


def plan_has_contract_anchor(path: Path) -> bool:
    frontmatter = parse_frontmatter(path)
    return bool(frontmatter.get("contract"))


def parse_frontmatter(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
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


def route(
    stage: str,
    blockers: list[str] | None = None,
    message: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    result = {
        "stage": stage,
        "skill": STAGE_SKILLS[stage],
        "blockers": blockers or [],
        "message": message or "",
    }
    result.update(extra)
    return result


def artifact_candidate_from_path(project: Path, path: Path) -> dict[str, str] | None:
    relative = path.relative_to(project).parts
    if len(relative) < 5 or relative[0] != ".ruyi":
        return None

    section = relative[1]
    if section in ("contracts", "plans", "tests", "explain", "spec-candidates") and len(relative) == 5:
        date = Path(relative[4]).stem
        if DATE_PATTERN.match(date):
            return {"module": relative[2], "feature": relative[3], "date": date}

    if section == "tasks" and len(relative) == 6:
        date = relative[4]
        if DATE_PATTERN.match(date):
            return {"module": relative[2], "feature": relative[3], "date": date}

    return None


def active_candidates(project: Path) -> list[dict[str, str]]:
    roots = [
        project / ".ruyi" / "contracts",
        project / ".ruyi" / "plans",
        project / ".ruyi" / "tasks",
        project / ".ruyi" / "tests",
        project / ".ruyi" / "explain",
    ]
    files: list[Path] = []
    for root in roots:
        if root.is_dir():
            files.extend(path for path in root.rglob("*.md") if path.is_file())

    seen: set[tuple[str, str, str]] = set()
    candidates: list[dict[str, str]] = []
    for path in sorted(files, key=lambda item: item.stat().st_mtime, reverse=True):
        candidate = artifact_candidate_from_path(project, path)
        if not candidate:
            continue
        key = (candidate["module"], candidate["feature"], candidate["date"])
        if key in seen:
            continue
        seen.add(key)
        candidates.append(candidate)
    return candidates


def route_continue_without_identity(project: Path) -> dict[str, Any]:
    candidates = active_candidates(project)
    if not candidates:
        return route(
            "contract",
            ["active-contract-not-found"],
            "未能定位当前活动需求，请先说明要继续哪个模块和功能。",
            candidates=[],
        )
    if len(candidates) > 1:
        return route(
            "contract",
            ["active-contract-ambiguous"],
            "发现多个活动需求，请先确认要继续哪一个。",
            candidates=candidates,
        )

    payload = {"intent": "continue", **candidates[0]}
    return route_continue(project, payload)


def route_request(project_path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    validate_intent(payload)

    project = Path(project_path)
    intent = payload["intent"]
    initialized = is_initialized(project)

    if not initialized:
        return route("init", ["project-not-initialized"], "项目未初始化，必须先进入 ruyi-init。")

    validate_stage_payload(payload)

    if intent == "continue" and not has_stage_identity(payload):
        return route_continue_without_identity(project)

    if intent in ("init", "contract"):
        return route(intent, [], f"进入 {STAGE_SKILLS[intent]}。")

    contract = contract_path(project, payload)
    if not contract.is_file():
        return route("contract", ["contract-not-found"], "缺少 contract，先进入需求定义阶段。")

    contract_status = parse_frontmatter(contract).get("status")
    if contract_status not in CONTRACT_READY_STATUSES:
        return route("contract", ["contract-not-confirmed"], "contract 未确认，不能进入 plan。")
    if not contract_has_required_content(contract):
        return route("contract", ["contract-incomplete"], "contract 缺少验收标准或测试用例，不能进入后续阶段。")
    size = contract_size(project, payload)

    if intent == "plan":
        if size == TINY_SIZE:
            return route("implement", ["tiny-skips-plan"], "tiny contract 省略 plan，直接进入实现。")
        return route("plan", [], "contract 已存在，可以进入开发计划阶段。")

    if size == TINY_SIZE:
        if intent == "implement":
            return route("implement", [], "tiny contract 已确认，可以进入轻量实现。")
        if intent == "test":
            return route("test", [], "tiny contract 已确认，可以进入轻量验证。")
        test = test_path(project, payload)
        if intent in ("explain", "approve", "spec-evolve"):
            if not test.is_file():
                return route("test", ["test-not-found"], "tiny contract 缺少 test，不能收口。")
            test_result = parse_frontmatter(test).get("result")
            if test_result not in TEST_PASSING_RESULTS:
                return route("test", ["test-not-passed"], "tiny contract 的 test 未通过，不能收口。")
            return route("complete", ["tiny-complete"], "tiny contract 已完成，默认不强制 explain/approve/spec-candidate。")

    plan = plan_path(project, payload)
    if intent in ("implement", "test", "explain", "approve", "spec-evolve") and not plan.is_file():
        return route("plan", ["plan-not-found"], "缺少 plan，不能进入正式实现。")

    if intent in ("implement", "test", "explain", "approve", "spec-evolve") and not plan_has_contract_anchor(plan):
        return route("plan", ["plan-missing-contract-anchor"], "plan 缺少 contract 锚点，不能进入正式实现。")

    plan_status = parse_frontmatter(plan).get("status")
    if intent in ("implement", "test", "explain", "approve", "spec-evolve") and plan_status not in PLAN_STATUSES:
        return route("plan", ["plan-not-confirmed"], "plan 未确认，不能进入正式实现。")

    if intent == "implement":
        return route("implement", [], "contract 和 plan 已存在，可以进入实现阶段。")

    if intent == "test" and not has_done_task(project, payload):
        blocker = "task-not-done" if has_task(project, payload) else "task-not-found"
        return route("implement", [blocker], "缺少已完成的 task 执行结果，不能进入正式测试。")

    if intent == "test":
        return route("test", [], "contract、plan 和 task 已存在，可以进入测试验证阶段。")

    test = test_path(project, payload)
    if intent == "explain" and not test.is_file():
        return route("test", ["test-not-found"], "缺少 test，不能生成 explain。")

    test_result = parse_frontmatter(test).get("result")
    if intent == "explain" and test_result not in TEST_PASSING_RESULTS:
        return route("test", ["test-not-passed"], "test 未通过，不能生成 explain。")

    if intent == "explain":
        return route("explain", [], "contract 和 test 已存在，可以生成 explain。")

    if intent in ("approve", "spec-evolve") and not explain_path(project, payload).is_file():
        return route("explain", ["explain-not-found"], "缺少 explain，不能进入后续阶段。")

    if intent in ("approve", "spec-evolve") and not explain_has_required_links(project, payload):
        return route("explain", ["explain-missing-links"], "explain 缺少 contract、plan 或 test 锚点，不能进入后续阶段。")

    if intent == "approve":
        return route("approve", [], "explain 已存在，可以进入审批阶段。")

    if intent == "spec-evolve":
        approval = parse_frontmatter(explain_path(project, payload)).get("approval")
        if approval != "approved":
            return route("approve", ["approval-not-approved"], "explain 未审批通过，不能进入知识沉淀。")
        return route("spec-evolve", [], "explain 已审批通过，可以生成 spec candidate。")

    return route_continue(project, payload)


def route_continue(project: Path, payload: dict[str, Any]) -> dict[str, Any]:
    contract = contract_path(project, payload)
    if not contract.is_file():
        return route("contract", ["contract-not-found"], "下一步是补齐 contract。")
    contract_status = parse_frontmatter(contract).get("status")
    if contract_status not in CONTRACT_READY_STATUSES:
        return route("contract", ["contract-not-confirmed"], "下一步是确认 contract。")
    if not contract_has_required_content(contract):
        return route("contract", ["contract-incomplete"], "下一步是补齐 contract 的验收标准和测试用例。")
    size = contract_size(project, payload)

    if size == TINY_SIZE:
        test = test_path(project, payload)
        if not test.is_file():
            return route("implement", ["tiny-test-not-found"], "tiny contract 下一步是实现并补充 test 证据。")
        test_result = parse_frontmatter(test).get("result")
        if test_result not in TEST_PASSING_RESULTS:
            return route("test", ["test-not-passed"], "tiny contract 的 test 未通过，需修复或补充验证。")
        return route("complete", [], "tiny contract 已完成。")

    plan = plan_path(project, payload)
    if not plan.is_file():
        return route("plan", ["plan-not-found"], "下一步是制定 plan。")
    if not plan_has_contract_anchor(plan):
        return route("plan", ["plan-missing-contract-anchor"], "下一步是补齐 plan 的 contract 锚点。")
    plan_status = parse_frontmatter(plan).get("status")
    if plan_status not in PLAN_STATUSES:
        return route("plan", ["plan-not-confirmed"], "下一步是确认 plan。")

    if not has_done_task(project, payload):
        return route("implement", ["task-not-done"], "下一步是执行 task 并完成实现自检。")

    test = test_path(project, payload)
    if not test.is_file():
        return route("test", ["test-not-found"], "下一步是生成 test 验证结果。")
    test_result = parse_frontmatter(test).get("result")
    if test_result not in TEST_PASSING_RESULTS:
        return route("test", ["test-not-passed"], "下一步是修复或补充验证，直到 test 通过。")

    explain = explain_path(project, payload)
    if not explain.is_file():
        return route("explain", ["explain-not-found"], "下一步是生成 explain。")

    approval = parse_frontmatter(explain).get("approval")
    return_stage = parse_frontmatter(explain).get("return_stage")
    if approval in ("changes-requested", "rejected") and return_stage in ("contract", "plan", "implement", "test"):
        return route(return_stage, ["approval-returned"], f"审批未通过，需返回 {return_stage} 阶段处理。")
    if approval == "conditionally-approved":
        return route("approve", ["approval-conditional"], "explain 为条件通过，需先确认条件是否已处理。")
    if approval != "approved":
        return route("approve", ["approval-pending"], "下一步是审批 explain。")

    if not candidate_path(project, payload).is_file():
        return route("spec-evolve", ["spec-candidate-not-found"], "下一步是生成 spec candidate。")

    return route("complete", [], "该 contract 的 Ruyi 主流程已完成。")


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Route a request to the next Ruyi stage.")
    parser.add_argument("--project", required=True, help="Project root path")
    parser.add_argument("--intent", required=True, choices=INTENTS, help="Ruyi intent")
    parser.add_argument("--module", help="Module slug")
    parser.add_argument("--feature", help="Feature slug")
    parser.add_argument("--date", help="Contract date, YYYY-MM-DD")
    args = parser.parse_args(argv)

    payload = {
        "intent": args.intent,
        "module": args.module,
        "feature": args.feature,
        "date": args.date,
    }
    output = json.dumps(route_request(args.project, payload), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
