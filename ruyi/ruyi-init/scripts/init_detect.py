"""Detect project support, initialization state, and structure completeness."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from common import REQUIRED_RUYI_DIRS, REQUIRED_RUYI_FILES


def load_package_json(project: Path) -> dict[str, Any]:
    package_json = project / "package.json"
    if not package_json.exists():
        return {}
    try:
        return json.loads(package_json.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {}


def dependency_names(package: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = package.get(key)
        if isinstance(value, dict):
            names.update(value.keys())
    return names


def detect_framework(dependencies: set[str]) -> str | None:
    if "vue" in dependencies:
        return "vue"
    if "react" in dependencies or "react-dom" in dependencies:
        return "react"
    return None


def detect_bundler(dependencies: set[str], project: Path) -> str | None:
    if "vite" in dependencies or (project / "vite.config.ts").exists() or (project / "vite.config.js").exists():
        return "vite"
    if "webpack" in dependencies or (project / "webpack.config.js").exists() or (project / "webpack.config.ts").exists():
        return "webpack"
    return None


def missing_required_paths(project: Path) -> list[str]:
    missing: list[str] = []
    for item in REQUIRED_RUYI_DIRS:
        if not (project / item).is_dir():
            missing.append(item)
    for item in REQUIRED_RUYI_FILES:
        if not (project / item).is_file():
            missing.append(item)
    return missing


def detect(project_path: str | Path) -> dict[str, Any]:
    project = Path(project_path)
    package = load_package_json(project)
    dependencies = dependency_names(package)
    framework = detect_framework(dependencies)
    bundler = detect_bundler(dependencies, project)
    supported = bool(framework and bundler)

    has_ruyi_dir = (project / ".ruyi").exists()
    has_ruyirc = (project / ".ruyirc").exists()
    initialized = has_ruyi_dir or has_ruyirc
    missing_required = missing_required_paths(project)
    complete = initialized and not missing_required

    if not supported:
        message = "当前仅支持前端项目：Vue/Vite、React/Vite、React/Webpack 或 Vue/Webpack。"
    elif complete:
        message = "Ruyi 已初始化且结构完整。"
    elif initialized:
        message = "Ruyi 已初始化但结构不完整。"
    else:
        message = "项目支持 Ruyi 初始化。"

    return {
        "supported": supported,
        "message": message,
        "initialized": initialized,
        "complete": complete,
        "missing_required": missing_required,
        "framework": framework,
        "bundler": bundler,
    }


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Detect Ruyi initialization state.")
    parser.add_argument("--project", required=True, help="Project root path")
    args = parser.parse_args(argv)

    output = json.dumps(detect(args.project), ensure_ascii=False, indent=2)
    if emit:
        print(output)
    return output


if __name__ == "__main__":
    main()
