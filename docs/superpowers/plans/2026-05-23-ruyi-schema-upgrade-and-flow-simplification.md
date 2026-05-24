# Ruyi Schema 升级与流程简化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 落地 Ruyi schema v2，使新项目使用精简目录与状态模型，使存量项目可自动升级，并让长 plan 与已审批返工场景可可靠续接。

**Architecture:** `.ruyirc` 引入独立 `schema_version`，`using-ruyi` 在任何正式路由前先门禁 schema 升级；`ruyi-upgrade` 只机械迁移 Ruyi 协议结构，并对废弃目录删除动作单独确认。正式交付资产继续由 `contract / plan / test / explain / spec` 承载，本地 `tasks / spec-candidates` 按需创建，不再进入团队索引或正式门禁。

**Tech Stack:** Markdown skills 与 references、Python 3 标准库脚本、`unittest` 本地验证、Git。

---

## 实施边界

- 当前设计依据：[2026-05-23-ruyi-local-execution-and-spec-simplification-design.md](D:/AIWorks/ruyi/docs/superpowers/specs/2026-05-23-ruyi-local-execution-and-spec-simplification-design.md)。
- `fixtures/` 与 `skills/*/scripts/tests/` 仅用于本地验证，不纳入发布提交。
- 工作区已有 [CHANGELOG.md](D:/AIWorks/ruyi/CHANGELOG.md) 修改；实现阶段不得覆盖或顺手提交，直到用户明确进入 release note / 发布步骤时再审视合并。
- 所有 schema/reference 语义变更都必须同步各发布 skill 内的副本，不能只更新单一来源文件。

## 文件职责映射

| 单元 | 生产文件 | 职责 |
| --- | --- | --- |
| Init schema v2 | `skills/ruyi-init/scripts/common.py`、`skills/ruyi-init/scripts/init_write.py`、`skills/ruyi-init/scripts/init_report.py`、`skills/ruyi-init/SKILL.md` | 新项目只创建正式目录，写入 `schema_version: 2`，停止生成废弃本地产物 |
| Upgrade | `skills/ruyi-upgrade/SKILL.md`、`skills/ruyi-upgrade/scripts/upgrade_project.py`、必要 references | 识别旧 schema，执行幂等迁移，报告人工审视项，按确认删除废弃目录 |
| Router / Index | `skills/using-ruyi/SKILL.md`、`skills/using-ruyi/scripts/route_request.py`、`skills/using-ruyi/scripts/index_rebuild.py` | 升级前置门禁、continue 恢复、本地资产不进入正式索引、移除 done-task 硬门禁 |
| Local tasks | `skills/ruyi-implement/SKILL.md`、`skills/ruyi-implement/scripts/task_create.py`、新增 `skills/ruyi-implement/scripts/task_checkpoint.py` | 按需创建本地执行恢复点并持久化 compact 前进度 |
| Reopen flow | `skills/ruyi-contract/scripts/contract_create.py`、新增 `skills/ruyi-contract/scripts/reopen_delivery.py`、`skills/ruyi-test/scripts/test_create.py`、`skills/ruyi-explain/scripts/explain_create.py`、`skills/ruyi-approve/scripts/approve_update.py` | 类型 D 重开原 contract，重置同路径下当前交付状态，重新产出当前 test/explain |
| Spec simplify | `skills/ruyi-spec-evolve/scripts/candidate_create.py`、`skills/ruyi-spec-merge/scripts/merge_apply.py`、`skills/ruyi-spec-merge/scripts/merge_common.py`、相关 SKILL | candidate 仅按需暂存；确认后正式 spec 直接更新并删除 candidate |
| Published references/docs | `README.md`、`docs/install.md`、各 `skills/*/references/*.md`、各相关 `SKILL.md` | 对外说明与 skill 自带协议副本同步到 schema v2 |

### Task 1: Init 生成 schema v2 项目骨架

**Files:**
- Modify: `skills/ruyi-init/scripts/common.py`
- Modify: `skills/ruyi-init/scripts/init_write.py`
- Modify: `skills/ruyi-init/scripts/init_report.py`
- Modify: `skills/ruyi-init/SKILL.md`
- Modify locally for verification only: `skills/ruyi-init/scripts/tests/test_common.py`
- Modify locally for verification only: `skills/ruyi-init/scripts/tests/test_init_write.py`
- Modify locally for verification only: `skills/ruyi-init/scripts/tests/test_init_report.py`

- [ ] **Step 1: 写出失败测试，约束 schema v2 初始化结果**

在本地测试中新增断言：

```python
def test_init_writes_schema_v2_without_local_runtime_dirs(self):
    result = write_init(root, facts)
    self.assertIn("schema_version: 2", (root / ".ruyirc").read_text(encoding="utf-8"))
    self.assertFalse((root / ".ruyi" / "tasks").exists())
    self.assertFalse((root / ".ruyi" / "spec-candidates").exists())
    self.assertFalse((root / ".ruyi" / "spec-archive").exists())
    self.assertFalse((root / ".ruyi" / "spec-patches").exists())
    self.assertFalse((root / ".ruyi" / "workspace").exists())
    gitignore = (root / ".gitignore").read_text(encoding="utf-8")
    self.assertIn(".ruyi/tasks/**", gitignore)
    self.assertIn(".ruyi/spec-candidates/**", gitignore)
```

另加完整迁移断言：不再创建 `init-evaluation-notes.md`，baseline contract 仍创建成功。

- [ ] **Step 2: 运行 init 测试确认失败**

Run:

```powershell
python -m unittest discover skills/ruyi-init/scripts/tests -v
```

Expected: FAIL，原因包含旧目录仍被创建、`.ruyirc` 没有 `schema_version: 2` 或 report 仍引用 evaluation notes。

- [ ] **Step 3: 修改初始化常量和输出**

在 `common.py` 中将固定目录收敛为正式资产：

```python
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

LOCAL_GITIGNORE_RULES = (
    ".ruyi/tasks/**",
    ".ruyi/spec-candidates/**",
)
```

在 `init_write.py` 的 `.ruyirc` 模板头部加入：

```yaml
schema_version: 2
```

删除 `workspace_readme()`、`evaluation_notes()` 的写入路径，移除 project README 中的 `workspace / spec-archive / spec-patches` 说明，并将 `tasks / spec-candidates` 说明改为“本地按需创建”。

- [ ] **Step 4: 更新完整迁移报告与 skill 约束**

`init_report.py` 和 `ruyi-init/SKILL.md` 不再承诺 `workspace/init-evaluation-notes.md`；完整迁移产物仅保留 baseline contract、`docs-registry.md`、`interview-bank.md`。

- [ ] **Step 5: 重跑 init 测试**

Run:

```powershell
python -m unittest discover skills/ruyi-init/scripts/tests -v
```

Expected: PASS。

- [ ] **Step 6: 提交生产文件**

```powershell
git add skills/ruyi-init/scripts/common.py skills/ruyi-init/scripts/init_write.py skills/ruyi-init/scripts/init_report.py skills/ruyi-init/SKILL.md
git commit -m "Simplify Ruyi init schema v2 layout"
```

不要提交 `skills/ruyi-init/scripts/tests/`。

### Task 2: 新增 `ruyi-upgrade` 与 schema 迁移脚本

**Files:**
- Create: `skills/ruyi-upgrade/SKILL.md`
- Create: `skills/ruyi-upgrade/references/upgrade-discipline.md`
- Create: `skills/ruyi-upgrade/references/script-runtime-protocol.md`
- Create: `skills/ruyi-upgrade/scripts/upgrade_project.py`
- Create locally for verification only: `skills/ruyi-upgrade/scripts/tests/test_upgrade_project.py`

- [ ] **Step 1: 写出失败测试，覆盖自动迁移与删除确认边界**

测试入口约定为：

```python
result = upgrade_project(root, remove_obsolete=False)
```

核心断言：

```python
self.assertEqual(result["from_schema"], 1)
self.assertEqual(result["to_schema"], 2)
self.assertIn(".ruyi/workspace", result["obsolete_dirs"])
self.assertTrue((root / ".ruyi" / "workspace").exists())
self.assertIn(".ruyi/tasks/**", (root / ".gitignore").read_text(encoding="utf-8"))
self.assertIn("schema_version: 2", (root / ".ruyirc").read_text(encoding="utf-8"))
```

再写 `remove_obsolete=True` 删除目录、重复运行幂等、发现 `derived_from` / `conditionally-approved` 时仅报告不修改文件的测试。

- [ ] **Step 2: 运行新测试确认失败**

Run:

```powershell
python -m unittest discover skills/ruyi-upgrade/scripts/tests -v
```

Expected: FAIL，因为 skill 与迁移脚本尚不存在。

- [ ] **Step 3: 实现 schema 迁移脚本**

`upgrade_project.py` 以一个明确常量驱动迁移：

```python
CURRENT_SCHEMA_VERSION = 2
OBSOLETE_DIRS = (
    ".ruyi/workspace",
    ".ruyi/spec-archive",
    ".ruyi/spec-patches",
)

def upgrade_project(project_path: str | Path, *, remove_obsolete: bool = False) -> dict:
    """Upgrade deterministic Ruyi project structure; never rewrite business semantics."""
```

脚本职责：

- 读取 `.ruyirc`；未含 `schema_version` 时视为 schema v1。
- 执行 `v1 -> v2` 的幂等迁移。
- 替换 Ruyi 管理的旧 `.gitignore` 规则并加入本地 `tasks / spec-candidates` 规则。
- 识别但不修改旧 `derived_from` contract 与旧审批状态。
- 发现废弃目录时在 `obsolete_dirs` 中返回；仅当 `remove_obsolete=True` 时删除。
- 动态调用 `using-ruyi/scripts/index_rebuild.py` 重建 INDEX。

- [ ] **Step 4: 编写 upgrade skill**

`SKILL.md` 规定两阶段执行方式：

```text
1. 自动运行升级脚本但不删除废弃目录。
2. 若 obsolete_dirs 非空，只向用户询问是否删除这些目录。
3. 用户确认后再次执行 --remove-obsolete。
4. 输出已自动处理、已清理、需人工审视三段总结。
```

禁止 `ruyi-upgrade` 自动合并 contract、改写正式 spec 或判断旧审批业务含义。

- [ ] **Step 5: 运行 upgrade 测试**

Run:

```powershell
python -m unittest discover skills/ruyi-upgrade/scripts/tests -v
python -m py_compile skills/ruyi-upgrade/scripts/upgrade_project.py
```

Expected: PASS。

- [ ] **Step 6: 提交新 skill 生产文件**

```powershell
git add skills/ruyi-upgrade/SKILL.md skills/ruyi-upgrade/references/upgrade-discipline.md skills/ruyi-upgrade/references/script-runtime-protocol.md skills/ruyi-upgrade/scripts/upgrade_project.py
git commit -m "Add Ruyi project schema upgrade skill"
```

不要提交 `skills/ruyi-upgrade/scripts/tests/`。

### Task 3: 在 `using-ruyi` 前置升级门禁并移除本地 task 正式门禁

**Files:**
- Modify: `skills/using-ruyi/SKILL.md`
- Modify: `skills/using-ruyi/scripts/route_request.py`
- Modify: `skills/using-ruyi/scripts/index_rebuild.py`
- Modify locally for verification only: `skills/using-ruyi/scripts/tests/test_route_request.py`
- Modify locally for verification only: `skills/using-ruyi/scripts/tests/test_index_rebuild.py`

- [ ] **Step 1: 写出失败路由测试**

新增以下场景：

```python
def test_initialized_old_schema_routes_to_upgrade_before_requested_stage(self):
    self.write_ruyirc(root, schema_version=None)
    result = route_request(root, {"intent": "contract"})
    self.assertEqual(result["stage"], "upgrade")
    self.assertEqual(result["skill"], "ruyi-upgrade")

def test_test_no_longer_requires_local_done_task(self):
    self.write_confirmed_contract_and_plan(root)
    result = route_request(root, self.payload(intent="test"))
    self.assertEqual(result["stage"], "test")

def test_continue_resumes_in_progress_local_task(self):
    self.write_confirmed_contract_and_plan(root)
    self.write_task(root, status="in-progress")
    result = route_request(root, self.payload(intent="continue"))
    self.assertEqual(result["stage"], "implement")
    self.assertIn("task-in-progress", result["blockers"])
```

新增 INDEX 测试：`tasks/` 与 `spec-candidates/` 不再作为正式产物写入 INDEX。

- [ ] **Step 2: 运行 using-ruyi 测试确认失败**

Run:

```powershell
python -m unittest discover skills/using-ruyi/scripts/tests -v
```

Expected: FAIL，原因包含未识别 upgrade stage、仍要求 `done task` 或 INDEX 仍读取本地目录。

- [ ] **Step 3: 添加 upgrade stage 与 schema 读取**

`route_request.py` 增加：

```python
CURRENT_SCHEMA_VERSION = 2

STAGE_SKILLS = {
    "upgrade": "ruyi-upgrade",
    ...
}

def schema_version(project: Path) -> int:
    ...

def requires_upgrade(project: Path) -> bool:
    return schema_version(project) < CURRENT_SCHEMA_VERSION
```

在 `is_initialized()` 成立后、任何 intent 路由之前返回 `upgrade` stage；迁移完成后用户原请求再继续执行。

- [ ] **Step 4: 重写实现与继续路由的本地 task 规则**

删除 `intent == "test"` 对 `has_done_task()` 的硬阻拦。`continue` 只用本地 task 恢复当前位置：

```python
if has_in_progress_task(project, payload):
    return route("implement", ["task-in-progress"], "存在本地执行中的 task，继续完成当前 checkpoint。")
if not test.is_file():
    return route("implement", ["implementation-status-check-required"], "按 confirmed plan 核对实现完成情况后进入 test。")
```

正式阶段仍由 contract/plan/test/explain 状态控制，不依赖本地 task 是否存在。

- [ ] **Step 5: 从 INDEX 移除本地资产**

在 `index_rebuild.py` 中仅索引正式产物：

```python
SECTIONS = {
    "contracts": "contract",
    "plans": "plan",
    "tests": "test",
    "explain": "explain",
}
```

移除 `tasks` 和 `spec-candidates` 的路径解释及状态参与逻辑；`reopened` 与 `pending` 等新正式状态在后续任务同步加入排名。

- [ ] **Step 6: 更新 using-ruyi 文字路由表并验证**

更新 SKILL 中：

- 初始化后优先校验 schema 版本。
- `continue` 可读取同一 feature 的本地 task 恢复，但 task 不是 test 门禁。
- spec 沉淀不再要求自动生成 candidate。

Run:

```powershell
python -m unittest discover skills/using-ruyi/scripts/tests -v
python -m py_compile skills/using-ruyi/scripts/route_request.py skills/using-ruyi/scripts/index_rebuild.py
```

Expected: PASS。

- [ ] **Step 7: 提交生产文件**

```powershell
git add skills/using-ruyi/SKILL.md skills/using-ruyi/scripts/route_request.py skills/using-ruyi/scripts/index_rebuild.py
git commit -m "Route Ruyi projects through schema upgrades and local resumes"
```

### Task 4: 将 task 转为本地 checkpoint 机制

**Files:**
- Modify: `skills/ruyi-implement/SKILL.md`
- Modify: `skills/ruyi-implement/scripts/task_create.py`
- Create: `skills/ruyi-implement/scripts/task_checkpoint.py`
- Modify locally for verification only: `skills/ruyi-implement/scripts/tests/test_task_create.py`
- Create locally for verification only: `skills/ruyi-implement/scripts/tests/test_task_checkpoint.py`

- [ ] **Step 1: 写出失败测试，限制本地 task 生命周期**

覆盖以下行为：

```python
def test_task_directory_is_created_lazily_from_confirmed_plan(self):
    self.assertFalse((root / ".ruyi" / "tasks").exists())
    result = create_task(root, payload(status="pending"))
    self.assertTrue(result["created"])
    self.assertTrue(Path(result["path"]).is_file())

def test_task_statuses_only_support_checkpoint_states(self):
    with self.assertRaises(ValueError):
        create_task(root, payload(status="superseded"))

def test_checkpoint_updates_progress_without_rebuilding_index(self):
    result = update_checkpoint(root, task_path, status="in-progress", next_step="运行验证")
    self.assertTrue(result["updated"])
    self.assertNotIn("index", result)
```

- [ ] **Step 2: 运行 implement 测试确认失败**

Run:

```powershell
python -m unittest discover skills/ruyi-implement/scripts/tests -v
```

Expected: FAIL，因为 task 仍要求初始化时目录存在、仍允许旧状态且没有 checkpoint 更新脚本。

- [ ] **Step 3: 收缩 task 创建行为**

`task_create.py` 修改为：

```python
TASK_STATUSES = ("pending", "in-progress", "done")

def is_initialized(project: Path) -> bool:
    return (project / ".ruyirc").is_file() and (project / ".ruyi").is_dir()
```

在创建时懒加载 `.ruyi/tasks/...`。移除 `superseded_by`、INDEX 重建与正式质量凭证表述；保留 plan anchor 与当前进度段。

- [ ] **Step 4: 增加 checkpoint 更新脚本**

`task_checkpoint.py` 只更新指定本地 task 的 frontmatter 与 `## 当前进度`：

```python
CHECKPOINT_STATUSES = ("pending", "in-progress", "done")

def update_checkpoint(project_path: str | Path, task_path: str | Path, payload: dict[str, Any]) -> dict:
    """Update local execution progress; never update formal Ruyi artifacts or INDEX."""
```

CLI 支持 `--status`、`--completed-step`、`--current`、`--next-step`、`--modified-file`、`--verification`、`--blocker`。

- [ ] **Step 5: 更新 implement 纪律并验证**

`ruyi-implement/SKILL.md` 明确：多 task 或预计跨轮实现必须在首次改源码前创建 checkpoint；结束回复、完成文件组和运行验证后更新 checkpoint；共享质量结论进入 test/explain。

Run:

```powershell
python -m unittest discover skills/ruyi-implement/scripts/tests -v
python -m py_compile skills/ruyi-implement/scripts/task_create.py skills/ruyi-implement/scripts/task_checkpoint.py
```

Expected: PASS。

- [ ] **Step 6: 提交生产文件**

```powershell
git add skills/ruyi-implement/SKILL.md skills/ruyi-implement/scripts/task_create.py skills/ruyi-implement/scripts/task_checkpoint.py
git commit -m "Make Ruyi tasks local execution checkpoints"
```

### Task 5: 实现已审批需求重新打开与最小状态模型

**Files:**
- Modify: `skills/ruyi-contract/SKILL.md`
- Modify: `skills/ruyi-contract/scripts/contract_create.py`
- Create: `skills/ruyi-contract/scripts/reopen_delivery.py`
- Modify: `skills/ruyi-plan/scripts/plan_create.py`
- Modify: `skills/ruyi-test/scripts/test_create.py`
- Modify: `skills/ruyi-explain/scripts/explain_create.py`
- Modify: `skills/ruyi-explain/scripts/explain_lint.py`
- Modify: `skills/ruyi-approve/SKILL.md`
- Modify: `skills/ruyi-approve/scripts/approve_update.py`
- Modify: `skills/using-ruyi/scripts/route_request.py`
- Modify locally: corresponding `skills/*/scripts/tests/test_*.py`

- [ ] **Step 1: 写出失败测试，覆盖类型 D 重开与状态收缩**

测试场景：

```python
def test_reopen_delivery_reuses_existing_contract_and_resets_current_outputs(self):
    self.write_approved_chain(root)
    result = reopen_delivery(root, payload(return_stage="contract", reason="需求澄清遗漏"))
    self.assertEqual(parse(contract)["status"], "reopened")
    self.assertEqual(parse(test)["result"], "pending")
    self.assertEqual(parse(explain)["approval"], "pending")
    self.assertFalse(any(contract.parent.glob("*.derived.md")))

def test_approve_rejects_removed_approval_states(self):
    with self.assertRaises(ValueError):
        update_approval(root, payload(status="conditionally-approved"))

def test_reopened_contract_does_not_enter_plan_until_reconfirmed(self):
    result = route_request(root, self.payload(intent="continue"))
    self.assertEqual(result["stage"], "contract")
```

另写更新同路径 `test` 与 `explain` 时保留返工记录、替换当前内容的测试。

- [ ] **Step 2: 运行相关测试确认失败**

Run:

```powershell
python -m unittest discover skills/ruyi-contract/scripts/tests -v
python -m unittest discover skills/ruyi-plan/scripts/tests -v
python -m unittest discover skills/ruyi-test/scripts/tests -v
python -m unittest discover skills/ruyi-explain/scripts/tests -v
python -m unittest discover skills/ruyi-approve/scripts/tests -v
python -m unittest discover skills/using-ruyi/scripts/tests -v
```

Expected: FAIL，原因包含缺少 `reopened / pending`、仍接受旧审批状态、仍要求类型 D 新建 contract。

- [ ] **Step 3: 扩展 contract 当前状态与重开脚本**

`contract_create.py` 将状态设为：

```python
CONTRACT_STATUSES = ("draft", "confirmed", "reopened")
```

新增 `reopen_delivery.py`，一次重开操作必须：

- 将原 contract frontmatter 更新为 `status: reopened`。
- 在原 contract 追加 `## 返工记录`。
- 按 `return_stage` 判断是否将原 plan 改为 `draft` 并追加状态记录。
- 将存在的原 test 改为 `result: pending`。
- 将存在的原 explain 改为 `approval: pending`，移除旧 `return_stage`。
- 不创建新 contract，不写 `derived_from`。

- [ ] **Step 4: 允许同路径正式产物在返工后重写当前内容**

对 `plan_create.py`、`test_create.py`、`explain_create.py` 采用相同保护规则：

```text
不存在文件：按原逻辑创建
文件当前状态为 draft / pending 且含返工记录：允许更新当前有效正文，保留返工记录
已 confirmed / passed / approved 且没有再次重开：拒绝覆盖
```

`reopen_delivery.py` 负责写入过渡状态 `result: pending`；读取和路由逻辑必须能识别该状态。`test_create.py` 的用户产出结果仍只接受 `passed / passed-with-notes / failed`，但在现有文件为 `pending` 且已记录返工时，允许以本次正式验证结果覆盖当前正文。

- [ ] **Step 5: 收缩 approval 状态与更新路由**

`approve_update.py` 改为：

```python
APPROVAL_STATUSES = ("approved", "changes-requested")
```

`using-ruyi` 的 A/B/C/D 文案与脚本规则调整为：

- D = 已审批原需求重开；
- `contract.status == reopened` 时返回 contract 澄清；
- `test.result == pending` 时返回 test；
- `explain.approval == pending` 时返回 approve；
- 不再判断 `conditionally-approved / rejected` 的新产出路径。

- [ ] **Step 6: 运行状态流测试与编译验证**

Run:

```powershell
python -m unittest discover skills/ruyi-contract/scripts/tests -v
python -m unittest discover skills/ruyi-plan/scripts/tests -v
python -m unittest discover skills/ruyi-test/scripts/tests -v
python -m unittest discover skills/ruyi-explain/scripts/tests -v
python -m unittest discover skills/ruyi-approve/scripts/tests -v
python -m unittest discover skills/using-ruyi/scripts/tests -v
python -m py_compile skills/ruyi-contract/scripts/contract_create.py skills/ruyi-contract/scripts/reopen_delivery.py skills/ruyi-plan/scripts/plan_create.py skills/ruyi-test/scripts/test_create.py skills/ruyi-explain/scripts/explain_create.py skills/ruyi-explain/scripts/explain_lint.py skills/ruyi-approve/scripts/approve_update.py skills/using-ruyi/scripts/route_request.py
```

Expected: PASS。

- [ ] **Step 7: 提交生产文件**

```powershell
git add skills/ruyi-contract/SKILL.md skills/ruyi-contract/scripts/contract_create.py skills/ruyi-contract/scripts/reopen_delivery.py skills/ruyi-plan/scripts/plan_create.py skills/ruyi-test/scripts/test_create.py skills/ruyi-explain/scripts/explain_create.py skills/ruyi-explain/scripts/explain_lint.py skills/ruyi-approve/SKILL.md skills/ruyi-approve/scripts/approve_update.py skills/using-ruyi/scripts/route_request.py
git commit -m "Reopen approved Ruyi deliveries without new contracts"
```

### Task 6: 简化 spec candidate 处理链

**Files:**
- Modify: `skills/ruyi-spec-evolve/SKILL.md`
- Modify: `skills/ruyi-spec-evolve/scripts/candidate_create.py`
- Modify: `skills/ruyi-spec-discover/SKILL.md`
- Modify: `skills/ruyi-spec-merge/SKILL.md`
- Modify: `skills/ruyi-spec-merge/scripts/merge_apply.py`
- Modify: `skills/ruyi-spec-merge/scripts/merge_common.py`
- Modify locally: `skills/ruyi-spec-evolve/scripts/tests/test_candidate_create.py`
- Modify locally: `skills/ruyi-spec-merge/scripts/tests/test_spec_merge.py`

- [ ] **Step 1: 写出失败测试，约束 candidate 仅为 pending 暂存**

新增断言：

```python
def test_candidate_is_created_lazily_without_archive_side_effects(self):
    result = create_candidate(root, payload)
    self.assertTrue(result["created"])
    self.assertFalse((root / ".ruyi" / "spec-archive").exists())

def test_resolved_candidate_is_deleted_without_patch_or_archive(self):
    result = apply_merge(root, candidate, decision="merged", reason="用户确认正式规则已写入")
    self.assertTrue(result["updated"])
    self.assertFalse(candidate.exists())
    self.assertFalse((root / ".ruyi" / "spec-patches").exists())
    self.assertFalse((root / ".ruyi" / "spec-archive").exists())
```

- [ ] **Step 2: 运行 spec 测试确认失败**

Run:

```powershell
python -m unittest discover skills/ruyi-spec-evolve/scripts/tests -v
python -m unittest discover skills/ruyi-spec-merge/scripts/tests -v
```

Expected: FAIL，因为当前脚本仍生成 archive/patch 与终态 candidate。

- [ ] **Step 3: 收缩 candidate 创建与解决行为**

`candidate_create.py`：

- 初始化判断只要求 `.ruyirc` 与 `.ruyi/`，创建 candidate 时懒建目录。
- 删除 `supersede_existing_candidates()` 及 archive 写入。
- 已有同目标 pending candidate 时返回“先处理当前候选”，不创建候选历史。

`merge_apply.py`：

- 只接受待处理 candidate。
- `merged` 前由 skill 要求 agent 已按用户确认更新目标正式 spec；脚本校验目标文件存在后删除 candidate。
- `rejected` 或无效 candidate 直接删除。
- 不再生成 patch、archive 或终态 candidate。

- [ ] **Step 4: 更新 spec skills 的用户动作顺序**

`ruyi-spec-evolve` 改为优先向用户提议直接更新正式 spec，只有“稍后处理”才创建 candidate。`ruyi-spec-discover` 保留大批量反推暂存能力。`ruyi-spec-merge` 负责确认、更新正式 spec、删除 candidate。

- [ ] **Step 5: 运行验证并提交**

Run:

```powershell
python -m unittest discover skills/ruyi-spec-evolve/scripts/tests -v
python -m unittest discover skills/ruyi-spec-merge/scripts/tests -v
python -m py_compile skills/ruyi-spec-evolve/scripts/candidate_create.py skills/ruyi-spec-merge/scripts/merge_apply.py skills/ruyi-spec-merge/scripts/merge_common.py
```

Expected: PASS。

```powershell
git add skills/ruyi-spec-evolve/SKILL.md skills/ruyi-spec-evolve/scripts/candidate_create.py skills/ruyi-spec-discover/SKILL.md skills/ruyi-spec-merge/SKILL.md skills/ruyi-spec-merge/scripts/merge_apply.py skills/ruyi-spec-merge/scripts/merge_common.py
git commit -m "Simplify Ruyi spec candidate resolution"
```

### Task 7: 同步 published references 与用户文档

**Files:**
- Modify: `README.md`
- Modify: `docs/install.md`
- Modify: all applicable `skills/*/references/contract-schema.md`
- Modify: all applicable `skills/*/references/plan-schema.md`
- Modify: all applicable `skills/*/references/task-schema.md`
- Modify: all applicable `skills/*/references/test-schema.md`
- Modify: all applicable `skills/*/references/explain-schema.md`
- Modify: all applicable `skills/*/references/approval-schema.md`
- Modify: all applicable `skills/*/references/main-flow.md`
- Modify: all applicable `skills/*/references/spec-candidate-schema.md`
- Modify: all applicable `skills/*/references/spec-merge-protocol.md`
- Modify: all applicable `skills/*/references/knowledge-evolution.md`
- Modify locally: skill documentation tests where already present

- [ ] **Step 1: 写出文档约束测试或文本扫描断言**

在现有本地文档测试中加入断言，或使用明确的扫描命令检出旧语义：

```powershell
rg -n "workspace/|spec-archive|spec-patches|derived_from|conditionally-approved|pending-manual-merge|必须.*done task|生成 spec candidate" skills README.md docs/install.md
```

Expected before implementation: 命中需要迁移的旧协议说明。

- [ ] **Step 2: 同步所有 reference 副本**

统一更新以下语义：

- task 为本地 `pending / in-progress / done` checkpoint。
- contract 包含 `reopened`，类型 D 不再新建 contract。
- test 包含返工后的 `pending`。
- approval 仅 `pending / approved / changes-requested`。
- candidate 仅本地 `pending`，解决后删除。
- 不再出现 `workspace / spec-archive / spec-patches` 的现行流程描述。
- `ruyi-upgrade` 和 `schema_version` 纳入主流程与安装说明。

- [ ] **Step 3: 更新 README 与安装说明**

更新结构树、主流程、安装后的升级路径及已接入项目升级命令说明。明确 `ruyi-upgrade` 会自动迁移结构，但删除废弃目录时询问一次。

- [ ] **Step 4: 扫描旧语义并处理允许保留的迁移说明**

Run:

```powershell
rg -n "workspace/|spec-archive|spec-patches|derived_from|conditionally-approved|pending-manual-merge|必须.*done task|生成 spec candidate" skills README.md docs/install.md
```

Expected: 只剩 `ruyi-upgrade` 的“检测旧产物/旧状态并提示处理”描述，不再存在仍指导新流程使用旧结构的文本。

- [ ] **Step 5: 提交文档与 published references**

```powershell
git diff --name-only -- README.md docs/install.md skills
git add README.md docs/install.md
# 按上一步列出的实际变更显式 git add 对应 skills 路径，不使用覆盖整个目录的通配符。
git diff --cached --name-only
git commit -m "Synchronize Ruyi schema v2 skill references"
```

执行 `git diff --cached --name-only` 前确认不会误暂存用户已有的 `CHANGELOG.md`。

### Task 8: 全量回归与准备发布

**Files:**
- Review only: all production files modified in Tasks 1-7
- Review separately: `CHANGELOG.md` existing workspace changes

- [ ] **Step 1: 执行语法检查**

Run:

```powershell
python -m py_compile skills/ruyi-init/scripts/common.py skills/ruyi-init/scripts/init_write.py skills/ruyi-init/scripts/init_report.py skills/ruyi-upgrade/scripts/upgrade_project.py skills/using-ruyi/scripts/route_request.py skills/using-ruyi/scripts/index_rebuild.py skills/ruyi-contract/scripts/contract_create.py skills/ruyi-contract/scripts/reopen_delivery.py skills/ruyi-plan/scripts/plan_create.py skills/ruyi-implement/scripts/task_create.py skills/ruyi-implement/scripts/task_checkpoint.py skills/ruyi-test/scripts/test_create.py skills/ruyi-explain/scripts/explain_create.py skills/ruyi-explain/scripts/explain_lint.py skills/ruyi-approve/scripts/approve_update.py skills/ruyi-spec-evolve/scripts/candidate_create.py skills/ruyi-spec-merge/scripts/merge_apply.py skills/ruyi-spec-merge/scripts/merge_common.py
```

Expected: exit code `0`。

- [ ] **Step 2: 执行所有本地 skill 单元测试**

Run:

```powershell
Get-ChildItem skills -Directory | ForEach-Object {
  $testDir = Join-Path $_.FullName 'scripts\tests'
  if (Test-Path $testDir) {
    Write-Host "== $($_.Name) =="
    python -m unittest discover $testDir -v
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  }
}
```

Expected: 每组测试均为 `OK`。

- [ ] **Step 3: 执行差异与污染检查**

Run:

```powershell
git diff --check
git status --short --ignored
git diff --name-only
```

Expected:

- 无 whitespace error。
- `skills/*/scripts/tests/` 如有改动仍为 ignored/local-only，不进入待提交生产 diff。
- `CHANGELOG.md` 若仍存在用户工作区修改，单独展示并保留，不混入实现 commit。

- [ ] **Step 4: 运行两个端到端 fixture 验证**

在本地 fixture 中验证：

```text
旧 schema 项目 -> using-ruyi 路由 upgrade -> 自动迁移 -> 确认删除废弃目录 -> 继续原请求
approved 需求 -> 类型 D reopen -> 同一路径 contract/test/explain 状态回退 -> 重验 -> 再审批
```

Expected: 结构迁移与业务返工均符合设计文档，且本地 task 可恢复长 plan 进度。

- [ ] **Step 5: 单独审视 release note 与发布范围**

只有进入发布步骤后，才读取并对比当前 `CHANGELOG.md` 工作区修改，决定是否保留、补充或重新组织；不得在实现提交中隐式覆盖该文件。
