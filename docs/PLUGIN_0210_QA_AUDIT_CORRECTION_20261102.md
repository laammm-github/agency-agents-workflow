# 0.2.10 QA 包装器首次失败证据更正（2026-11-02）

对 `QA_0210_AUDIT.json` 与 `PLUGIN_0210_CHECK_RUNNER_SUPERSEDES_REGRESSION_20261102.md` 作**追加更正**，不覆盖原记录。

首次 PowerShell 包装器在 `ErrorActionPreference=Stop` 下将 Python unittest 输出到 stderr 的文字作为 `NativeCommandError`，工具返回“Process completed with exit code 1”。**首次 `RAW_STDOUT.txt` 与 `RAW_STDERR.txt` 实际均为 0 字节**；之前称其“保留原始失败输出”不准确。真实失败信息仅在当时的 Desktop Commander 工具响应中可见，未写入上述两个文件，不能将空文件作为原始错误文本证据。

后续第二次独立运行成功，`RUN2_STDOUT.txt`、`RUN2_STDERR.txt` 非空，`RESULT.json` 与 15+1 项 PASS 均可独立复核。首次包装器失败不计 PASS，且该更正不改变完整宿主验收 0/3 的结论。

机器可读追加记录：`build/host-workflow-v2/plugin-0210-qa-regression-20261102T1207Z/HARNESS_EVIDENCE_CORRECTION.json`。
