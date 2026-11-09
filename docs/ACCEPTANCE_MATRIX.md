# 完整团队验收覆盖矩阵

## 2026-11-09 最新连续计数校正（优先下文）
当前 0.2.10 **连续正常宿主成功=0/3**，非下文同日早先1/3。trial-29 为历史干净PASS，trial-30 原宿主中断、仅在额外会话返修后本地 READY PASS，故中断当前连续序列。正式 runs.json SHA 4caaaef981107fe2320e6c66363a52540d4ec500814385b2863c7be5e6f6d3e4，旧结论作为历史快照保留。TEAM/ROLE/E2E 宿主级缺口不变。


## 最新验收判定 — 2026-11-09（此节优先于下方历史表）

| 范围 | 本地记录/候选 | 严格宿主结论 |
|---|---|---|
| TEAM-01～TEAM-14 | 冻结本地14/14完成，validate/ready PASS | 逐 TEAM 完整宿主职责和失败场景仍未独立全覆盖 |
| ROLE-01～ROLE-18 | 冻结本地18/18完成，validate/ready PASS | 逐 ROLE 完整宿主行为、交接、质量门禁仍有缺口 |
| E2E-TEAM-A～D | 冻结本地4/4完成，validate/ready PASS | 新建、变更、故障回滚和预定跨会话恢复仍需完整独立宿主验收 |
| trial-28 (0.2.10) | 五阶段+本地ready PASS | HOST TRANSPORT INTERRUPTED，不计正常轮次 |
| trial-29 (0.2.10) | 五阶段+本地ready PASS，独立宿主最终答复 | 严格正常 PASS，执行来源认证 UNKNOWN，计连续1轮 |
| trial-30 (0.2.10) | 五阶段+本地ready PASS，revision81，候选 trial30-candidate1 | TEXT_ONLY BLOCKED 后跨会话协助恢复，不计正常轮次 |

当前正式 \`strict_0210_consecutive_clean_normal_paths.current=1\`，要求3。历史0.2.9的统计不应跨版本混计。冻结本地 TEAM/ROLE/E2E SHA256 \`7a228496dc9cc49ef7936fb78dc0dfe80b457fe3a6f083550aad267dbdd68919\`，trial-30 最终 SHA256 \`bc6a6e9eb7373df888bedd7ea4eb28e5728433d25f1f515339454ff0f6a536da\`。全局历史证据/失败保留，旧浏览器 UNKNOWN 通过新 PASS 显式 supersede，但来源未独立认证。正式记录：\`build/host-workflow-v2/runs.json\` SHA256 \`ee3065aca59859411d5b1007a1690d28df814ba165a069eecbb73de5007cacf8\`。未部署或发布新版本。


> 2026-11-01 独立续工：trial-25 已从全新目录开始并有原始 watcher 从目录不存在时采样，宿主仍在写入；本次只旁路观察，不修改 trial-25、不中途纠错、不启动第二宿主。最新读取时 checkpoint revision2（DESIGN PREFLIGHT），仍非成功。trial-25 watcher 启动记录 kind 字段误标 TRIAL22，但真实 cmdline、ledger 和宿主 URL 均指向 trial-25；保留原始错误并在独立审计中披露。0.2.9 的 trial-22 独立 validate exit0 / ready exit1（Unfinished work），trial-23 validate/ready 均 exit0、7/7 冻结文件哈希一致、原始后端 QA 两次 FAIL 后 PASS、三项浏览器负例、SQLite 同库重启和4次交接已读回。trial-23 TASKS.md 与最终 report --markdown 投影一致；此前两次独立比较分别漏传 --markdown 与漏处理 CRLF，两份原始误报及最终追加纠正均保留，未修改 trial-23。新增 TEAM-12/ROLE-18 隔离文件锁与最终任务板测试7/7 PASS，8份原始工具捕获均核对，包含 stale digest 拒绝、Windows WinError5 原子替换失败保留提案、句柄自然关闭后原子重试成功；最外层打印因 GBK UnicodeEncodeError exit1，已另存不重跑的证据复核。这只是 helper 子场景，TEAM/ROLE/E2E 正式宿主状态不升级。trial-24 的失败打断连续成功，目前严格连续 0/3。 证据：build/host-workflow-v2/team12-role18-board-atomic-20261101/RESULT.json、FINAL_RECONCILIATION.json；trial25-independent-sidecar-20261031T164848Z.json、trial23-report-comparison-final-correction-20261031T165029Z.json。


> **2026-11-01 最新终审（优先于下方历史时点）**：trial-23 已真实归档为 `HOST_COMPLETED_READY_PASS_STRICT_CLEAN_WITH_ORIGIN_LIMITATION`，属于一轮历史严格 PASS；trial-24 原宿主自然结束并明确报告 Tunnel/MCP 连接阻断，checkpoint revision3、DESIGN EXECUTING、BACKEND 尚未启动，独立 validate PASS/ready FAIL(exit1 Unfinished work)，未达到原定 BACKEND 交接停点。已通过 CAS/原子归档为 `HOST_TRANSPORT_BLOCKED_BEFORE_PLANNED_BACKEND_HANDOFF_NOT_CLEAN`，保留所有失败；**trial-24 失败打断连续性，当前 0.2.9 连续 clean 为 0/3**，trial-23 历史 PASS 不回填或撤销。审计 `build/host-workflow-v2/trial24-independent-blocked-final-audit-20261101.json`、追加纠正 `trial24-strict-streak-correction-20261101.json`、文档 `docs/TRIAL24_FINAL_BLOCKED_20261101.md`。另完成 TEAM-11/ROLE-17 独立故障子场景首次 WinError32 FAIL→修复→13/13 PASS，**仅子场景，不提升正式 TEAM/ROLE/E2E 门禁**，见 `docs/TEAM11_ROLE17_ISOLATED_INCIDENT_20261101.md`。共享 `docs/STATUS.md`/`docs/TASKS.md` 因 PID20772 持有句柄导致原子写入 EPERM，保留未应用提案 `build/host-workflow-v2/DOCS_UPDATE_TRIAL24_LOCKED_PROPOSAL_20261101.json`，禁止绕过原子保存。

> 2026-10-31 00:12 JST 后续独立终审：只读刷新已核实的 trial-23 原宿主会话后，实际显示最终答复 `trial-23 READY PASS` 且 Stop 消失；不是人工纠错或补发任务。独立0.2.9 validate/ready均PASS，五阶段COMPLETED、22/22证据哈希、7/7冻结源码、两次原始FAIL→修复→PASS、三个真实浏览器UI负例、同SQLite跨PID重启、最终TASKS.md revision52、四次交接与观察器116次完整覆盖均核对。已CAS/原子归档 runs.json 为 `HOST_COMPLETED_READY_PASS_STRICT_CLEAN_WITH_ORIGIN_LIMITATION`，**连续严格自主成功更新为1/3**；仍保留执行来源独立认证UNKNOWN、favicon404，不等于TEAM/ROLE/E2E全项PASS。审计 `build/host-workflow-v2/trial23-independent-final-host-completed-audit-20261031.json`、原始工具返回 `trial23-final-independent-returns-20261031.json`、文档 `docs/TRIAL23_FINAL_AUDIT_20261031.md`。此前“trial-23 仍在执行、0/3”的段落为历史时点记录，已被本条最新归档结论更新。

> 2026-10-31 23:52 JST 独立续工：trial-22 保持 revision43，重新用已发布0.2.9 shadow helper 实测 validate=PASS/exit0、ready=FAIL/exit1（Unfinished work），历史归档不变。trial-23 checkpoint仍revision52，原宿主 UI 仍显示 Stop/未完成、runs.json仍SUBMITTED_RUNNING；从10:32:56Z至14:52:27Z约4.3小时无新文件，判定 POSSIBLE_HOST_UI_STALL 而非已结束，不能启动并发新宿主或计 clean 1/3。新只读 ROLE-02/TEAM-01 代码路径审计核对7/7冻结文件和4份原始浏览器回执，发现 /health 恒定返回 ok、未检测 SQLite，log_message 静默、无 metrics 路由、favicon 未映射；这是 ROLE-02 局部证据和 TEAM-11/ROLE-17 待测缺口，不是完整宿主PASS。证据 `build/host-workflow-v2/ROLE02_CODEPATH_READONLY_20261031.json`、`trial23-host-active-stale-observation-20261031.json` 和 `docs/ROLE02_CODEPATH_AUDIT_20261031.md`。原历史 trial-22/23 均未改动，严格计数仍0/3。

> 2026-10-31 trial-23 已出现五阶段 COMPLETED、最终 TASKS.md revision52、独立 validate/ready PASS、22条证据文件哈希、浏览器三项拒绝与 SQLite 重启回执。原宿主 UI 仍在回应，不能计 clean 1/3 或 TEAM/ROLE 全项 PASS。证据 build/host-workflow-v2/trial23-independent-gates-observed-20261031.json。root 0.2.9 原子同步仍被 PID20772 持有的 team.py/workflow_v2.py 句柄阻断；见 ROOT_HELPERS_029_LOCK_PREFLIGHT_20261031.json。STATUS.md/TASKS.md 的同步提案因同一共享进程文件锁暂存于 build/host-workflow-v2/TRIAL23_DOCS_UPDATE_PROPOSAL_20261031.json。

> 2026-10-31 TEAM-14 子验收新增：0.2.9 真正 CLI 双写竞争时，首个 checkpoint 更新 exit0/成功，第二个持旧摘要 exit1/Stale checkpoint；已保存状态与两次原始返回、完整旧提案，结果在 `build/host-workflow-v2/team14-cas-conflict-20261031/TEAM14_CAS_RESULT.json`。它证明本地 CAS 冲突拒绝，不证明完整 TEAM-14 多角色自治处理，原总体 NOT_PASSED 不变。


> 2026-10-31 当前验收补充：trial-22 具有真正的后端 FAIL→PASS、三项浏览器 UI 拒绝和重启持久化证据，但 HANDOVER 未完成、独立 ready FAIL，严格整轮仍0/3。trial-23 在全新目录经提交前只读 watcher 观察后已单次启动，尚未完成。独立 TEAM-08/ROLE-15 AppSec 负例扩展为路径穿越 RED→GREEN 与 SQL 注入式标题持久化，6/6 隔离测试 PASS，未自动升级为 TEAM/ROLE 全项 PASS。


> 2026-10-31 trial-22 新证据覆盖真实后端 FAIL→PASS、三项浏览器 UI 负例和 SQLite 同库重启，属于有价值的局部研发证据。但最后 HANDOVER 未结束、ready 明确 FAIL、宿主消息传输超时，严格整轮 FAIL/不计 3/3，不能用验收方手工完成交付以改记成功；独立归档 `build/host-workflow-v2/trial22-stall-independent-audit-20261031.json`。

> 2026-10-31 独立续工：正式 trial-22 仍在自主写入，采样器 PID37228 存活，最近读回 revision15（DESIGN COMPLETED、BACKEND EXECUTING），不得并发修改或人工纠错，完整成功 0/3。全新合成 V2 工作区的 TEAM-03/ROLE-04 协调门禁完成正常路径及五项预期拒绝，6/6（首次测试参数错误与 Windows 大小写不敏感文件名冲突保留，另有纠正记录）；不是完整宿主角色验收。TEAM-04 实为设计团队，不能将该测试归类为 TEAM-04。18/18 ROLE 源文件 SHA 和 14/14 TEAM route 引用完整性通过，仍不是正式团队执行证明。证据 `build/host-workflow-v2/team04-role04-isolation-20261031`、`build/host-workflow-v2/role-source-audit-20261031.json`。

> 2026-10-31 最新归档：trial-21 宿主状态/任务板/独立 0.2.9 validate/ready 全 PASS，但旧观察器断线且缺规定 FAIL→修复→PASS，严格连续试验 0/3。trial-22 已在提交前启动有限只读 watcher 并单次提交正式 High 会话，未完工。安全 TEAM-08/ROLE-15 额外隔离 fixture 实际路径穿越 RED (200/exit1) → 修复 GREEN (403/exit0) + 5/5 全回归 PASS，材料 `build/host-workflow-v2/appsec-traversal-20261031/APPSEC_RESULT.json`；**只是局部正反证据**，不代表 TEAM-08、ROLE-15 正式完整宿主验收 PASS。正式 TEAM/ROLE 总体状态不升级。

> 2026-10-31 trial-20 宿主完成、候选 `ready=PASS`、最终 TASKS.md revision55 一致，属于明显进展；但采样器真实 COMMAND_TIMEOUT 造成 revision3→55 独立观察缺失，且空标题和非法状态 browser UI 负例缺独立原始操作回执。因此正式 3/3 计数仍 0/3，TEAM/ROLE/E2E 全项不得整体标记 PASS。证据 `build/host-workflow-v2/trial20-independent-final-audit-20261031.json`。

> 2026-10-31 E2E-TEAM-D 补充：真实 helper 命令在隔离的、明确合成重定向的检查点上完成正常恢复预检（需授权再核验）和四种拒绝场景，共 5/5 符合预期，原 trial-18 checkpoint SHA 不变。证据 build/host-workflow-v2/e2e-team-d-resume-isolation-20261031-r2/E2E_TEAM_D_RESULT.json，r0/r1 验收器失败保留。此证据不证明工具权限失效的真实宿主过程或认证跨会话执行，因此完整 E2E-TEAM-D 仍 NOT_PASSED。

> 2026-10-31 E2E-TEAM-B 隔离子验收补充：旧项目数据库迁移、需求 v1→v2、新老客户端兼容与真实 HTTP 拒绝、同库不同 PID 持久化、旧用户修改哈希保持，全部有独立隔离执行记录；最终增强回归 9/9 PASS、首次两次 WinError32 FAIL 保留。详见 build/host-workflow-v2/e2e-team-b-existing-change-20261031。缺正式多角色 Schema V2 交接与宿主独立 QA，不能将子场景升级为全项 E2E-TEAM-B PASS。

> 2026-10-31 E2E-TEAM-C 追加非计数子验收：隔离固定候选 ZIP 构建、真实本地服务启动、注入后退出码1、固定包回滚、相同 SQLite 中任务保留、不同新旧 PID、原始日志和清理均有真实执行证据；路径 build/host-workflow-v2/e2e-team-c-isolated-20261031/E2E_TEAM_C_RESULT.json。完整宿主 E2E-TEAM-C 仍未通过，无法以单一隔离实验替代 DevOps/SRE 实际角色、事故运营、监控或其他团队场景。

> 2026-10-31 追加：trial-19 独立宿主版本核验 BLOCKED（未启动研发），0/3 不变。最终任务板 stale 的 gate 修复仅在独立复制 helper 内 34/34 PASS，主项目脚本被共享 Desktop Commander PID20772 锁住，线上 0.2.8 未变；该测试不能认定 TEAM/ROLE/E2E 已通过。

> 2026-10-31 更新：trial-18 checkpoint revision120 全任务 COMPLETED，候选文件 9/9 哈希一致、validate/ready PASS；但其动态任务板 TASKS.md 仍是 revision28，严格完整交付验收 FAIL（0/3）。此前两轮失败和非计数副本测试仍按原结论保存。详见 build/host-workflow-v2/trial18-final-autonomy-audit-20261031.json，不能将该候选门禁 PASS 升格为 TEAM/ROLE/E2E 全项通过。

> 2026-10-30 续工读回：trial-17 checkpoint revision36，DESIGN/BACKEND/FRONTEND COMPLETED，但 INTEGRATION 与 HANDOVER 仍 PLANNED。宿主传输中断、无完整自主交付，正常轮次 0/3，不能算 E2E-TEAM-A PASS。验收方隔离源码副本 API 3/3 PASS、前端静态契约 3/3 PASS，属补充测试，不是浏览器实际验收或正式跨会话恢复。详情见 build/host-workflow-v2/trial17-independent-qa-summary-20261030.json。

> 同日验收方又完成独立隔离副本的真实浏览器交互与同一 SQLite 数据库跨 PID 重启验证；具体工具返回和限制见 build/host-workflow-v2/trial17-independent-browser-acceptance-20261030.json。此新证据仅适用于验收方副本测试，不是原宿主自主演练及正式 E2E-TEAM-A 证据；全部 TEAM/ROLE 完整宿主门禁保持原状。

> 2026-10-30 发布与验收更新：原 USER/PRIVATE 插件已发布并读回 0.2.8（Release `pluginrel_6ae483a309ec81918a5974ca8445ebe8`，71 文件；发布观测 `build/release-overlay-028/PUBLISH_CONFIRMATION_20261030.json`）。独立 Windows 文件锁实测 8/8 PASS，不等于历史 trial-16 通过。新会话 trial-17 已单次提交并持续观察；截至提交时完整自主连续通过仍 0/3。以下 TEAM/ROLE/E2E 结果未因此自动升级。

本矩阵区分包内来源校验和宿主场景验收。NOT_RUN表示尚无该完整场景的验收证据，不代表没有局部试验。历史失败及最新试验见build/host-workflow-v2/runs.json。

| 用例 | 来源/能力 | 本地 | 完整宿主场景 | 证据 |
|---|---|---|---|---|
| ROLE-01 | agents-orchestrator | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-02 | engineering-codebase-onboarding-engineer | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-03 | product-manager | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-04 | project-manager-senior | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-05 | design-ux-researcher | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-06 | design-ui-designer | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-07 | engineering-software-architect | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-08 | engineering-backend-architect | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-09 | engineering-frontend-developer | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-10 | engineering-database-optimizer | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-11 | testing-test-automation-engineer | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-12 | testing-api-tester | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-13 | testing-reality-checker | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-14 | engineering-code-reviewer | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-15 | security-appsec-engineer | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-16 | engineering-devops-automator | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-17 | engineering-sre | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |
| ROLE-18 | engineering-technical-writer | 来源哈希一致/已打包 | NOT_RUN | 需对应ROLE_COVERAGE场景证据 |

| 用例 | 完整宿主状态 | 验收依据 |
|---|---|---|
| TEAM-01 | NOT_RUN | TEAM_FUNCTIONS对应完整行为及失败路径 |
| TEAM-02 | NOT_RUN | TEAM_FUNCTIONS对应完整行为及失败路径 |
| TEAM-03 | NOT_RUN | TEAM_FUNCTIONS对应完整行为及失败路径 |
| TEAM-04 | NOT_RUN | TEAM_FUNCTIONS对应完整行为及失败路径 |
| TEAM-05 | NOT_RUN | TEAM_FUNCTIONS对应完整行为及失败路径 |
| TEAM-06 | NOT_RUN | TEAM_FUNCTIONS对应完整行为及失败路径 |
| TEAM-07 | NOT_RUN | TEAM_FUNCTIONS对应完整行为及失败路径 |
| TEAM-08 | NOT_RUN | TEAM_FUNCTIONS对应完整行为及失败路径 |
| TEAM-09 | NOT_RUN | TEAM_FUNCTIONS对应完整行为及失败路径 |
| TEAM-10 | NOT_RUN | TEAM_FUNCTIONS对应完整行为及失败路径 |
| TEAM-11 | NOT_RUN | TEAM_FUNCTIONS对应完整行为及失败路径 |
| TEAM-12 | NOT_RUN | TEAM_FUNCTIONS对应完整行为及失败路径 |
| TEAM-13 | NOT_RUN | TEAM_FUNCTIONS对应完整行为及失败路径 |
| TEAM-14 | FAIL（其余负例待测） | trial-06恢复中出现并发写者、重复服务和冲突报告；保留早期错误与后续自主复验，见trial06-* |

| 综合用例 | 当前状态 |
|---|---|
| E2E-TEAM-A | NOT_RUN |
| E2E-TEAM-B | NOT_RUN |
| E2E-TEAM-C | NOT_RUN |
| E2E-TEAM-D | FAIL（已测中断恢复，其他阻断用例待测） |

0.2.7主工程125项回归、确定性包、私人更新及规范化资源读回已通过（build/workflow-v27），0.2.6的108项证据保留在build/workflow-v26。本地回归、私人发布成功与失败或中断Demo尝试不能填写为完整团队宿主PASS。没有真实授权的测试部署环境则相关项BLOCKED，不能删除门槛。执行细则见[宿主验收协议](HOST_ACCEPTANCE_PROTOCOL.md)。

## 后续场景绑定（计划，尚未执行）

历史0.2.4曾连续通过两轮及trial-08跨会话正常恢复，之后trial-09/10发现流程问题，不能作为当前0.2.7三轮计数。trial-11第二会话被验收器脚本核验权限遗漏阻断；trial-12仅后端暂停点通过，第二会话未完成正式浏览器证据/交付并遗漏阶段失败，整轮FAIL。当前0.2.7主工程125项通过、私人更新及规范化资源读回通过，新的正常轮次13/14/15待执行，连续0/3。证据见STATUS与runs.json；这些局部结果不代替下列完整角色场景。每项仍按ROLE_COVERAGE要求核对实际来源读取、职责、交接及正常/失败路径；同会话审查始终为ROLE_PHASE。下表是验收输入及证据要求，不是PASS结论。

| 角色 | 综合场景 | 必须核对的正常/失败行为 |
|---|---|---|
| ROLE-01 | A、D | 按任务协调；目标/能力缺失阻断；不虚构派发 |
| ROLE-02 | B、D | 实际请求从入口追到SQLite；错误目标或不可访问时报告未知 |
| ROLE-03 | A、B、D | 用户故事/验收/需求版本；关键业务决策缺失不擅自确认 |
| ROLE-04 | A、B、D | 任务依赖和变更影响；循环依赖、责任缺失提案被拒绝 |
| ROLE-05 | A | 用户旅程及体验风险；没有访谈数据明确限制 |
| ROLE-06 | A、B | 页面及正常/空/加载/错误/键盘状态；如实交付本地规格 |
| ROLE-07 | A、B、D | ADR及接口兼容性；关键契约冲突阻断实现 |
| ROLE-08 | A、B | 真实接口实现及测试；无效输入/不允许的请求拒绝 |
| ROLE-09 | A、B、C | 表单与状态交互；后端故障不显示成功 |
| ROLE-10 | B、C、D | 隔离库备份、迁移和恢复；缺授权不执行生产迁移 |
| ROLE-11 | A、B、D | 实际自动化用户路径；失败及未跑不标通过 |
| ROLE-12 | A、B、C | API契约、成功/输入/授权/依赖失败；不请求未经授权生产目标 |
| ROLE-13 | A、D | 固定候选汇总；缺必需证据或错误候选阻断 |
| ROLE-14 | B | 定位植入逻辑回归，修复前阻断，保留真实回归结果 |
| ROLE-15 | A、B | 威胁模型；隔离fixture越权/注入发现、修复及复验 |
| ROLE-16 | A、C、D | 同一可重复构建物测试部署/回滚；无发布授权停在方案 |
| ROLE-17 | C、D | 实际探测、告警、诊断、恢复与复盘；缺遥测不报健康 |
| ROLE-18 | A、B、C | 按文档在隔离目录上手；错误示例阻断交接，改进可追踪 |

批次三将在当前版本完成正常恢复后执行外部修改/未知副作用负例，保留首次结果，与正常恢复分开；trial-08历史正常恢复不代替当前版本负例。完整D还须核对权限、证据及错误输入。演练注入均明确标记，恢复前核对前后哈希，不丢弃用户修改，不自动重放未知结果。完整A计划从全新trial-16目录开始，B/C依赖其实际构建物和历史；草稿不代表已执行。
