# Ruyi 安装说明

Ruyi 的安装方式应保持轻量：保留完整 Ruyi 仓库，把 `skills/` 目录下的各个 skill 平铺到目标 code agent 的 skills 搜索目录。

> Ruyi is a frontend dev contract framework for AI coding agents. Install the skill package once, then let the agent route project work through Ruyi's fixed pipeline.

当前发布结构要求每个 skill 都带自己的 `references/`，不依赖顶层共享 references。这样 Trae、Claude Code CLI 等只识别平铺 skill 目录的工具也能正常发现 Ruyi。

## 安装模型

```text
Ruyi 仓库/
├── README.md
├── assets/
└── skills/
    ├── using-ruyi/
    ├── ruyi-init/
    ├── ruyi-contract/
    ├── ruyi-plan/
    ├── ruyi-implement/
    ├── ruyi-test/
    ├── ruyi-explain/      # deprecated compatibility entry
    ├── ruyi-approve/
    ├── ruyi-upgrade/
    ├── ruyi-spec-discover/
    ├── ruyi-spec-evolve/
    └── ruyi-spec-merge/

Agent skills 目录/
├── using-ruyi/
├── ruyi-init/
├── ruyi-contract/
├── ruyi-plan/
├── ruyi-implement/
├── ruyi-test/
├── ruyi-explain/      # deprecated compatibility entry
├── ruyi-approve/
├── ruyi-upgrade/
├── ruyi-spec-discover/
├── ruyi-spec-evolve/
└── ruyi-spec-merge/
```

核心原则：

- 不要求把 Ruyi 做成 CLI。
- 不要求 agent 用户记住脚本命令。
- 不把多个 skill 包在一个 `ruyi/` 父目录里发布。
- 不依赖顶层共享 `references/`。
- 本地开发时优先使用目录联接，避免复制后忘记同步。

## 本地开发安装

假设 Ruyi 位于：

```text
D:\AIWorks\ruyi
```

### Windows

将目标 agent 的 skills 目录替换成实际路径，例如 `C:\Users\<you>\.agents\skills`：

```powershell
$target = "$env:USERPROFILE\.agents\skills"
New-Item -ItemType Directory -Force -Path $target

Get-ChildItem "D:\AIWorks\ruyi\skills" -Directory | ForEach-Object {
  $link = Join-Path $target $_.Name
  if (-not (Test-Path $link)) {
    cmd /c mklink /J $link $_.FullName
  }
}
```

### macOS / Linux

将目标 agent 的 skills 目录替换成实际路径，例如 `~/.agents/skills`：

```bash
mkdir -p ~/.agents/skills
for skill in /path/to/ruyi/skills/*; do
  ln -s "$skill" ~/.agents/skills/"$(basename "$skill")"
done
```

## Git 安装

```bash
git clone https://github.com/Nikicho/ruyi.git ~/.ruyi
mkdir -p ~/.agents/skills
for skill in ~/.ruyi/skills/*; do
  ln -s "$skill" ~/.agents/skills/"$(basename "$skill")"
done
```

Windows：

```powershell
git clone https://github.com/Nikicho/ruyi.git "$env:USERPROFILE\.ruyi"
$target = "$env:USERPROFILE\.agents\skills"
New-Item -ItemType Directory -Force -Path $target

Get-ChildItem "$env:USERPROFILE\.ruyi\skills" -Directory | ForEach-Object {
  $link = Join-Path $target $_.Name
  if (-not (Test-Path $link)) {
    cmd /c mklink /J $link $_.FullName
  }
}
```

## 验证

查看目标 skills 目录下是否能看到平铺的 Ruyi skills：

```powershell
Get-ChildItem "$env:USERPROFILE\.agents\skills" | Where-Object Name -like "ruyi-*"
Get-ChildItem "$env:USERPROFILE\.agents\skills\using-ruyi"
```

期望能看到：

```text
using-ruyi
ruyi-init
ruyi-contract
ruyi-plan
ruyi-implement
ruyi-test
ruyi-explain  # deprecated compatibility entry
ruyi-approve
ruyi-upgrade
ruyi-spec-discover
ruyi-spec-evolve
ruyi-spec-merge
```

然后重启 code agent，让它重新发现 skills。

## 更新

如果使用本地开发链接，直接修改 Ruyi 仓库即可。

如果使用 Git：

```bash
cd ~/.ruyi
git pull
```

复制安装的场景需要重新复制 `skills/` 下的各个目录。

更新 skills 后，已经初始化过的业务项目应先通过统一入口运行升级：

```text
请使用 using-ruyi 继续当前项目工作；如果项目 schema 落后，先运行 ruyi-upgrade。
```

`ruyi-upgrade` 会自动迁移 `.ruyirc`、本地忽略规则、INDEX、旧 explain 审批、旧 frontend baseline 和旧二级 spec INDEX。检测到旧 `explain / workspace / spec-archive / spec-patches` 目录时，会先询问是否删除；删除确认完成后才标记为 schema v3。

## 卸载

删除目标 skills 目录下的 Ruyi skill 链接或复制目录即可，不需要删除业务项目中已生成的 `.ruyi/`。

Windows 示例：

```powershell
Remove-Item "$env:USERPROFILE\.agents\skills\using-ruyi" -Force
Remove-Item "$env:USERPROFILE\.agents\skills\ruyi-*" -Force
```

macOS / Linux 示例：

```bash
rm ~/.agents/skills/using-ruyi
rm -rf ~/.agents/skills/ruyi-*
```
