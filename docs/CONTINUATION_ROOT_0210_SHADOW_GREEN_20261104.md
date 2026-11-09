# Agency Agents Workflow — 2026-11-04 续工：线上全资源一致性与 root shadow 升级演练

## 1. 完整发布物核验：PASS（静态来源范围）
- 原 USER/PRIVATE 插件 0.2.10，release `pluginrel_6ae857ea7ce4819193bcd1a74d0f83b5`。
- Plugin Creator 实际获取线上共 71 个文件，保存 `build/published-0210-resource-audit-20261104/remote-files-1..5.json`（5批），无大小限制/缺失。
- 本地执行 `compare_release.py` exit0，`COMPARISON.json` SHA256 `129970641a70b697203d0019ea9a382348e7c3e7bd32e5548935eddd9395bdcf`。
- 本地 0.2.10 ZIP 共 70 个打包文件，与线上相应 70 个文件规范化换行后 **70/70 内容一致**；多出线上 `.codex-plugin/plugin.json` 一项，本地候选目录和 ZIP 无此文件。全部 71 份线上文件读取完毕。
- 候选 ZIP SHA256 `005e75607c87d7305b95c6024011f8ba39f09de44442425db44238aea478b0a7`。此项证明静态文件一致，不能证明其他宿主会话真实加载/执行插件。

## 2. 根同步安全前置和新发现
- 旧 Desktop Commander Node PID20772 仍有打开的根 `scripts/team.py`、`scripts/workflow_v2.py`、`scripts/check_runner.py` 等句柄。未关闭进程，未试图释放句柄或强行覆盖。
- 已准备的 11 文件 overlay 可覆盖打包资源和部分工程文件，但进一步扩展比较发现它**不足以覆盖全部测试与开发工作树**：`tests/test_teaching_integration.py` 的候选不同，`tests/test_task_board_readiness.py` 只在候选中存在，主工程 `README.md` 亦与候选不同。
- 真正的 root→0.2.10 源/测试差异项目应计 **14 项**，旧 11 项差量统计并非错误，而是范围有限。另需复制未变化但测试运行必需的 `requirements-dev.txt` 与五项 tests 资源文件。

## 3. 全新隔离 shadow 升级演练：PASS
新工作树：`build/root-0210-shadow-rehearsal-20261104/worktree`；绝未覆盖旧根目录。
- 已有 `REHEARSAL_PLAN.md`、`stage_shadow.py`、`STAGE_RESULT.json`、`REPAIR_RESULT.json` 和独立 `run_rehearsal*.py` 执行入口。
- 初始模拟应用 11 文件 overlay 加上 2 项测试差异，后补进候选版 README.md 及相同的五项 tests fixture、`requirements-dev.txt`。
- 第一次完整测试：130 tests / 36 ERROR、exit1，原因是 shadow 缺少 README.md 和 tests 资源文件；原始结果 `TEST_RESULT.json` 保留。
- 第二次完整测试：130 tests / 1 ERROR、exit1，缺少 requirements-dev.txt；原始结果 `TEST_RESULT_RETEST.json` 保留。
- 第三次完整测试：130 tests / 1 ERROR（WinError10053 连接中止）、exit1；还出现外层 GBK 打印异常；原始 `TEST_RESULT_RETEST2.json` 保留并独立读取确认测试本身未通过。
- 针对性教学服务测试：5/5 PASS、exit0，`TEST_TARGETED.json` 保存。
- 最后完整回归：130/130 PASS、exit0，53.550 秒，`TEST_RESULT_FINAL_ATTEMPT.json` SHA256 `483b452cc42d549295b449094743e0bf64fdd8201e90b22e8949bb6885b5c217`。
- 最后独立读回比对：包括 package、scripts、tests（含非 Python fixtures）、README.md、requirements-dev.txt 的 **100 个候选路径逐项 SHA256 一致，0 差异**；主工程 74 个已登记 root baseline 文件在操作前后无改动。源码通过的是新隔离工作树，而非主工程的原目录。

## 4. 范围/阻断
- 本地 frozen candidate 既有 revision40 / ready=PASS、deployed=false、execution_authentication=UNKNOWN；本轮未修改其已完成检查点。
- trial-27 revision14 / runs SUBMITTED_RUNNING，尚未取得原宿主会话终态证明，不改写其证据和登记。
- 0.2.10 完整自主宿主 0/3、TEAM 0/14、ROLE 0/18、E2E 0/4 不因本轮静态资源比对或 shadow 130/130 通过而增加。
- **下一步**：需在无旧文件锁的正式工作树安全同步 14 项差异并独立回归；或将已验证的 shadow 工作树作为后续开发基线。W4/W5 全套宿主验收还需在被测会话中实际读取插件精确 release/version 并证明单写者与真实浏览器、运行服务证据。
- 本文件是模型整理的审计摘要，不应冒充第三方原始工具认证或真实部署证明。
