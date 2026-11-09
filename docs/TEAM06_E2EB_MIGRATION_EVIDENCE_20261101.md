# TEAM-06 / E2E-TEAM-B：已有 SQLite 项目迁移隔离证据

## 实施范围

独立、仅测试用的合成已有项目：`build/host-workflow-v2/existing-project-migration-lab-20261101`。不读取真实用户数据库，不修改任何历史 trial checkpoint，不提交/推送或部署。该项目 v1 已存在两个含中文内容的工单，其中一个包含既有用户状态修改。原始 SQLite 文件哈希 SHA256 为 `298a04b80c3c952b2411fefdd4e0e17bfed4a85e5c0cc966c4714482ad9a4a7a`。

## 真实执行证据

- RED：初始项目尚未实现 schema 迁移，3 个实际 `unittest` 运行报错，退出码 **1**；原始 Python 子进程 stdout/stderr/完整十六进制字节：`RED_TOOL_RETURN.json`（SHA256 `68930fbd641a0a42c5bca6ffe5ac30ce20fcfc017fba02c77031d146e9c47dd5`）。
- 修复：在隔离项目中实现 SQLite v1→v2 的 `priority` 列迁移，使用 `BEGIN IMMEDIATE`、`PRAGMA user_version`、显式事务提交与回滚、显式关闭连接；已存在 v2 时不重复修改，旧版本之外拒绝无依据迁移。
- GREEN：3/3 单元验收通过，退出码 **0**，原始返回 `GREEN_TOOL_RETURN.json`（SHA256 `e6e2411c2790ccaa5a4ba840af17e968b483e34948dfc7db4e9146b18e5ad7a9`）。
- 已验收：两条原始工单与已有用户状态变更完整保留；重复迁移幂等；故意在 `ALTER TABLE` 后触发异常能回滚到 v1 原始 schema，随后重试可以成功。独立审计 `MIGRATION_RED_GREEN_AUDIT.json`，SHA256 `67b03c8da532a837f723e4510caf743e01ca11af9d152ff7e282b9e9f29675a7`；合成 v1 原始数据库哈希保持不变。

**验收等级：TEAM-06 / E2E-TEAM-B 的独立局部真实测试证据 PASS；完整 TEAM-06 或 E2E-TEAM-B 宿主验收仍为 NOT_PASSED。** 不能以本文件代替自主宿主原始工具认证、角色交接、实际浏览器、候选冻结或原项目变更追踪链。

当前独立正式 trial-27 仍在新 ChatGPT High 宿主执行，首次提交审计 `build/host-workflow-v2/trial27-submission-observed-20261101.json`。禁止在它运行期间由验收方修改其 checkpoint 或发中途纠错。
