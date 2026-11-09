# Agency Agents Workflow 0.2.10 — check_runner 真实回归（2026-11-02）

本次使用可信 Plugin Creator 读取原私人插件 USER/PRIVATE 的当前发布版本 **0.2.10**，Release `pluginrel_6ae857ea7ce4819193bcd1a74d0f83b5`。直接取回发布文件 `skills/agency-workflow/scripts/check_runner.py`，SHA-256 为 `7ad73950c45a12bd21fc9e5f84d17259cf9c7b4e9628be70e9e79a5400fda64`，并在独立测试目录运行。

- 原有 `test_check_runner.py`：**15/15 PASS**，无失败、无错误、无跳过，真实子进程退出码 0。
- 新增定向回归：**1/1 PASS**。先真实执行 FAIL（exit 3），修复后以 `supersedes=['FAIL-ORIGINAL']` 执行 PASS。最终任务的当前 `evidence_refs` 仅保留 `PASS-REPAIR`，不可变历史 `state.evidence` 仍保留原 FAIL 与后续 PASS，且 unresolved 为空。
- 首次 PowerShell 包装器因 `ErrorActionPreference=Stop` 将测试 stderr 视为异常，**exit 1**。原始 `RAW_STDOUT.txt`、`RAW_STDERR.txt` 保留；调整独立包装器后第二次执行成功。不可把首次包装器失败计为测试通过。
- 只在 `build/host-workflow-v2/plugin-0210-qa-regression-20261102T1207Z` 新建独立文件；未修改 trial-22、trial-27、原插件发布内容、共享 `runs.json` 或 `docs/STATUS.md`/`docs/TASKS.md`。
- 该结果只证明 0.2.10 QA 证据替代逻辑在隔离测试中成立，**不代表 0.2.9 的完整自主宿主试验通过，也不计 TEAM/ROLE/E2E 完整验收**。trial-27 原宿主是否结束仍未获可靠证明，正式归档与新轮次继续受单写者门禁限制。

原始证据：`RESULT.json`、`RUN2_STDOUT.txt`、`RUN2_STDERR.txt`、`RAW_STDOUT.txt`、`RAW_STDERR.txt`；机器审计：`QA_0210_AUDIT.json`。
