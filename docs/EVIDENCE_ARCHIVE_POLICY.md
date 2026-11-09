# 证据归档、索引与清理策略（2026-11-09）

本策略用于 Agency Agents Workflow 0.2.10 的开发侧工作区，不修改插件发布包、私人插件或任何历史验收结论。

## 1. 原则

- **历史不可重写。** 真实 QA FAIL、UNKNOWN、修复 PASS、工具回执、浏览器记录、CAS/原子失败提案及备份均原地保留，不能通过移动/删除伪造成功。
- **索引不是事实来源。** `trial-*/checkpoint.json` 记录各轮任务；`build/host-workflow-v2/runs.json` 保存正式归档结论；`evidence/` 及观察日志保存原始证据。本目录新增的索引是有明确时间点的只读投影。
- **不搬迁既有路径。** 历史字段 `artifact_ref`、输入 manifest、`runs.json`、监测脚本可能使用旧路径。未经引用全量迁移及复验，不修改这些路径。
- **保护进行中的试验。** 对 INCOMPLETE、BLOCKED、未知副作用及缺检查点目录只收集元数据，跳过深度内容哈希检查；不关闭其他会话、不操作试验写者。
- **明确认证边界。** 哈希一致不等于宿主外部工具来源经过独立认证，也不等于严格自主验收通过。

## 2. 目录职责

| 路径 | 职责 | 保护规则 |
|---|---|---|
| `scripts/evidence_archive.py` | 开发侧独立索引/核验/清理提案/导航生成 | 不在插件运行时打包清单 |
| `tests/test_evidence_archive.py` | 合成工作区的自动化测试 | 临时夹具只在本项目 build 下创建 |
| `build/host-workflow-v2/trial-*/` | 原始 checkpoint、源码候选、工具输出、交接与历史 | 永久保留、禁止自动移动 |
| `build/host-workflow-v2/trial-*-observed/` | 验收侧观察副本 | 永久保留 |
| `build/host-workflow-v2/runs.json` | 官方验收记录与严格连续计数 | 只能按原有授权 SHA/CAS/原子流程更改 |
| `build/host-workflow-v2/*-watch.jsonl` | 时间轴和监测证据 | 永久保留 |
| `build/evidence-archive-index/snapshots/` | 不可覆盖的 JSON 索引快照 | 每次创建新文件 |
| `build/evidence-archive-index/verification/` | 只读哈希核验结果 | 保存包括异常的完整结果 |
| `build/evidence-archive-index/plans/` | 清理待审清单 | 默认零删除、零移动 |
| `build/evidence-archive-index/INDEX-*.md` | 面向人工的试验导航 | 属于快照，不代表实时状态 |

## 3. 保留与清理分级

**R0 永久保护。** 所有试验目录、`-observed`、`checkpoint.json`、`runs.json`、`evidence/` 原始数据、候选 manifest、`*.jsonl`、`*.log`、`*.stop`、截图、手工 review、失败事故、原始发布 ZIP、CAS proposal、备份及未完成轮次。不能因旧、失败或阻断而删除。

**R1 只读元数据归档。** 索引快照、来源 SHA、核验回执及导航文件可重复新建，不能覆盖旧版。旧格式逻辑 ID（如 trial-09 的 `A-DESIGN`）只通过原记录 `state.artifacts` 查出对应路径并在索引注明 `ARTIFACT_ID_ALIAS`，不修改历史 checkpoint。

**R2 待授权的可再生缓存。** 如 `__pycache__/`、`*.pyc`。目前只做识别，不自动移动或删除。未来先确认不在运行、不被包/证据引用、有完整哈希与备份、具备明确操作授权后才考虑可逆隔离。

**R3 待复核暂存物。** `*.pending`、`*.tmp`、历史失败 CAS 提案默认仍是 R0 保护，必须先关联产生原因、实际哈希、观察日志和官方归档状态，不能按扩展名或时间盲删。

## 4. 可重复执行的操作

在项目根目录执行，输入/输出均留在授权目录：

`python -B scripts/evidence_archive.py snapshot --project-root . --output build/evidence-archive-index/snapshots/host-workflow-YYYYMMDD-new.json`

`python -B scripts/evidence_archive.py verify --project-root . --index build/evidence-archive-index/snapshots/host-workflow-YYYYMMDD-new.json --output build/evidence-archive-index/verification/host-workflow-YYYYMMDD-verify.json`

`python -B scripts/evidence_archive.py cleanup-plan --project-root . --index build/evidence-archive-index/snapshots/host-workflow-YYYYMMDD-new.json --output build/evidence-archive-index/plans/host-workflow-YYYYMMDD-review.json`

`python -B scripts/evidence_archive.py report --project-root . --index build/evidence-archive-index/snapshots/host-workflow-YYYYMMDD-new.json --output build/evidence-archive-index/INDEX-YYYYMMDD.md`

输出均为排他新建（已有目标则拒绝），会读回确认 SHA。`verify` 在发现内容不匹配时退出 1；权限/格式等错误退出 2。发现差异时应独立调查，禁止直接修改历史证据消除警告。

## 5. 本次真实盘点结论

- 原仓 `build/host-workflow-v2` 顶层共689项（599文件），试验相关目录54个、共2376个文件。
- 第一版核验发现 `trial-09` 的 `A-DESIGN`、`A-CONTRACT` 两条“路径缺失”。对照原检查点，确认它们实际上是产物 ID，映射到 `DESIGN.md`、`CONTRACT.md`。初版索引及两项误报原样保留；索引器增强逻辑 ID 映射后单独生成第二版。
- 第二版索引 `snapshots/host-workflow-20261109-r2.json`：**380 个文件核验通过、0项差异**。41个未完成或缺检查点等目录暂缓深度认证，不能被算作已核验通过。
- `plans/host-workflow-20261109-review.json` 显示**自动删除候选0项**。唯一 `runs.json.trial28-29-20261109.pending` 被列入待复核且仍然保留。
- `INDEX-20261109.md` 提供按轮次导航和旧格式映射，非实时状态文件。

## 6. 未来若需实际释放空间

必须单独列出每一个拟处理路径、当前 SHA、引用状态、所有者、活跃进程/宿主状态、可逆备份与恢复方案，并获得明确的目标和操作授权。建议采用“核验快照 → 复制/核对 → 隔离与读回 → 最终确认再销毁”四阶段；不得绕过 Windows 文件锁或原子的 CAS 保存，也不可将清理成果计为 QA 或宿主验收 PASS。本次没有实现和执行移动/删除，历史原始材料全部保留原位。

## 7. 查询入口

- 快速查找：`build/evidence-archive-index/INDEX-20261109.md`。
- 程序检索：对应 `snapshots/*.json` 中 `runs_index`、`trials[].checkpoint`、`trials[].evidence[]`、`candidate.files[]`。
- 校验回执：`verification/host-workflow-20261109-r2-verify.json`。
- 清理提案：`plans/host-workflow-20261109-review.json`。
- 实际最新项目验收状态：`docs/STATUS.md`、`docs/ACCEPTANCE_MATRIX.md` 与原 `runs.json`。
