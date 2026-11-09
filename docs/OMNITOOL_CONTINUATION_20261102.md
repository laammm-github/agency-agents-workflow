# Agency Agents Workflow — OmniTool-only 续工记录（2026-11-02）

## 操作与设备边界
- 本轮后续本地代码、文件、命令及审计操作均经已授权 OmniTool 完成；未使用 Desktop Commander，没有终止或解锁共享进程。
- 根目录 `docs/STATUS.md`、`docs/TASKS.md`、`build/host-workflow-v2/runs.json`、原 `trial-27` 的源码与 checkpoint 和根 helper 均未修改；审计 SHA256 与原有记录完全一致。
- 项目不存在可用 Git 仓库，继续使用原始证据、哈希、Schema V2 checkpoint 和只增量文档。

## 新增受控隔离修复任务
目录：`build/host-workflow-v2/trial27-patch501-lab-20261102`。

1. 新目录初始化 Schema V2、真实 owner/需求/任务、PREFLIGHT/EXECUTING 和 implementation gate。原 `trial-27` 的后端源码/测试先核对 SHA256 后只复制到隔离目录。为了适应新隔离目录，仅修改测试中的绝对项目名断言。
2. 使用已发布 0.2.9 对应 shadow `check_runner.py` 执行一轮真正的测试失败：6 项、4 个 ERROR、退出码 1，PATCH 返回 501。原始回执：`evidence/patch-first-red.json`，记录 `EV-PATCH-RED`，任务进入 FAILED。
3. 按 FAILED→PREFLIGHT→EXECUTING 恢复，重新通过 implementation preflight 后，仅对隔离 `server.py` 新增受约束的 `do_PATCH`：状态枚举验证、参数绑定 SQLite、显式 commit/closing，正常200/非法400/不存在404。新 SOURCE artifact 显式 supersedes RED 原件。
4. 再经 `check_runner` 真正运行 6/6 PASS、退出码0；证据 `evidence/patch-green.json`，记录 `EV-PATCH-GREEN`，显式 supersedes `EV-PATCH-RED`。原始失败证据仍在全局历史，只有当前任务有效引用改为 PASS。
5. OmniTool 实际读取修复源码并保留 `evidence/source-review-read.json`；`review.md` 明确同会话 ROLE_PHASE/MODEL_JUDGMENT，非独立审查。最终任务 `FIX-BACKEND` COMPLETED，checkpoint revision16，`validate PASS`，生成并读回 `TASKS.md`。未准备发布候选，`ready` 如实拒绝：Candidate manifest mismatch。此隔离补测不等于原 trial-27 通过。

## 0.2.9 原版全量回归与隔离 QA 改善
- 不改动已发布 0.2.9 的原 shadow 源码；两次实际全量回归 129 项均为 **128/129**，同一 `test_invalid_input_and_authorization` 因 Windows loopback `ConnectionAbortedError [WinError 10053]` 失败，原始记录分别在实验目录 `evidence/shadow-full-regression-first-fail.log`、`evidence/shadow-full-regression-second-fail.log`。
- 原 shadow 的教学集成模块单独复测 5/5 PASS，原始日志 `evidence/shadow-focused-recheck-pass.log`。
- 创建与 0.2.9 脚本哈希一致的新隔离 `build/qa-shadow-20261102`，**只修改 QA 副本**的 `tests/test_teaching_integration.py`：启动本机测试服务后针对幂等 `/health` 做有限重试（最多5次），不自动重放任何 POST 写操作。该副本定向 5/5，完整 129/129 PASS；原始日志 `evidence/qa-shadow-full-regression-pass.log`。
- 这是 QA-only 候选验证。尚未合并进主工程，也不应将其声称为原 0.2.9 shadow 全量 PASS 或新插件发布。

## 当前总门禁和续工要求
- 严格连续自主宿主验收仍 **0/3**；TEAM 完整宿主 **0/14**、ROLE **0/18**、四条 E2E **0/4**。
- `trial-27` 原 checkpoint revision14，BACKEND FAILED；`runs.json` 仍 SUBMITTED_RUNNING，原 ChatGPT 宿主终态 UNKNOWN。不可把无进程/无文件变化当作远端结束证明，不启动并发原宿主写入。
- 主项目 `scripts/team.py` 与 `scripts/workflow_v2.py` 仍不同于线上 0.2.9 shadow，既有 Windows 文件句柄风险尚未正常解除。不得使用 Desktop Commander，亦不得强行杀进程、覆盖脚本、跳过原子保存。
- 下一步依序：通过 OmniTool 安全核对原宿主终态与句柄状态 → 获得无干扰条件后版本化同步 canonical helpers → 审阅 QA-only 稳定性补丁是否纳入未来版本 → 再做严格连续宿主试验及完整 TEAM/ROLE/E2E 验收。

机器核查 `build/host-workflow-v2/trial27-patch501-lab-20261102/OMNITOOL_CONTINUATION_AUDIT_20261102.json`，SHA256 `176d02df5ba68bfb74052a8c94960e6814aa1ac14d3f43610696e644f5bc4d7a`。该独立审计仅证明本地实验与文件哈希，不提供工具执行来源的独立认证。
