# TEAM-14 / QA capture 排他创建竞态：隔离验证（2026-11-03 JST）

- 版本门禁：可信 Plugin Creator 返回 USER/PRIVATE、0.2.10、Release `pluginrel_6ae857ea7ce4819193bcd1a74d0f83b5`；测试载入的 `check_runner.py` SHA-256 为 `7ad73950c45a12bd21fc9e5f84d17259cf9c7b4e9628bef70e9e79a5400fda64`。
- 在全新隔离 fixture 中执行一次真实 QA 子进程。子进程在返回前创建 `evidence/RACE1.json`，模拟另一写者占据同一 capture 路径。
- 结果：QA adapter 对排他 `open('x')` 返回真实 `FileExistsError`；原始文件内容 `external-actor-original` 未覆盖；checkpoint revision=3，pending=1，evidence=0，任务仍 EXECUTING。
- `workflow.resume` 正确拒绝未解决副作用：`Resolve unknown side effects before resume`。没有自动重试或错误计为 PASS。
- 独立测试进程正常结束；审计脚本标记 isolated PASS。该测试**不是**同时发生的两个独立写者竞争证明，也不是完整 TEAM-14/ROLE/E2E 宿主验收 PASS。
- 审计：`build/host-workflow-v2/team14-qa-capture-race-20261102T1630Z/CAPTURE_RACE_AUDIT.json`；执行器：同目录 `run_capture_race.py`。文件通过同卷临时文件 + `os.replace` 原子落盘。
- `runs.json`、trial-22、trial-27 检查点、共享 `STATUS.md`、`TASKS.md` 的 SHA-256 前后 5/5 一致。没有触碰历史试验或原数据库。
- 原宿主结束证据仍未知：trial-22 revision43/HANDOVER 未完成；trial-27 revision14/BACKEND FAILED，runs 仍 SUBMITTED_RUNNING。无可靠宿主结束证明前不启动并发试验、不补发纠错、不原子归档成功。
- 总体严格连续 0/3；TEAM 0/14、ROLE 0/18、E2E 0/4 完整宿主通过。共享 STATUS/TASKS 原件未更新，以本独立文档补充本次证据，避免绕过历史文件句柄与原子保存门禁。
