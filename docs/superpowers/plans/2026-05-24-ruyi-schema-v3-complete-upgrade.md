# Ruyi Schema v3 Complete Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 落地 Ruyi schema v3，使新项目直接使用无 explain、双 INDEX、拆分 baseline 的结构，并让存量项目完整升级到当前协议。

**Architecture:** 以 `schema_version: 3` 为硬门禁，`using-ruyi` 在任何阶段路由前先触发 `ruyi-upgrade`。正式团队资产只保留 `contracts / plans / tests / spec / INDEX.md`，`test` 同时承载验证与审批，`ruyi-upgrade` 负责把旧 explain、旧 spec 业务事实、旧入口文件和旧索引完整迁移到 v3。

**Tech Stack:** Markdown skills 与 references、Python 3 标准库脚本、`unittest` 本地验证、Git。

---

## 实施边界

- 设计依据：[2026-05-23-ruyi-schema-v3-complete-upgrade-and-index-design.md](D:/AIWorks/ruyi/docs/superpowers/specs/2026-05-23-ruyi-schema-v3-complete-upgrade-and-index-design.md)。
- `skills/*/scripts/tests/` 和 `fixtures/` 只做本地验证，继续保持 ignored，不提交 GitHub。
- 当前工作区已有用户改动 [CHANGELOG.md](D:/AIWorks/ruyi/CHANGELOG.md)，实现阶段不得暂存、覆盖或提交，直到用户明确进入 release note 发布处理。
- 所有 schema/reference 语义变更必须同步各 skill-local copies；不能只改一个 skill 的副本。
- v3 不保留兼容入口：旧 `frontend-baseline.md` 拆分后删除，旧 `.ruyi/explain/` 迁移后删除，旧二级 spec INDEX 合并后删除。

## 文件职责映射

| 单元 | 生产文件 | 职责 |
| --- | --- | --- |
| Init v3 | `skills/ruyi-init/scripts/common.py`、`skills/ruyi-init/scripts/init_write.py`、`skills/ruyi-init/scripts/init_report.py`、`skills/ruyi-init/SKILL.md` | 新项目创建 v3 目录、两个正式 INDEX、拆分 baseline，不再创建 explain 和二级 spec INDEX |
| Router / Index | `skills/using-ruyi/SKILL.md`、`skills/using-ruyi/scripts/route_request.py`、`skills/using-ruyi/scripts/index_rebuild.py` | schema v3 门禁、无 explain 主流程、根 INDEX 只索引 contract/plan/test |
| Test / Approve | `skills/ruyi-test/SKILL.md`、`skills/ruyi-test/scripts/test_create.py`、`skills/ruyi-approve/SKILL.md`、`skills/ruyi-approve/scripts/approve_update.py` | test 成为验证与审批载体，approve 直接更新 test |
| Explain removal | `skills/ruyi-explain/SKILL.md` 及发布结构 | 主流程移除或改为废弃提示，不再生成正式 explain |
| Upgrade v3 | `skills/ruyi-upgrade/SKILL.md`、`skills/ruyi-upgrade/scripts/upgrade_project.py` | legacy v1/v2 直接完整迁移到 v3，处理旧 baseline、旧 explain、旧 spec、旧入口文件和删除废弃目录 |
| Contract / Plan boundary | `skills/ruyi-contract/SKILL.md`、`skills/ruyi-contract/references/contract-discipline.md`、`skills/ruyi-plan/SKILL.md`、`skills/ruyi-plan/references/planning-discipline.md` | contract 只吸收业务约束，实施设计提醒进入 plan；plan 发现需求变化退回 contract |
| Spec / candidate | `skills/ruyi-spec-discover/SKILL.md`、`skills/ruyi-spec-evolve/SKILL.md`、`skills/ruyi-spec-merge/SKILL.md`、相关 scripts 与 references | 使用 `.ruyi/spec/INDEX.md` 作为唯一 spec 入口，candidate local-only，正式 spec 变更同步索引 |
| Published docs | `README.md`、`docs/install.md`、所有相关 `skills/*/references/*.md` | 对外说明与 skill-local 协议副本同步到 v3 |

### Task 1: Init 直接生成 schema v3 项目结构

**Files:**
- Modify: `skills/ruyi-init/scripts/common.py`
- Modify: `skills/ruyi-init/scripts/init_write.py`
- Modify: `skills/ruyi-init/scripts/init_report.py`
- Modify: `skills/ruyi-init/SKILL.md`
- Modify locally only: `skills/ruyi-init/scripts/tests/test_common.py`
- Modify locally only: `skills/ruyi-init/scripts/tests/test_init_write.py`
- Modify locally only: `skills/ruyi-init/scripts/tests/test_init_report.py`

- [ ] **Step 1: 写失败测试约束新 init 结构**

新增断言：

```python
def test_init_writes_schema_v3_without_explain_or_second_level_spec_indexes(self):
    result = write_init(root, facts)
    self.assertIn("schema_version: 3", (root / ".ruyirc").read_text(encoding="utf-8"))
    self.assertTrue((root / ".ruyi" / "INDEX.md").is_file())
    self.assertTrue((root / ".ruyi" / "spec" / "INDEX.md").is_file())
    self.assertFalse((root / ".ruyi" / "explain").exists())
    self.assertFalse((root / ".ruyi" / "spec" / "frontend-baseline.md").exists())
    self.assertFalse((root / ".ruyi" / "spec" / "references" / "shared" / "INDEX.md").exists())
    self.assertFalse((root / ".ruyi" / "spec" / "references" / "modules" / "INDEX.md").exists())
```

同时断言 `development-baseline.md`、`coding-baseline.md`、`testing-baseline.md` 存在，且 `.gitignore` 仍忽略 `.ruyi/tasks/**` 和 `.ruyi/spec-candidates/**`。

- [ ] **Step 2: 运行 init 测试确认失败**

Run:

```powershell
python -m unittest discover skills/ruyi-init/scripts/tests -v
```

Expected: FAIL，当前实现仍是 schema v2 或仍创建 `explain/`、旧二级 spec INDEX。

- [ ] **Step 3: 修改 init 常量与写入模板**

将正式目录收敛为：

```python
REQUIRED_RUYI_DIRS = (
    ".ruyi",
    ".ruyi/contracts",
    ".ruyi/plans",
    ".ruyi/tests",
    ".ruyi/spec",
    ".ruyi/spec/references",
    ".ruyi/spec/references/shared",
    ".ruyi/spec/references/modules",
)

LOCAL_GITIGNORE_RULES = (
    ".ruyi/tasks/**",
    ".ruyi/spec-candidates/**",
)
```

`.ruyirc` 写入 `schema_version: 3`。删除 `frontend-baseline.md`、`explain/`、`spec/references/shared/INDEX.md`、`spec/references/modules/INDEX.md` 的生成逻辑，新增 `.ruyi/spec/INDEX.md` 模板。

- [ ] **Step 4: 更新 init 引导文本**

`ruyi-init/SKILL.md` 明确：

- 快速开始：创建最小 v3 结构和 baseline。
- 完整迁移：只读取 agent 可访问的本地文本文件，或通过用户已有浏览器工具读取外部文档；不保存不可复用的本地临时文档地址。
- 完整迁移产出当前业务事实 baseline contract，不批量补历史 contract。
- 新项目入口文件指向 `.ruyi/INDEX.md` 和 `.ruyi/spec/INDEX.md`，不再提 explain。

- [ ] **Step 5: 验证并提交**

Run:

```powershell
python -m unittest discover skills/ruyi-init/scripts/tests -v
python -m py_compile skills/ruyi-init/scripts/common.py skills/ruyi-init/scripts/init_write.py skills/ruyi-init/scripts/init_report.py
```

Expected: PASS。

Commit:

```powershell
git add skills/ruyi-init/scripts/common.py skills/ruyi-init/scripts/init_write.py skills/ruyi-init/scripts/init_report.py skills/ruyi-init/SKILL.md
git commit -m "Create Ruyi schema v3 projects from init"
```

### Task 2: Router 与根 INDEX 切到无 explain 主流程

**Files:**
- Modify: `skills/using-ruyi/SKILL.md`
- Modify: `skills/using-ruyi/scripts/route_request.py`
- Modify: `skills/using-ruyi/scripts/index_rebuild.py`
- Modify locally only: `skills/using-ruyi/scripts/tests/test_route_request.py`
- Modify locally only: `skills/using-ruyi/scripts/tests/test_index_rebuild.py`

- [ ] **Step 1: 写失败测试覆盖 v3 路由**

新增断言：

```python
def test_old_schema_routes_to_upgrade_before_any_stage(self):
    self.write_ruyirc(root, schema_version=2)
    result = route_request(root, {"intent": "contract"})
    self.assertEqual(result["stage"], "upgrade")
    self.assertEqual(result["skill"], "ruyi-upgrade")

def test_standard_delivery_routes_from_passed_test_to_approve_without_explain(self):
    self.write_confirmed_contract_plan_and_passed_test(root, approval="pending")
    result = route_request(root, {"intent": "continue", "module": "orders", "feature": "search", "date": "2026-05-24"})
    self.assertEqual(result["stage"], "approve")

def test_approved_test_completes_delivery(self):
    self.write_confirmed_contract_plan_and_passed_test(root, approval="approved")
    result = route_request(root, {"intent": "continue", "module": "orders", "feature": "search", "date": "2026-05-24"})
    self.assertEqual(result["stage"], "complete")
```

`index_rebuild` 新增断言：根 INDEX 只来自 `contracts / plans / tests`，不扫描 `explain / tasks / spec-candidates`。

- [ ] **Step 2: 运行 using-ruyi 测试确认失败**

Run:

```powershell
python -m unittest discover skills/using-ruyi/scripts/tests -v
```

Expected: FAIL，当前路由仍会进入 explain 或 INDEX 仍提到 explain。

- [ ] **Step 3: 实现 schema v3 门禁与无 explain 路由**

在 `route_request.py` 中更新：

```python
CURRENT_SCHEMA_VERSION = 3
STAGE_SKILLS["upgrade"] = "ruyi-upgrade"
```

路由顺序调整为：

1. 未初始化 -> `ruyi-init`。
2. schema 缺失或 `< 3` -> `ruyi-upgrade`。
3. 缺 contract -> `ruyi-contract`。
4. contract 不是 `confirmed` -> `ruyi-contract`。
5. standard/large 缺 plan -> `ruyi-plan`。
6. 缺 test 或 test failed/pending -> `ruyi-implement` 或 `ruyi-test`，按当前实现状态判断。
7. test passed/passed-with-notes 且 approval pending -> `ruyi-approve`。
8. test approval approved -> complete。
9. tiny 在 test passed 后 complete，不强制 approve。

- [ ] **Step 4: 重建根 INDEX 格式**

`index_rebuild.py` 只扫描：

```python
FORMAL_SECTIONS = ("contracts", "plans", "tests")
```

根 INDEX 输出每个 feature 的 contract、plan、test 路径和 `contract.status / test.result / test.approval`，不写 task/candidate/explain。

- [ ] **Step 5: 更新 using-ruyi 文本路由表**

删除“生成开发简报 / explain”主流程入口。保留 `ruyi-explain` 只作为已废弃提示时，不再被 using-ruyi 正常路由。

- [ ] **Step 6: 验证并提交**

Run:

```powershell
python -m unittest discover skills/using-ruyi/scripts/tests -v
python -m py_compile skills/using-ruyi/scripts/route_request.py skills/using-ruyi/scripts/index_rebuild.py
```

Expected: PASS。

Commit:

```powershell
git add skills/using-ruyi/SKILL.md skills/using-ruyi/scripts/route_request.py skills/using-ruyi/scripts/index_rebuild.py
git commit -m "Route Ruyi schema v3 without explain"
```

### Task 3: Test 承载验证与审批，Approve 直接更新 Test

**Files:**
- Modify: `skills/ruyi-test/SKILL.md`
- Modify: `skills/ruyi-test/scripts/test_create.py`
- Modify: `skills/ruyi-approve/SKILL.md`
- Modify: `skills/ruyi-approve/scripts/approve_update.py`
- Modify: `skills/ruyi-approve/references/approval-discipline.md`
- Modify locally only: `skills/ruyi-test/scripts/tests/test_test_create.py`
- Modify locally only: `skills/ruyi-approve/scripts/tests/test_approve_update.py`

- [ ] **Step 1: 写失败测试覆盖 test approval 字段**

`test_create.py` 新增或调整断言：

```python
def test_created_test_contains_pending_approval_for_standard_delivery(self):
    result = create_test(root, payload(result="passed"))
    text = Path(result["path"]).read_text(encoding="utf-8")
    self.assertIn("approval: pending", text)
    self.assertIn("## 验收与证据", text)
    self.assertIn("## 结论", text)
```

`approve_update.py` 新增断言：

```python
def test_approve_updates_test_not_explain(self):
    self.write_test(root, result="passed", approval="pending")
    result = update_approval(root, payload(status="approved"))
    self.assertTrue(result["updated"])
    self.assertEqual(parse_frontmatter(test_path)["approval"], "approved")
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```powershell
python -m unittest discover skills/ruyi-test/scripts/tests -v
python -m unittest discover skills/ruyi-approve/scripts/tests -v
```

Expected: FAIL，当前审批目标仍是 explain。

- [ ] **Step 3: 更新 test schema 与生成脚本**

`test_create.py` 的 frontmatter 至少包含：

```yaml
result: passed | passed-with-notes | failed | pending
approval: pending
contract: .ruyi/contracts/<module>/<feature>/<date>.md
plan: .ruyi/plans/<module>/<feature>/<date>.md
```

tiny 可以没有 plan，但 standard/large 必须有 plan。正文保持最小结构：

```md
# Test：[功能名称]

## 验收与证据
## 结论
```

仅当影响审批时才写失败项、未覆盖项或风险，不生成空章节。

- [ ] **Step 4: 改造 approve_update.py**

将目标路径从 `.ruyi/explain/...` 改为 `.ruyi/tests/...`。校验规则：

- test 存在。
- `result` 为 `passed` 或 `passed-with-notes` 才能 approve。
- 当前 `approval` 必须为 `pending`。
- `status` 只允许 `approved | changes-requested`。
- `changes-requested` 必须带 `return_stage`，取值 `contract | plan | implement | test`。

- [ ] **Step 5: 更新 test/approve skill 说明**

`ruyi-test` 通过后进入 approve，不再进入 explain。`ruyi-approve` 审批当前 test，审批备注追加到 test 正文。

- [ ] **Step 6: 验证并提交**

Run:

```powershell
python -m unittest discover skills/ruyi-test/scripts/tests -v
python -m unittest discover skills/ruyi-approve/scripts/tests -v
python -m py_compile skills/ruyi-test/scripts/test_create.py skills/ruyi-approve/scripts/approve_update.py
```

Expected: PASS。

Commit:

```powershell
git add skills/ruyi-test/SKILL.md skills/ruyi-test/scripts/test_create.py skills/ruyi-approve/SKILL.md skills/ruyi-approve/scripts/approve_update.py skills/ruyi-approve/references/approval-discipline.md
git commit -m "Approve Ruyi deliveries through test"
```

### Task 4: Upgrade v3 完整迁移存量项目

**Files:**
- Modify: `skills/ruyi-upgrade/SKILL.md`
- Modify: `skills/ruyi-upgrade/scripts/upgrade_project.py`
- Modify locally only: `skills/ruyi-upgrade/scripts/tests/test_upgrade_project.py`

- [ ] **Step 1: 写 legacy v1/v2 到 v3 的失败测试**

覆盖以下 fixture 场景：

```python
def test_legacy_v1_project_upgrades_directly_to_v3(self):
    self.write_ruyirc(root, schema_version=None)
    result = upgrade_project(root, remove_obsolete=True)
    self.assertEqual(result["from_schema"], 1)
    self.assertEqual(result["to_schema"], 3)
    self.assertIn("schema_version: 3", (root / ".ruyirc").read_text(encoding="utf-8"))
```

```python
def test_upgrade_removes_explain_after_migrating_approval_to_test(self):
    self.write_v2_chain_with_explain(root, approval="approved")
    result = upgrade_project(root, remove_obsolete=True)
    self.assertFalse((root / ".ruyi" / "explain").exists())
    self.assertEqual(parse_frontmatter(test_path)["approval"], "approved")
```

```python
def test_upgrade_splits_frontend_baseline_and_deletes_old_file(self):
    self.write_frontend_baseline(root)
    result = upgrade_project(root, remove_obsolete=True)
    self.assertFalse((root / ".ruyi" / "spec" / "frontend-baseline.md").exists())
    self.assertTrue((root / ".ruyi" / "spec" / "development-baseline.md").is_file())
    self.assertTrue((root / ".ruyi" / "spec" / "coding-baseline.md").is_file())
```

再覆盖二级 spec INDEX 合并、旧 spec 业务事实迁移到 baseline contract、入口文件去 explain 引用、废弃目录删除。

- [ ] **Step 2: 运行 upgrade 测试确认失败**

Run:

```powershell
python -m unittest discover skills/ruyi-upgrade/scripts/tests -v
```

Expected: FAIL，当前脚本仍是 schema v2 迁移。

- [ ] **Step 3: 提升 upgrade 常量与迁移管线**

`upgrade_project.py` 更新：

```python
CURRENT_SCHEMA_VERSION = 3
OBSOLETE_DIRS = (
    ".ruyi/explain",
    ".ruyi/workspace",
    ".ruyi/spec-archive",
    ".ruyi/spec-patches",
)
```

将 `upgrade_project()` 拆成小函数：

```python
def migrate_ruyirc(project: Path, result: dict) -> None: ...
def migrate_gitignore(project: Path, result: dict) -> None: ...
def migrate_spec_baselines(project: Path, result: dict) -> None: ...
def merge_spec_indexes(project: Path, result: dict) -> None: ...
def migrate_spec_business_facts(project: Path, result: dict) -> None: ...
def migrate_explain_to_tests(project: Path, result: dict) -> None: ...
def migrate_entry_files(project: Path, result: dict) -> None: ...
def remove_obsolete_dirs(project: Path, result: dict, *, remove_obsolete: bool) -> None: ...
def rebuild_indexes(project: Path, result: dict) -> None: ...
```

每个函数只处理一个责任，避免 `upgrade_project.py` 失控。

- [ ] **Step 4: 实现 spec baseline 与 INDEX 迁移**

规则：

- `frontend-baseline.md` 中含 lint/build/test/git 操作的段落进入 `development-baseline.md`。
- 组件、状态、样式、类型、接口、错误处理规则进入 `coding-baseline.md`。
- 无法分类的长期问题进入 `open-questions.md`，并在 result 中记录 `needs_user_decision`。
- `spec/references/shared/INDEX.md` 与 `spec/references/modules/INDEX.md` 的有效路径合并到 `.ruyi/spec/INDEX.md` 后删除。

若脚本不能可靠分类，必须报告问题并要求用户在升级流程内选择，不能把项目标为 v3 后遗留旧入口。

- [ ] **Step 5: 实现旧 spec 业务事实迁移**

自动迁移只处理明显模式，例如文件或标题包含 `business facts / current behavior / existing behavior / 当前业务事实 / 现状 / 已有能力`。目标路径：

```text
.ruyi/contracts/<module>/_baseline/current.md
.ruyi/contracts/<module>/<feature>/baseline.md
```

不确定段落写入 `needs_user_decision`，由 `ruyi-upgrade` 在对话中询问后继续完成。

- [ ] **Step 6: 实现 explain -> test 迁移与 explain 删除**

将旧 explain 的有效信息迁入对应 test：

- `approval`、审批说明、return stage -> test frontmatter 与审批段。
- 验证结论若 test 缺失则补入 test；若 test 已有，以 test 为主，只补审批相关信息。
- 长期风险或未决项迁入 `.ruyi/spec/open-questions.md`。
- 迁移完成后删除 `.ruyi/explain/`。

- [ ] **Step 7: 迁移项目入口文件**

更新 Ruyi 管理段落：

- `CLAUDE.md`
- `.claude/settings.json`
- `.claude/commands/ruyi.md`
- `.ruyi/project-actions.md`

去除 explain、旧 INDEX、旧审批路径引用，指向 v3 路由和两个 INDEX。

- [ ] **Step 8: 验证并提交**

Run:

```powershell
python -m unittest discover skills/ruyi-upgrade/scripts/tests -v
python -m py_compile skills/ruyi-upgrade/scripts/upgrade_project.py
```

Expected: PASS。

Commit:

```powershell
git add skills/ruyi-upgrade/SKILL.md skills/ruyi-upgrade/scripts/upgrade_project.py
git commit -m "Upgrade Ruyi projects completely to schema v3"
```

### Task 5: Contract / Plan 阶段边界与 spec 检索入口

**Files:**
- Modify: `skills/ruyi-contract/SKILL.md`
- Modify: `skills/ruyi-contract/references/contract-discipline.md`
- Modify: `skills/ruyi-plan/SKILL.md`
- Modify: `skills/ruyi-plan/references/planning-discipline.md`
- Modify: `skills/ruyi-contract/references/spec-schema.md`
- Modify: `skills/ruyi-plan/references/spec-schema.md`

- [ ] **Step 1: 更新 contract 阶段规则**

在 contract discipline 中加入：

```md
当用户开始讨论组件拆分、状态管理、缓存、service 组织、mock、错误处理、目录调整或实现步骤时，先提醒这是 plan 阶段内容。

当前 contract 只确认该话题是否形成业务约束或验收要求：它是否影响用户行为、兼容范围、性能目标、安全边界或交付范围？
```

如果影响，则写入业务规则、范围或验收标准；如果不影响，则不写入 contract。

- [ ] **Step 2: 更新 plan 阶段反向规则**

在 planning discipline 中加入：plan 若发现方案选择改变用户行为、业务规则、接口范围或验收标准，必须返回 contract，不允许在 plan 中隐式扩展需求。

- [ ] **Step 3: 更新 spec 检索规则**

contract/plan 均通过 `.ruyi/spec/INDEX.md` 发现相关 baseline、references 和 open questions。contract 读取 baseline contract 作为业务背景，但不得把 baseline 当成本次变更 contract。

- [ ] **Step 4: 文本扫描验证**

Run:

```powershell
rg -n "实施设计|架构讨论|spec/INDEX.md|baseline contract|返回.*contract|隐式扩展" skills/ruyi-contract skills/ruyi-plan
```

Expected: 命中新增规则。

- [ ] **Step 5: 提交**

```powershell
git add skills/ruyi-contract/SKILL.md skills/ruyi-contract/references/contract-discipline.md skills/ruyi-plan/SKILL.md skills/ruyi-plan/references/planning-discipline.md skills/ruyi-contract/references/spec-schema.md skills/ruyi-plan/references/spec-schema.md
git commit -m "Clarify Ruyi contract and plan phase boundaries"
```

### Task 6: Spec candidate 与知识沉淀改为 test 依据

**Files:**
- Modify: `skills/ruyi-spec-discover/SKILL.md`
- Modify: `skills/ruyi-spec-evolve/SKILL.md`
- Modify: `skills/ruyi-spec-evolve/scripts/candidate_create.py`
- Modify: `skills/ruyi-spec-merge/SKILL.md`
- Modify: `skills/ruyi-spec-merge/scripts/merge_apply.py`
- Modify: `skills/ruyi-spec-merge/scripts/merge_common.py`
- Modify locally only: `skills/ruyi-spec-evolve/scripts/tests/test_candidate_create.py`
- Modify locally only: `skills/ruyi-spec-merge/scripts/tests/test_spec_merge.py`

- [ ] **Step 1: 写失败测试：candidate 来源从 explain 切到 test**

```python
def test_candidate_can_be_created_from_approved_test(self):
    self.write_test(root, result="passed", approval="approved")
    result = create_candidate(root, payload(source="test"))
    self.assertTrue(result["created"])
    self.assertIn(".ruyi/tests/", Path(result["path"]).read_text(encoding="utf-8"))

def test_candidate_rejects_unapproved_test(self):
    self.write_test(root, result="passed", approval="pending")
    result = create_candidate(root, payload(source="test"))
    self.assertEqual(result["reason"], "test-not-approved")
```

- [ ] **Step 2: 更新 candidate_create.py**

删除对 `.ruyi/explain/...` 的硬依赖。新规则：

- 来源可以是 approved test。
- `ruyi-spec-discover` 从代码反推时允许无 test，但必须标记来源为 code observation。
- candidate 仍在 `.ruyi/spec-candidates/`，local-only，不进入根 INDEX。

- [ ] **Step 3: 更新 spec-evolve / spec-merge 文案**

`ruyi-spec-evolve` 从“explain 后沉淀”改为“approved test 后或代码反推后沉淀”。`ruyi-spec-merge` 合入正式 spec 后必须同步 `.ruyi/spec/INDEX.md`。

- [ ] **Step 4: 验证并提交**

Run:

```powershell
python -m unittest discover skills/ruyi-spec-evolve/scripts/tests -v
python -m unittest discover skills/ruyi-spec-merge/scripts/tests -v
python -m py_compile skills/ruyi-spec-evolve/scripts/candidate_create.py skills/ruyi-spec-merge/scripts/merge_apply.py skills/ruyi-spec-merge/scripts/merge_common.py
```

Expected: PASS。

Commit:

```powershell
git add skills/ruyi-spec-discover/SKILL.md skills/ruyi-spec-evolve/SKILL.md skills/ruyi-spec-evolve/scripts/candidate_create.py skills/ruyi-spec-merge/SKILL.md skills/ruyi-spec-merge/scripts/merge_apply.py skills/ruyi-spec-merge/scripts/merge_common.py
git commit -m "Use approved tests for Ruyi spec evolution"
```

### Task 7: 全局 reference、README 与 install 文档同步

**Files:**
- Modify: `README.md`
- Modify: `docs/install.md`
- Modify: all applicable `skills/*/references/main-flow.md`
- Modify: all applicable `skills/*/references/index-protocol.md`
- Modify: all applicable `skills/*/references/spec-schema.md`
- Modify: all applicable `skills/*/references/contract-schema.md`
- Modify: all applicable `skills/*/references/plan-schema.md`
- Modify: all applicable `skills/*/references/test-schema.md`
- Modify: all applicable `skills/*/references/approval-schema.md`
- Modify: all applicable `skills/*/references/task-schema.md`
- Modify: all applicable `skills/*/references/knowledge-evolution.md`
- Modify: all applicable `skills/*/references/spec-candidate-schema.md`
- Modify: all applicable `skills/*/references/spec-merge-protocol.md`
- Remove or deprecate: `skills/*/references/explain-schema.md` according to final release structure

- [ ] **Step 1: 扫描旧语义**

Run:

```powershell
rg -n "explain|frontend-baseline|references/shared/INDEX|references/modules/INDEX|schema_version: 2|spec-archive|spec-patches|workspace|source_explain|交付结果进入 `explain`|验证失败时，不能进入正式 explain" README.md docs/install.md skills
```

Expected: 命中所有需要迁移的旧文本。

- [ ] **Step 2: 同步所有 reference 副本**

统一更新：

- main flow：`contract -> plan -> implement -> test -> approve -> complete`，tiny 为 `contract -> implement -> test -> complete`。
- index protocol：根 INDEX 只索引 `contracts / plans / tests`，spec INDEX 是唯一 spec 检索入口。
- spec schema：删除二级 INDEX；baseline 拆分为 `development-baseline.md` 与 `coding-baseline.md`；candidate local-only 但不默认加载进正式 spec 结论。
- test schema：新增 `approval` 字段并移除进入 explain 的要求。
- approval schema：审批对象为 test。
- knowledge evolution：来源从 approved explain 改为 approved test 或 code observation。

- [ ] **Step 3: 更新 README 与 install**

README 发布结构中移除或标注废弃 `ruyi-explain`，加入 `ruyi-upgrade` 的 v3 完整迁移说明。`docs/install.md` 保留并更新使用方式、升级方式和成熟项目接入方式。

- [ ] **Step 4: 复扫旧语义**

Run:

```powershell
rg -n "schema_version: 2|frontend-baseline|references/shared/INDEX|references/modules/INDEX|source_explain|交付结果进入 `explain`|验证失败时，不能进入正式 explain" README.md docs/install.md skills
```

Expected: 无命中，或仅在 upgrade 旧结构检测说明中命中且语义明确为迁移来源。

- [ ] **Step 5: 提交**

先查看实际变更：

```powershell
git diff --name-only -- README.md docs/install.md skills
git status --short
```

确认未包含 `CHANGELOG.md` 和 ignored tests 后提交：

```powershell
git add README.md docs/install.md <actual changed skill reference paths>
git commit -m "Synchronize Ruyi schema v3 references"
```

### Task 8: 全量验证、版本发布准备与推送

**Files:**
- Review: all production files changed in Tasks 1-7
- Review separately only when publishing release notes: `CHANGELOG.md`

- [ ] **Step 1: Python 语法检查**

Run:

```powershell
python -m py_compile `
  skills/ruyi-init/scripts/common.py `
  skills/ruyi-init/scripts/init_write.py `
  skills/ruyi-init/scripts/init_report.py `
  skills/ruyi-upgrade/scripts/upgrade_project.py `
  skills/using-ruyi/scripts/route_request.py `
  skills/using-ruyi/scripts/index_rebuild.py `
  skills/ruyi-test/scripts/test_create.py `
  skills/ruyi-approve/scripts/approve_update.py `
  skills/ruyi-spec-evolve/scripts/candidate_create.py `
  skills/ruyi-spec-merge/scripts/merge_apply.py `
  skills/ruyi-spec-merge/scripts/merge_common.py
```

Expected: exit code `0`。

- [ ] **Step 2: 全量本地 skill 测试**

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

Expected: 每组测试 `OK`。

- [ ] **Step 3: 端到端 fixture 验证**

用本地 ignored fixture 覆盖：

```text
legacy v1 无 schema_version -> using-ruyi 触发 upgrade -> upgrade 到 v3 -> 删除 explain/旧索引/旧 baseline -> 重建两个 INDEX -> 原请求继续进入 contract 或 plan
v2 approved explain -> upgrade -> 审批迁入 test -> approve 状态可继续路由 complete
旧 frontend-baseline -> upgrade -> development/coding baseline 拆分并删除旧文件
旧 spec 业务事实 -> upgrade -> baseline contract
contract 阶段聊实施设计 -> skill 文案要求提醒转入 plan
```

- [ ] **Step 4: 工作区污染检查**

Run:

```powershell
git diff --check
git status --short --ignored
git diff --name-only
```

Expected:

- 无 whitespace error。
- `skills/*/scripts/tests/` 和 `fixtures/` 仍是 ignored/local-only。
- `CHANGELOG.md` 若仍有用户改动，继续单独保留，不混入实现提交。

- [ ] **Step 5: Release note 与版本提交**

只有用户明确进入发布时，才审视 `CHANGELOG.md`。如果本次发布版本为 `1.0.3` 或用户指定版本：

```powershell
git add CHANGELOG.md README.md docs/install.md <release metadata if any>
git commit -m "Release Ruyi <version>"
git push origin codex/ruyi-github-publish
```

Expected: push 成功；如果远端拒绝，先报告分支阻塞，不做强推。
