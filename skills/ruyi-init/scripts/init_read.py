"""Read existing frontend project facts for Ruyi initialization."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from common import list_tree, read_text
from init_detect import detect, dependency_names, load_package_json


ROOT_FILE_CANDIDATES = (
    "package.json",
    "index.html",
    "vite.config.ts",
    "vite.config.js",
    "webpack.config.ts",
    "webpack.config.js",
    "tsconfig.json",
    "jsconfig.json",
)

ENTRY_FILE_CANDIDATES = (
    "main.ts",
    "main.js",
    "src/main.ts",
    "src/main.js",
    "src/main.tsx",
    "src/main.jsx",
    "src/App.vue",
    "src/App.tsx",
    "src/App.jsx",
    "src/App.js",
    "app.vue",
    "App.vue",
)

ROUTER_DIRS = ("src/router", "src/routers", "router", "routers")
STORE_DIRS = ("src/store", "src/stores", "src/pinia", "src/vuex", "store", "stores")
API_DIRS = ("src/api", "src/apis", "api", "apis")
SERVICE_DIRS = ("src/service", "src/services", "service", "services")
MODULE_ROOTS = ("src/views", "src/pages", "src/modules", "src/module", "views", "pages", "modules", "module")
DOCUMENT_ROOT_FILES = (
    "README.md",
    "README.zh.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
)
DOCUMENT_DIRS = ("docs", "mock")
DOCUMENT_SUFFIXES = (".md", ".mdx", ".txt", ".yaml", ".yml", ".json")
DOCUMENT_SAMPLE_LIMIT = 1200

INIT_INTERVIEW_QUESTIONS = (
    {
        "key": "auth.method",
        "topic": "鉴权流程",
        "question": "鉴权方式？",
        "options": ["JWT", "Session", "OAuth", "其它", "不知道"],
    },
    {
        "key": "auth.token_storage",
        "topic": "鉴权流程",
        "question": "token 存在哪里？",
        "options": ["localStorage", "cookie", "memory", "其它", "不知道"],
    },
    {
        "key": "auth.refresh",
        "topic": "鉴权流程",
        "question": "token 刷新机制？",
        "options": ["refresh token", "重新登录", "无刷新", "其它", "不知道"],
    },
    {
        "key": "auth.failure",
        "topic": "鉴权流程",
        "question": "鉴权失败后怎么处理？",
        "options": ["跳登录页", "弹窗提示", "静默刷新", "其它", "不知道"],
    },
    {
        "key": "error.response_envelope",
        "topic": "错误处理",
        "question": "接口是否有统一响应结构？",
        "options": ["是", "否", "部分接口有", "不知道"],
    },
    {
        "key": "error.code_field",
        "topic": "错误处理",
        "question": "业务错误码字段？",
        "options": ["code", "errCode", "status", "其它", "不知道"],
    },
    {
        "key": "error.success_rule",
        "topic": "错误处理",
        "question": "业务成功判定？",
        "options": ["code === 0", "success === true", "HTTP 2xx", "其它", "不知道"],
    },
    {
        "key": "routing.mode",
        "topic": "路由约定",
        "question": "路由主要如何组织？",
        "options": ["集中 routes 文件", "模块内路由", "文件路由", "其它", "不知道"],
    },
    {
        "key": "routing.auth_guard",
        "topic": "路由约定",
        "question": "路由权限在哪里处理？",
        "options": ["全局 guard", "页面内判断", "后端菜单", "其它", "不知道"],
    },
    {
        "key": "routing.layout",
        "topic": "路由约定",
        "question": "布局如何绑定路由？",
        "options": ["父路由 layout", "页面组件自带", "动态 layout", "其它", "不知道"],
    },
)


def existing_files(project: Path, candidates: tuple[str, ...]) -> list[str]:
    return [item for item in candidates if (project / item).is_file()]


def files_under(project: Path, directories: tuple[str, ...], suffixes: tuple[str, ...] = (".js", ".jsx", ".ts", ".tsx", ".vue")) -> list[str]:
    found: list[str] = []
    for directory in directories:
        root = project / directory
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix in suffixes:
                found.append(path.relative_to(project).as_posix())
    return found


def extract_route_names(project: Path, router_files: list[str]) -> list[str]:
    names: set[str] = set()
    for item in router_files:
        text = read_text(project / item)
        for match in re.finditer(r"name\s*:\s*['\"]([^'\"]+)['\"]", text):
            names.add(match.group(1))
        for match in re.finditer(r"path\s*:\s*['\"]([^'\"]+)['\"]", text):
            names.add(match.group(1).strip("/") or "/")
    return sorted(names)


def detect_language(project: Path, root_files: list[str], entry_files: list[str]) -> str:
    if "tsconfig.json" in root_files or any(Path(item).suffix in (".ts", ".tsx") for item in entry_files):
        return "typescript"
    if any(project.rglob("*.ts")) or any(project.rglob("*.tsx")):
        return "typescript"
    return "javascript"


def module_candidates(project: Path) -> list[str]:
    candidates: set[str] = set()
    for root_name in MODULE_ROOTS:
        root = project / root_name
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if child.is_dir():
                candidates.add(child.relative_to(project).as_posix())
    return sorted(candidates)


def document_candidates(project: Path) -> list[dict[str, Any]]:
    candidates: list[Path] = []
    for name in DOCUMENT_ROOT_FILES:
        path = project / name
        if path.is_file():
            candidates.append(path)

    for directory in DOCUMENT_DIRS:
        root = project / directory
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in DOCUMENT_SUFFIXES:
                candidates.append(path)

    items: list[dict[str, Any]] = []
    for path in sorted(set(candidates), key=lambda item: item.relative_to(project).as_posix()):
        try:
            sample = path.read_text(encoding="utf-8", errors="replace")[:DOCUMENT_SAMPLE_LIMIT]
        except OSError:
            sample = ""
        stat = path.stat()
        items.append(
            {
                "path": path.relative_to(project).as_posix(),
                "size": stat.st_size,
                "modified_at": int(stat.st_mtime),
                "sample": sample,
                "quality": "unreviewed",
            }
        )
    return items


def detect_test_signals(package: dict[str, Any]) -> list[str]:
    signals: set[str] = set()
    scripts = package.get("scripts")
    if isinstance(scripts, dict):
        for name, command in scripts.items():
            text = f"{name} {command}".lower()
            for marker in ("test", "vitest", "jest", "playwright", "cypress"):
                if marker in text:
                    signals.add(marker)

    for name in dependency_names(package):
        lower = name.lower()
        for marker in ("vitest", "jest", "playwright", "cypress"):
            if marker in lower:
                signals.add(marker)
    return sorted(signals)


def read_project(project_path: str | Path) -> dict[str, Any]:
    project = Path(project_path)
    package = load_package_json(project)
    detection = detect(project)
    root_files = existing_files(project, ROOT_FILE_CANDIDATES)
    entry_files = existing_files(project, ENTRY_FILE_CANDIDATES)
    router_files = files_under(project, ROUTER_DIRS)
    store_files = files_under(project, STORE_DIRS)
    api_files = files_under(project, API_DIRS)
    service_files = files_under(project, SERVICE_DIRS)
    tests = detect_test_signals(package)

    questions: list[str] = []
    if not router_files:
        questions.append("未识别到 router 入口，需确认项目路由组织方式。")
    if not api_files and not service_files:
        questions.append("未识别到 api/service 数据访问层，需确认接口调用方式。")
    if not tests:
        questions.append("未识别到测试脚本或测试依赖，需确认验证方式。")

    return {
        "root_files": root_files,
        "entry_files": entry_files,
        "framework": detection["framework"],
        "bundler": detection["bundler"],
        "language": detect_language(project, root_files, entry_files),
        "router": {
            "files": router_files,
            "route_names": extract_route_names(project, router_files),
        },
        "store": {
            "files": store_files,
        },
        "data_access": {
            "api_files": api_files,
            "service_files": service_files,
            "style": "layered" if service_files else ("api-only" if api_files else "unknown"),
        },
        "module_candidates": module_candidates(project),
        "test_signals": tests,
        "project_tree": list_tree(project, max_depth=3),
        "open_questions": questions,
        "brownfield": {
            "document_sources": document_candidates(project),
            "interview_questions": list(INIT_INTERVIEW_QUESTIONS),
            "interview_answers": {},
            "open_topics": [],
            "unknown_answers": 0,
        },
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Read frontend project facts for Ruyi initialization.")
    parser.add_argument("--project", required=True, help="Project root path")
    args = parser.parse_args(argv)

    output = json.dumps(read_project(args.project), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
