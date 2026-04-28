"""Report Ruyi initialization results, missing items, and refusal reasons."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- 无"
    return "\n".join(f"- {item}" for item in items)


def format_report(detect: dict[str, Any], write: dict[str, Any]) -> str:
    if not detect.get("supported", False):
        return f"""# Ruyi 初始化结果

## 结论

拒绝初始化。

## 原因

{detect.get("message") or "当前项目不在 Ruyi 首版支持范围内。"}
"""

    if detect.get("initialized") and detect.get("complete"):
        return f"""# Ruyi 初始化结果

## 结论

无需初始化，当前项目 Ruyi 结构完整。

## 说明

{detect.get("message") or "Ruyi 已初始化且结构完整。"}
"""

    if detect.get("initialized") and not detect.get("complete"):
        return f"""# Ruyi 初始化结果

## 结论

拒绝自动补齐。

## 原因

项目已经存在部分 Ruyi 结构，但结构不完整。根据 Ruyi 初始化门禁，不能自动补齐，需人工确认后处理。

## 缺失项

{bullet_list(detect.get("missing_required", []))}
"""

    return f"""# Ruyi 初始化结果

## 结论

初始化完成。

## 已创建

{bullet_list(write.get("created", []))}

## 已更新

{bullet_list(write.get("updated", []))}

## 已跳过

{bullet_list(write.get("skipped", []))}

## 待确认

{bullet_list(write.get("notes", []))}
"""


def main(argv: list[str] | None = None, *, emit: bool = True) -> str:
    parser = argparse.ArgumentParser(description="Format Ruyi initialization report.")
    parser.add_argument("--detect", required=True, help="JSON file from init_detect.py")
    parser.add_argument("--write", required=True, help="JSON file from init_write.py")
    args = parser.parse_args(argv)

    detect = json.loads(Path(args.detect).read_text(encoding="utf-8-sig"))
    write = json.loads(Path(args.write).read_text(encoding="utf-8-sig"))
    report = format_report(detect, write)
    if emit:
        print(report)
    return report


if __name__ == "__main__":
    main()
