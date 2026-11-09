# Agency Agents Workflow — OmniTool-only 0.2.10 续工记录（2026-11-02）

## 本轮执行范围
只使用 OmniTool 操作 Windows 工作区，不调用 Desktop Commander、不终止共享进程、不修改既有 trial-27、runs.json、主工程 helper 或已发布私人插件。所有后续实验使用新的隔离目录。

### 第一阶段：真实 Runner 缺陷修复
隔离项目 `build/release-030-runner-fix-20261102`。
- 超时前的原始 RED 已真实执行并完整落盘：runner-red.json，exit1，16个测试中新增用例1项 FAIL；checkpoint revision7，status FAILED，pending_operations为空。恢复后核对原进程/日志后**没有重放**。
- FAILED → PREFLIGHT → EXECUTING，实施预检PASS；主/包内check_runner.py分别版本化修复，两个源文件SHA256相同：`7ad73950c45a12bd21fc9e5f84d17259cf9c7b4e9628bef70e9e79a5400fda64`。
- 机制：后续真实 PASS 显式 supersedes 的先前 FAIL，仅从 task.evidence_refs 当前引用中退休；state.evidence原始失败记录和所有失败回执保留。没有 supersedes 时绝不清除失败。
- check_runner 实测定向16/16 PASS、完整130/130 PASS，退出码均0；完整结果由一发一次性QA存证，原始结果文件 evidence/runner-green.json 和 evidence/runner-full.json。
- 同会话源码审查使用 OmniTool 真实file_read捕获，MODEL_JUDGMENT标识如实。任务FIX-RUNNER正式COMPLETED、checkpoint revision17，`validate PASS`，实际生成TASKS.md。0.2.9+同内容打包两次产出同一SHA256 `59bca3ee0e7b81c03e2ecfff175bd43627e40c3e1b63b40c27737f7f1b904098`（此包插件manifest仍0.2.9，只是修复候选，未发布）。

### 第二阶段：0.2.10 独立打包候选
独立项目 `build/release-030-package-20261102`。
- 从已验证的Runner修复目录逐文件校验后隔离复制，Schema V2创建PREPARE-030 INTEGRATION任务、保存需求/角色来源/旧版文件基线，PREFLIGHT和implementation门禁PASS。
- 将plugin.json显式升至0.2.10，更新Skill版本及local-checks.md内的失败证据退休语义，更新该候选README。版本化产物/哈希及旧版本通过artifact supersedes保留。
- 首次打包实际exit1：隔离复制时误排除了两个合法checkpoint.json资源模板，包白名单拒绝。失败由实际OmniTool command_status回执写至 evidence/package-first-fail.json 及 EV-PACKAGE-RED，全局历史保留，任务转为FAILED。
- FAILED → PREFLIGHT → EXECUTING后按预检恢复两个模板的原始SHA256文件，显式登记为SOURCE输入。第二次打包通过 EV-PACKAGE-GREEN / exit0 / supersedes EV-PACKAGE-RED。
- 此0.2.10候选ZIP两次构建均为70文件，固定SHA256 `005e75607c87d7305b95c6024011f8ba39f09de44442425db44238aea478b0a7`，源ZIP的BUILD哈希登记为任务input。
- 之后的真实check_runner完整集成回归130/130 PASS、exit0、EV-RELEASE-030-FULL显式supersedes原FAIL，捕获文件 evidence/release-030-full.json，且测试前后冻结ZIP SHA没有漂移。
- 四份OmniTool实际源代码读取回执加同会话ROLE_PHASE审查分别留存；任务PREPARE-030正式COMPLETED，checkpoint revision18，TASKS.md revision18，validate PASS。
- `team.py ready --candidate unprepared` 实测FAIL(exit1，Candidate manifest mismatch)。0.2.10属于**完整本地打包/集成已通过的候选**，不是完成了全项目的最终候选冻结、宿主交付或正式在线发布。
- 独立审计 `build/release-030-package-20261102/LOCAL_CANDIDATE_030_AUDIT.json` SHA256 `1be4123656fd6b81bf12dc6426905b2fc6afaab22282348a345ceee75b86025f`，确认原trial-27、runs.json、根两个helper与事前SHA一致。包路径 `build/release-030-package-20261102/build/agency-workflow-plugin.zip`。

## 最新安全阻塞
- 根工程原子同步脚本在07:43 UTC再次只读检查，返回`BLOCKED_FILE_HANDLES`：主根team.py/workflow_v2.py仍被共享node.exe PID20772句柄持有。没有--apply，没有强制杀进程，也没有绕过原子提交。
- trial-27登记仍为SUBMITTED_RUNNING，checkpoint revision14，BACKEND FAILED。缺可信宿主终态，不启动与之竞争的正式宿主试验，也不宣告原试验完成。
- 0.2.10 ZIP **尚未发布到线上私人插件**；不得从本地版本字段推断插件线上已更新。
- 严格连续0.2.9 clean仍0/3；TEAM-01..14完整宿主0/14、ROLE-01..18完整宿主0/18，E2E-TEAM A/B/C/D完整宿主0/4。局部单元/集成PASS不能升级上述总门禁。

## 下一个可执行安全动作
先通过OmniTool核实既有宿主会话真实终态与共享文件锁所有权/是否自然释放；解除实际冲突后，沿CAS/原子门禁同步根工程helper，并针对新版本进行**新的**、版本可核验的顺序宿主验收。补齐TEAM/ROLE/E2E矩阵，冻结最终候选、生成最终TASKS.md和独立ready gate。任何UNKNOWN、缺工具或锁冲突保持阻断，不重放不明副作用。

以上不包含自行安排的后台或跨会话异步执行。
