# Agency Agents Workflow 0.2.10：QA 证据路径边界隔离验收（2026-11-03）

## 测试范围与来源
- 原私人插件：USER / PRIVATE，版本 0.2.10，Release `pluginrel_6ae857ea7ce4819193bcd1a74d0f83b5`（本轮 Plugin Creator 真实元数据读回）。
- 真实运行源：已独立核验的线上版本 `check_runner.py`，SHA-256 `7ad73950c45a12bd21fc9e5f84d17259cf9c7b4e9628bef70e9e79a5400fda64`。
- 使用 0.2.9 shadow 仅作为一致的测试 fixture/helper，不复制任何历史 Demo/试验应用源码。所有测试数据在新建隔离目录内，执行的子进程仅操作该目录。

## 原始失败假设与纠正
第一次测试试图复现 `evidence/../escaped.json` 绕过：**假设未成立**。原实现的 `team.inside` 已在执行子进程之前抛出 `ContractError('Unsafe relative path')`。该尝试原始进程 exit 1，审计 `plugin-0210-capture-boundary-20261103T0320JST/CAPTURE_BOUNDARY_AUDIT.json` 原样保留，不能报告为 RED 漏洞。
首次尝试附带的内存防护包装器 4/4 通过，但对已测试的路径属于冗余防护；不视为线上修复。

## 独立复核
新建隔离目录，直接运行未修改的 0.2.10 `check_runner.py`：3 个非法证据路径（一级 `..`、嵌套 `..`、绝对路径）均被拒绝，检查点 SHA-256 不变，子进程未启动，无逃逸文件。1 个合法 `evidence/valid.json` 正常运行，exit 0、证据文件写入指定目录。**4/4 PASS，测试进程 exit 0**。
证据：`build/host-workflow-v2/plugin-0210-capture-boundary-confirm-20261103T0322JST/CAPTURE_BOUNDARY_CONFIRMATION.json`，并保存 `RAW_STDOUT.txt`、`RAW_STDERR.txt`、`EXIT_CODE.txt`、运行脚本与独立 fixture。

## 宿主门禁与剩余事项
本轮只读核查 `runs.json`、trial-22/trial-27 检查点、观察器和 `docs/STATUS.md`、`docs/TASKS.md`：trial-22 revision43，历史 HANDOVER 未完成且 ready FAIL；trial-27 revision14、BACKEND FAILED，运行登记仍 `SUBMITTED_RUNNING`，没有可靠的原宿主结束证明。原观察器进程未发现，但不能仅凭进程消失证明宿主结束。
共享 Desktop Commander PID20772 仍存在，根 `scripts/team.py` 与 `scripts/workflow_v2.py` 哈希不同于 0.2.9 shadow，不能强制替换或声称 P1 同步完成。
原五项共享状态文件保持不变；本轮仅新增隔离审计和本说明。**严格连续自主验收 0/3、TEAM 0/14、ROLE 0/18、E2E 0/4，均未因本子场景改变。**
