# Script Runtime Protocol

## 1. 定位

Ruyi 是 skill 包，不是 CLI 产品。脚本是可选的协议辅助工具，不是主流程的唯一入口。

## 2. 路由判断

路由判断由 agent 主导：

1. 优先读取 `using-ruyi/SKILL.md` 的路由判定表。
2. 直接读取 `.ruyi/` 产物、frontmatter 和目录结构。
3. Python 可用时，可以用 `route_request.py` 复核。
4. Python 不可用时，不得因为脚本失败而绕过 Ruyi 门禁。

## 3. 写入脚本 fallback

阶段产物写入按以下顺序选择：

1. 项目有 Node 且存在对应 `.mjs` 脚本：优先使用 `.mjs`。
2. Python 可用且存在 `.py` 脚本：使用 `.py`。
3. 二者都不可用：agent 按 schema 直接写 Markdown，但必须逐项执行 schema 和 discipline 的硬门禁。

## 4. 约束

- 脚本失败不是跳过流程的理由。
- 直接写 Markdown 时，仍然不能覆盖已有产物。
- 直接写 Markdown 时，必须保留固定路径、frontmatter 和章节结构。
- 能用脚本校验的场景，优先用脚本；脚本不可用时才 fallback。
