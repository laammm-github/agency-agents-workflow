# Agency Agents Workflow 续工事实记录 — 2026-11-01

本文件是补充证据索引。原有 `docs/STATUS.md`、`docs/TASKS.md` 因共享 Desktop Commander Node PID20772 持有文件句柄，曾出现原子替换 EPERM，不能靠原地覆盖消除阻断。旧文档内容和历史失败均需保留，后续正常释放句柄时再安全同步。

## 发布与严格验收

- 原 USER/PRIVATE 插件 ID `plugins_6ae1de0d0fb481918688acd3e26d7051`，已发布线上 0.2.9，release `pluginrel_6ae53a8cc71881919a8e7c98c19f7536`。
- trial-23：`HOST_COMPLETED_READY_PASS_STRICT_CLEAN_WITH_ORIGIN_LIMITATION`。实际 checkpoint revision52 / SHA256 `59dbaadf3a96f53541e877ae0377ac8feb4cbab8c665ec4ef1c22b9544f74eeb`，22证据、4交接、真实 FAIL→修复→PASS、独立浏览器负例与 SQLite 重启、最终 TASKS.md、独立 validate/ready PASS。严格成功总数 **1**；仍保留执行工具来源独立认证 UNKNOWN 的限制。证据 `build/host-workflow-v2/trial23-independent-final-host-completed-audit-20261031.json`。
- trial-24：原宿主返回 `MCP server is not initialized` 和 `Tunnel-client has not been seen for 300 seconds`，原项目 checkpoint revision3、DESIGN EXECUTING，后续真实开发尚未到达。已真实归档 `HOST_TRANSPORT_BLOCKED_BEFORE_PLANNED_BACKEND_HANDOFF_NOT_CLEAN`，不可计入 PASS；原本的连续成功被打断，**当前连续成功 streak 为 0/3**。证据 `build/host-workflow-v2/trial24-independent-blocked-final-audit-20261101.json` 和 `trial24-strict-streak-correction-20261101.json`。
- trial-25：针对工具通道失联，使用新的独立 High 宿主 `https://chatgpt.com/c/6ae619aa-a794-83e8-b6a8-785ede8ccfa0` 单次提交完整任务；提交前 PID2196 的既有有限时长只读 watcher 已启动，首条样本记录目录不存在。runs.json 原子登记 `SUBMITTED_RUNNING`，原始 request 与索引备份保存。首次任务允许在真实能力核对后使用 OmniTool/原生授权工具替代失联的公司 coding tunnel，不重启共享进程，不做中途人工提示。**尚未完成、尚未计入3轮**。证据 `build/host-workflow-v2/trial25-submission-observed-20261101.json` 和 `trial-25-watch.jsonl`。

## Windows 文件锁与后续任务

- 公司 `coding_tools_mcp_gongsi` 通道当前返回 tunnel client 300秒离线；从本机进程快照可看到 Desktop Commander、Computer Use、Playwright 与 OmniTool 的其他 tunnel-client，但不能把它们的状态视为该 coding 通道已恢复。只读定位脚本 `build/host-workflow-v2/inspect_host_mcp_tunnel_20261101.py`。
- canonical `scripts/team.py`、`scripts/workflow_v2.py` 与已发布 0.2.9 shadow 文件哈希仍不同；共享 Desktop Commander Node PID20772 持有文件句柄。默认只读 `build/host-workflow-v2/sync_root_helpers_029_once.py` 返回 `BLOCKED_FILE_HANDLES`，未执行 --apply，不杀共享进程、不绕过 compare/atomic 写入。说明 `build/host-workflow-v2/ROOT_HELPERS_029_LOCK_PREFLIGHT_20261031.json`。
- `docs/STATUS.md`、`docs/TASKS.md` 更新时真实出现原子写 EPERM，原完整更新提案在 `build/host-workflow-v2/TRIAL23_DOCS_UPDATE_PROPOSAL_20261031.json`、`TRIAL23_FINAL_DOCS_LOCKED_PROPOSAL_20261031.json` 和 `DOCS_UPDATE_TRIAL24_LOCKED_PROPOSAL_20261101.json`。不能通过原地覆盖或反复试错替代。
- TEAM-01..14、ROLE-01..18、E2E-TEAM-A/B/C/D 完整矩阵未全项通过。已有隔离 B/C/D、AppSec RED→GREEN/SQL 注入安全性、TEAM14 CAS 冲突等局部证据，不升级为完整角色宿主验收。
- 下一优先级：旁路观察 trial-25 的真实版本门禁、QA FAIL→PASS、浏览器负例、同库重启与最终 handover/ready；结束后独立审计、原子归档，依照其实际结果计算连续 streak。然后执行剩余完整自主轮次及 TEAM/ROLE/E2E 缺项，直到所有原始验收条件真正满足。

本记录仅依据实际 Windows 文件/工具返回；不补写历史 trial、不制造执行来源凭证、不声明当前试验已经完成。
