# OmniTool-only 续工增量 — 2026-11-02 第二轮验证

## 续工范围与隔离
- 遵循用户明确要求，全部本地操作使用 OmniTool；未调用 Desktop Commander，未终止现有共享工具进程。
- 原 trial-27 宿主是否结束仍 UNKNOWN，runs.json 为 SUBMITTED_RUNNING，checkpoint revision14，DESIGN COMPLETED / BACKEND FAILED，不能作为完整成功。
- 根脚本原子同步 preflight 两次确认 BLOCKED_FILE_HANDLES。共享进程 PID20772 持有 team.py、workflow_v2.py；不强行杀进程、不在原目录执行 apply、不绕过锁。
- OmniTool browser_open 返回 BROWSER_SESSION_LIMIT(3)；未在原 ChatGPT 试验宿主取得最终回执。本轮不启动新的并发正式宿主试验。

## QA 候选连续验证（隔离副本）
- 独立目录：build/qa-shadow-20261102，只修改 tests/test_teaching_integration.py 的健康检查启动探测。它最多重试五次 /health 只读请求，不重放 POST。
- 之前首次该隔离副本 129/129 PASS 的证据在 build/host-workflow-v2/trial27-patch501-lab-20261102/evidence/qa-shadow-full-regression-pass.log。
- 本轮通过 OmniTool verification_run 再次实际执行 python -B -m unittest discover -s tests -v：**129/129 PASS，exit0，53.252s**，原始 stderr 另存 evidence/qa-shadow-full-regression-second-pass.log。
- 本轮执行 python -B -m scripts.package：**PASS，70 files**，生成 build/qa-shadow-20261102/build/agency-workflow-plugin.zip，SHA256 c4e5599a064f58714a4308873ef67407baf517b27e2b5bcd945154264b3ea52d。该 ZIP 不构成新线上版本。
- 文件哈希独立比对：plugin.json、package-files.json、SKILL.md、team.py、workflow_v2.py、check_runner.py 与已发布 0.2.9 原 shadow 完全一致；仅 QA 单测 tests/test_teaching_integration.py 差异（旧 SHA256 08180cf83cc39a8c3679ea9a30a186d2a3087c53139cc640f24275489950a171，新 SHA256 2a44f4249d7250af9415d08c720b842aafa32c400c269a7d299fba47bd956c58）。
- 此健康探测改善本地测试稳定性，不证明 WinError 10053 的外部根因（安全软件/本机网络栈干预尚未确认）；原 0.2.9 shadow 历史两次 128/129 失败仍保留，不能回写为 PASS。

## 当前验收边界与下一步
- 原私人插件仍 0.2.9，尚未发布 0.2.10；完整连续自主成功仍 0/3。
- TEAM-01..14、ROLE-01..18、E2E-TEAM-A/B/C/D 真实宿主全项验收仍未完成。
- 下一步需先通过当前已授权 OmniTool 能力核实原会话真正终态，等待共享文件句柄可安全释放，随后按 hash 与锁门禁同步 canonical helper，再行新版本候选回归和严格三轮宿主验收。不能把 QA-only 测试稳定化等同完整团队交付。
