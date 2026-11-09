# Agency Agents Workflow — 2026-11-04 续工实施计划 v1

目标：在不覆盖旧主项目、历史 trial、runs.json 或共享进程句柄的前提下，将 0.2.10 已发布候选推进到可独立审计的闭环，并逐步补齐原始“任务推进→失败返修→阶段交接→跨会话恢复→证据验收→最终交付”要求。此文为执行计划，不是已通过的 TASKS.md。

## 基线与证据
- 主项目 D:\\ai-coding-workspace\\agency-agents-mcp，当前根 plugin.json 仍为 0.2.8；根 team.py/workflow_v2.py 和根包内一致，但不同于隔离 0.2.10。
- 原 PRIVATE/USER 插件在线版本 0.2.10；Release pluginrel_6ae857ea7ce4819193bcd1a74d0f83b5；四个关键文件与独立候选规范化换行后一致（2026-11-04 实际读回）。
- 独立 0.2.10 候选 build/release-030-package-20261102，PREPARE-030 COMPLETED，历史 130/130 PASS，但历史本地审计指出 ready 未满足候选冻结门禁。
- trial-27 revision14 BACKEND FAILED，runs=SUBMITTED_RUNNING；原宿主停止未确认，禁止修改或创建并行写者；Desktop Commander PID20772 不强行处理。
- 严格计数以最新独立矩阵为准：自主 0/3、TEAM 0/14、ROLE 0/18、E2E 0/4。

## 分批执行、依赖与验收
### W1（P0，当前即可，只读+追加隔离审计）：候选门禁事实核验
Owner: testing-reality-checker。输入：原封存 0.2.10 候选 checkpoint / ZIP / manifest / Plugin Creator 元数据。检验 SHA256、checkpoint revision、pending、candidate/release/current board、validate/ready 的实际返回，并将失败原样留证。验收：可定位的原始运行回执，明确 PASS/FAIL/UNKNOWN；不得补写历史结论。
### W2（P0，依赖 W1）：在全新独立工作区实施候选冻结及交付门禁
Owner: engineering-devops-automator；review: testing-reality-checker。复制已验证候选只读作为输入，在新工作区先持久化 schema-v2 需求、任务、角色来源与依赖；预检→执行→QA→核验→交接。补齐 freeze manifest 和真实 candidate/ready 要件；重跑受影响测试，完成后生成最新 TASKS.md 并读取、validate、ready。不得回填 W1 原历史项目 checkpoint，不得冒充线上重新发布。验收：冻结候选哈希，最新 taskboard revision，真实命令返回及实际 ready=PASS；若需要新增任务/证据而工具不支持，则标 BLOCKED。
### W3（P0，W1 可并行只读、变更需独立确认）：历史 trial-27 恢复边界
Owner: agents-orchestrator。核查实际宿主会话结束证明、服务 PID/启动时间/健康与数据、观察器和检查点变化；仅凭 PID 消失不归档、不解除未知副作用。验收：确定可恢复/阻断的客观依据；任何不明写者保持 BLOCKED，不并发写历史。
### W4（P1，依赖 W2 且确认独立宿主能力）：严格 3 次新宿主完整自主试验
Owner: testing-reality-checker。每轮从空目录、被测会话自身核实已加载 0.2.10/Release；一名写者；提交前独立有限观察器；真实 QA FAIL→独立保存→修复→PASS、真实浏览器三类负例、同 SQLite 新 PID 重启、任务交接、最终 TASKS.md 与 validate/ready、固定候选。连续 3/3 才验收；失败保留、重新计数；不能用隔离单测冒充宿主。
### W5（P1，依赖 W4 及可用授权环境）：团队角色/场景矩阵
Owner: agents-orchestrator + testing-reality-checker。逐项核验 TEAM-01..14、ROLE-01..18，E2E-TEAM-A/B/C/D；重用可核实证据但不把子验收标全项 PASS。覆盖已有项目变更、部署故障/回滚、跨会话恢复/权限拒绝、并发冲突和角色失败交接。每项有 acceptance IDs、来源、真实工具结果、缺陷及关闭记录。
### W6（P2，W2/W4/W5 完成后）：最终交付
Owner: engineering-technical-writer + testing-reality-checker。冻结交付版本，独立确认插件版/文件哈希/测试结果/实际运行状态，完整 README/REVIEW/任务板和验收矩阵，发布动作按已有授权目标执行。最终判据为所有强制门禁通过，未完成不得声称交付。

## 本轮执行策略
1. 立即实施 W1 并保存命令与只读检查证据。
2. 在不触碰历史原目录的前提下落实 W2；若前置门禁不满足，报告具体参数、路径与错误，不绕过 CAS/原子保存。
3. W3 保持独立只读检查；因宿主侧无法证实停止时不得新建并行写者。
4. 未执行的 W4/W5/W6 维持 NOT_RUN；当前计划不被当作正式 W2 checkpoint，也不改变历史计数。

## 约束
不使用 Desktop Commander；用 OmniTool。任何本地试验不能证明远端消息端到端验收。失败先记录再返修；没有证据的完成度不虚报。计划如有变化以新版本单独更新，不篡改旧失败审计。
