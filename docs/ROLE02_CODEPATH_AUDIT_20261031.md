# ROLE-02 / TEAM-01 只读代码路径审计（2026-10-31）

本次仅通过已授权的只读工具读取已冻结的 trial-23 源码、原始浏览器快照、集成测试和 0.2.9 角色资料，不访问其活动服务、不写入其 SQLite、不修改任何 trial-22/23 检查点或源码。独立审计 JSON：`build/host-workflow-v2/ROLE02_CODEPATH_READONLY_20261031.json`，SHA256 `9989ea158d4b38802d1f637ccb4629108068fa3c9323fb5f7bc232bf3719cf8d`。

## 一句话

该候选是原生 HTML/JavaScript 前端通过 `fetch` 访问 Python 标准库 HTTP 服务，后端使用 `sqlite3` 持久化任务的本地 Web 应用。

## 五分钟路径

创建任务：`app.js` 的表单提交 → `POST /api/tasks` → `server.py Handler.do_POST` 验证标题 → SQLite `INSERT INTO tasks` → HTTP 201 → `refresh()` 调用 `GET /api/tasks`，最终由 `Handler._list` 执行 `SELECT`。

修改状态：`app.js` 下拉框 change → `PATCH /api/tasks/{id}` → `Handler.do_PATCH` 验证状态 → 参数化 SQLite `UPDATE` → HTTP 200 → 重新加载列表。按状态筛选：`GET /api/tasks?status=...` → `Handler._list` 的参数化 `WHERE status=?`。删除：`DELETE /api/tasks/{id}` → SQLite `DELETE` → HTTP 204。

## 深入证据

实际读取的 `server.py`、`app.js`、`tests/test_integration.py` 均与冻结候选哈希一致（7/7）；浏览器已存的创建、修改状态、筛选、同库重启四份 Playwright 页面快照与代码路径相符。集成测试源码显示相同数据库路径跨不同 PID 重启；本次没有重新启动服务或重新执行浏览器，原始执行证据应继续以 trial-23 的宿主回执为准。角色原始资料 `engineering-codebase-onboarding-engineer.md` 已实际读取，独立报告中保存了源文件 SHA 和函数/SQL 代码行号。

## 已定位的可靠性缺口

`GET /health` 在 `server.py` 中直接返回 `{"ok": true}`，未检查 SQLite 可用性；`log_message` 被覆写为 `pass`；所检查的后端没有 metrics 路由；静态文件白名单未包含 `/favicon.ico`。因此**不能把当前健康端点的 200 当成数据库可用或服务 SLO 达标的证明**。这只是源代码级缺口，并未在本轮对活动服务进行故障注入，也未证明真实事故。原先浏览器回执中存在 favicon 404，保持原证据，不修改已冻结候选。

## 验收归类与后续

这是 **ROLE-02 / TEAM-01 的只读代码路径局部证据**，不是角色自身完整宿主工作流、正式 handoff、失败设备/目录拒绝或 E2E 场景的 PASS。完整 ROLE-02、TEAM-01、TEAM-11、ROLE-17 仍 NOT_PASSED。后续新隔离试验应覆盖依赖故障时健康探针/日志/指标/告警的真实故障→恢复路径，不能事后修改 trial-23 以抹平历史。
