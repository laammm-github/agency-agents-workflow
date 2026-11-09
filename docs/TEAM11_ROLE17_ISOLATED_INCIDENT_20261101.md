# 2026-11-01 TEAM-11 / ROLE-17 独立故障子场景验收

在正式 trial-24 宿主仍执行时，**没有触碰 trial-24 项目或发送人工纠错**。独立创建 `build/host-workflow-v2/role17-team11-health-isolation-20261101`，从零编写 Python 标准库 HTTP + SQLite 测试 fixture，只监听 127.0.0.1 的自动端口，运行后正常关闭，无新 MCP Server/调度器/后台服务。

首次真实 QA **FAIL（exit 1）**：SQLite 连接未及时关闭，Windows 上故障注入 `os.replace` 报 `WinError 32`。保留 `INITIAL_QA_FAIL_TOOL_RETURN.json` 和 `fixture-initial-fail.sqlite3`；修复为显式关闭连接后，在新隔离数据库上复测 **13/13 PASS、exit 0**，原始 HTTP 状态与响应体（base64）、事件时间顺序和本地工具返回分别保存于 `INCIDENT_RESULT.json`、`QA_RETEST_TOOL_RETURN.json`。完整审计 `INDEPENDENT_AUDIT.json`。

覆盖健康检查必须真实访问 SQLite、故障期间两次 503 触发一次告警、/metrics 记录 SLO 不达标、同库恢复后 200 与任务状态保留、告警解除、缺少遥测时健康和指标均返回 503/unknown。保留复盘 `INCIDENT_REVIEW.md`。冻结的 trial-23 checkpoint SHA 仍为 `59dbaadf3a96f53541e877ae0377ac8feb4cbab8c665ec4ef1c22b9544f74eeb`。

**验收边界：这只是独立子场景 PASS，不是 TEAM-11、ROLE-17 或 E2E-TEAM-C/D 正式 PASS。** 仍缺真实多角色交接、独立告警设施、真实宿主执行及完整回归。共享 `docs/STATUS.md`、`docs/TASKS.md` 在 trial-24 写入期间未并发修改；本文件是新增、独立的文档补充。
