# ROLE-17 / TEAM-11：真实 HTTP 数据库故障注入（隔离补测）

时间：2026-11-02T06:57:58.776035+00:00

对历史冻结 trial-23 服务端源码执行**只读导入**，仅在内存将 ROOT 指向全新隔离目录，使用 127.0.0.1 自动端口和新建 SQLite。没有复制 Demo 或修改任何历史试验。

创建任务及健康/列表基线成功；将隔离数据库文件临时移走并在同路径创建目录模拟数据库不可用。故障时 /health 仍返回 HTTP 200，而 /api/tasks 失败；恢复原 SQLite 后任务仍在。

本次判定：ISOLATED_FAULT_REPRODUCED_RECOVERY_PASS。这暴露健康探针不覆盖数据库就绪性，不等于完整 ROLE-17 或 TEAM-11 PASS，也不影响 0.2.9 连续自主计数。

原始每次 HTTP 结果、异常、服务端 stderr 和原始文件前后哈希保存在 build/host-workflow-v2/role17-health-fault-20261102T0658Z/RESULT.json、RAW_HTTP_SERVER_STDERR.txt。
