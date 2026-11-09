# Agency Agents Workflow — 2026-11-01 续工与验收增量

该文件是新的只增量证据记录；主 `docs/STATUS.md` 和 `docs/TASKS.md` 的原子更新此前受到共享 Desktop Commander 文件句柄阻断，不通过直接覆盖或杀共享进程修复。历史 trial、原 checkpoint、失败证据均未被更改。

## trial-26 正式独立终验

- 原独立 High 宿主 `https://chatgpt.com/c/6ae69280-5648-83e8-a349-8eb982c50b0f` 已结束。Checkpoint revision **26** / SHA256 `95314d2a88e9270f91b83fb761bc8ad627ac2d8ecdce73e667f39fe8fc39016e`。
- DESIGN COMPLETED、BACKEND FAILED、FRONTEND/INTEGRATION/HANDOVER PLANNED，4 条证据（3 FAIL、1 PASS）、1 handoff、0 pending；观察器从空目录采集到 revision26，50 条变更样本，正常有限退出。
- 实测原始失败分别为 `ModuleNotFoundError: server`、`TypeError: 'socket' object is not callable`、`PermissionError [WinError 32]`（测试 SQLite 文件在 Windows 系统 TEMP、sqlite3.Connection 通过 `with` 没有关闭）。0.2.9 shadow `validate` 真实 exit0/PASS，`ready` 真实 exit1 `Unfinished work`。
- 已原子归档 `BACKEND_FAILED_THREE_REAL_CHECKS_NOT_STRICT_CLEAN` 到 `runs.json`，保存原始索引备份，审计 `build/host-workflow-v2/trial26-independent-failure-audit-20261101.json`。不能补写后端 PASS、交接或最终 READY。

## 已解决的隔离技术缺陷

- 从固定 trial-26 源码复制**仅作为隔离测试夹具**，在 `build/host-workflow-v2/sqlite-lifecycle-lab-20261101` 内将测试 SQLite 临时目录限定在沙箱。未改变后端连接语义时，实际 RED：3/3 测试于文件清理阶段出现 `WinError32`，退出1，完整原始输出保存 `RED_WINDOWS_FILE_HANDLE.json`。
- 仅修改隔离副本：后端 SQLite 连接使用 `contextlib.closing`，初始化 schema 显式 commit，测试库路径保持沙箱内。随后实际 GREEN：3/3 API tests PASS、exit0，原始返回 `GREEN_WINDOWS_FILE_HANDLE.json`。独立检查原 trial-26 checkpoint 和源码哈希均未变化。
- 审计 `build/host-workflow-v2/sqlite-lifecycle-lab-20261101/SQLITE_LIFECYCLE_RED_GREEN_AUDIT.json`，SHA256 `1268f10010b2004e8056f81d94e9ed7759ea5a26df856f2594a3e17519072aae`。以前 RED 留下的 3 个临时 SQLite 文件未强制删除；另行处理需确认所有权与句柄，不跨授权边界。
- 本补充是一个已验证的**局部 QA 修复**，不代表新主试验、TEAM/ROLE 或原 trial-26 已 PASS。

## trial-27 新的严格自主试验

- 唯一新项目目标 `build/host-workflow-v2/trial-27` 在正式首次提交前不存在。既有有限只读 watcher 在提交前独立启动，Windows PID **34392**，首条样本确认目标不存在，启动日志 `build/host-workflow-v2/trial27-observer-start-20261101.json`。
- 新 ChatGPT High 会话 `https://chatgpt.com/c/6ae6b4a1-2984-83ee-8757-cbbfd5f21862` 已单次提交。请求 `trial27-request-20261101.txt` 明确规定原插件 0.2.9/Release 的**本次宿主真实 metadata 验证**、不触碰共享 Node 的 checkpoint 预览、模块导入、connection 命名和 SQLite 清理的可复现预防措施、真实新 QA FAIL→repair→PASS、浏览器三个负例、同库新 PID 重启、最终 HANDOVER/TASKS.md 和独立 validate/ready。
- `runs.json` 已 compare/atomic 登记为 **SUBMITTED_RUNNING**，原始索引备份 `runs-before-trial27-submit-20261101.json`，首次提交审计 `trial27-submission-observed-20261101.json`。截至本增量观察仍在宿主元数据/工具预检，尚无完整 PASS；禁止验收方并发写入、纠错提示或提前算作 clean。

## 总体待办

原私人插件 0.2.9 当前正常发布；历史 trial-23 一轮独立终验严格 PASS（执行来源认证限制继续披露），trial-24/25/26 均未达到 clean 并打断连续性，**连续 clean 计数仍为 0/3**。主目录 0.2.9 helper 同步因 Windows 共享文件句柄阻断；TEAM-01..14 / ROLE-01..18 / E2E-TEAM-A/B/C/D 仍需完整独立宿主场景与矩阵门禁。接下来应旁路观察 trial-27 实际完成情况，独立验收后忠实归档，再按依赖顺序推进新的连续试验和团队能力验收。
