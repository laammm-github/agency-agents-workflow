# 实施任务板（规划起点）

## 0.1.2 二次审查修复（最新）
4 项发现已完成本地修复，新增 11 项回归，56 项全量测试通过（exit code 0）。见 REVIEW_FIXES.md、build/review2-verification.json 和 build/review2-changes.diff。私人插件已更新至 0.1.2 并读回核对，release 为 pluginrel_6ae202bd5d208191bd335deb2f93528f；完整团队宿主验收仍未完成，T-09 状态不变。

规则：任务状态仅在获得文件与实际测试证据后从 TODO 改为 DONE；执行失败标记 BLOCKED 并附具体原因。禁止无凭据勾选。

| ID | 任务 | 状态 | 依赖 | 完成证据 |
|---|---|---|---|---|
| DOC-01 | 需求、架构、AI Coding、安全、测试文档落地 | DONE | 无 | 文档存在与后续标准复核 |
| DOC-02 | 对照 codex-mcp 与官方格式，修订插件包方案 | DONE（文档） | DOC-01 | PLUGIN_STANDARD_AUDIT、PLUGIN_PACKAGING，相关文档修订 |
| DOC-03 | 本轮设计评估与文档一致性修订 | DONE（文档） | DOC-02 | REVIEW_LOG 第 5 轮；检查与差异记录见 STATUS |
| P0-01 | 验证 ChatGPT 插件可见性与账户环境 | TODO | DOC-01 | 实际插件发现记录 |
| P0-02 | 验证在线工具能访问目标 Windows 设备/工作区（OmniTool 为已探测提供方） | PARTIAL | DOC-01 | 本次成功列目录、读取目标文档、修改文档；设备完整身份/权限模式待验证 |
| P0-03 | 验证浏览器插件目标会话、只读快照 | TODO | P0-01 | 测试网页快照 |
| P0-L | 本地工具/路径/运行时基线（无 Git 用快照差异） | DONE（本地） | DOC-01 | 开发前实际探测记录；不要求 OmniTool |
| P1-01 | 固定上游 commit，建立源角色索引 | DONE（本地） | P0-L | SHA + schema + 角色数 + 许可 + 内容哈希 |
| P1-02 | 单测 Frontmatter、ID、slug、Runbook 映射 | DONE（本地） | P1-01 | 实际单测输出 |
| P2-01 | 创建符合 schema 的根 plugin.json 和唯一 agency-workflow Skill | DONE（本地） | P1-01 | manifest/Skill 合约检查 |
| P2-02 | 构建索引引用、打包脚本、ZIP/路由/安全测试 | PARTIAL | P2-01 | manifest + package + routing + security 自动化输出 |
| P2-03 | 可选真实注册 App 绑定版 | DEFERRED | P2-02,P0-01 | 平台导出映射、宿主实测、成对引用及独立包检查 |
| P2-04 | Skills-only 私人插件 ChatGPT Web 安装与 Skill 触发 | TODO | P2-02,P0-01 | 新会话实际触发与工具调用证据；不依赖 P2-03 |
| P3-01 | 只读本地项目分析闭环 | TODO | P0-02,P2-04 | 文件来源与工具调用结果 |
| P4-01 | 小范围代码修复 + 测试 + Diff | TODO | P3-01 | 实际变更/测试 |
| P4-02 | Code Reviewer 只读角色化审查阶段 | TODO | P4-01 | 审查报告与差异对应 |
| P5-01 | 浏览器测试闭环 | TODO | P0-03,P2-04 | 浏览器操作证据 |
| P5-02 | 12 场景对照评估 | TODO | P4-02,P5-01 | 汇总表 + 基线 |

## 工作约定
- 每个任务单独提交最小可审核改动；未授权不要创建 Git commit。
- 完成时更新本文件与 STATUS.md，必须写清验证命令、工具结果和失败项。
- DOC-01 的 DONE 仅表示文档写入，不能推断 P0–P5 的插件开发已经完成。
- DOC-02 仅证明文档通过基于真实参考工程的设计审查；没有创建 plugin.json、SKILL.md 或实际 ZIP，不能把文档 DONE 算作插件测试 PASS。

## 全流程扩展任务（用户新增）
| ID | 任务 | 状态 | 依赖 | 完成证据 |
|---|---|---|---|---|
| DOC-04 | 18角色来源核对、全流程职责与验收方案 | DONE（文档） | DOC-03 | ROLE_COVERAGE、SOURCE_MAPPING、本轮外部核对与文档检查 |
| P7-01 | 新角色来源/许可/索引/引用及路由接入 | TODO | P1/P2 | 固定来源、许可、包与路由检查 |
| P7-02 | 需求到前后端与数据功能闭环 | TODO | P3,P7-01 | ROLE-03–10 真实产物和失败路径 |
| P8-01 | 自动化/API/安全/证据验收闭环 | TODO | P4,P7-02；UI部分还需P5 | ROLE-11–15 工具与交接证据 |
| P9-01 | 测试环境交付、回滚与运维反馈 | TODO | P8-01 | ROLE-16–18 真实演练及文档上手 |
| P9-02 | 角色阶段宿主验收（非最终团队交付） | TODO | P9-01 | ROLE-01–18 适用项、全链路与权限阻断证据 |

## 完整团队功能实现（最终必须全部完成）
DOC-01–04 仅表示文档；P0–P5 的只读/修复里程碑和 P7–P9 角色场景均不代表项目最终完成。

| ID | 任务 | 状态 | 依赖 | 完成证据 |
|---|---|---|---|---|
| DOC-05 | 团队功能缺口评估与完整实现规格 | DONE（文档） | DOC-04 | TEAM_FUNCTIONS及本轮文档检查；无产品实现 |
| T-01 | 团队契约与隔离教学环境 | PARTIAL | P0-L | schemas/正反例/fixture隔离 |
| T-02 | 工程协作、任务板、检查点与恢复 | PARTIAL | T-01,P2,P3 | 依赖/追踪校验、新会话恢复与失败路径 |
| T-03 | 需求、方案与变更管理 | PARTIAL | T-02,P7角色资料 | PRD/任务/契约/设计/影响传播 |
| T-04 | 新项目/已有项目开发与集成 | PARTIAL | T-03,P4 | 前后端/数据实现、联调与原有修改保护 |
| T-05 | 质量、安全与缺陷闭环 | PARTIAL | T-04,P8；UI项还需P5 | 自动化/安全/审查/回归重开和阻断 |
| T-06 | 候选版本、发布与回滚 | PARTIAL | T-05,P9角色资料 | 固定候选、授权测试环境部署/冒烟/回滚 |
| T-07 | 运维、文档交接与反馈 | PARTIAL | T-06,P9角色资料 | 遥测/事件/恢复/上手/改进backlog |
| T-08 | 完整功能包与真实宿主适配 | PARTIAL | T-02–T-07 | 打包契约与所有入口实际触发 |
| T-09 | 完整团队综合验收与交付 | TODO | T-08,P7–P9 | TEAM/ROLE及四条综合E2E全部必需项通过 |

表中 P7/P8/P9“角色资料”指相关来源与包接入子项，不依赖该阶段的全部场景完成，避免与 T 工作包循环依赖；阶段场景最终随 T-09 汇总。团队功能详情、文件范围和验证方式见 IMPLEMENTATION_PLAN.md。

## 本轮实现证据与未完成范围
P1及P2本地检查见build/verification.json和full-agent-catalog.json，发布包63文件；create_plugin已创建私人候选并核对远端文件清单，安装/实际触发仍NOT_RUN。P2-02仍PARTIAL：静态路由/安全契约不替代宿主行为测试。
T-01–T-08均已有流程/模板/契约或校验组件与教学测试，但完整工作包验收仍未完成；状态统一PARTIAL，不以代码存在勾选DONE。T-09仍TODO，四条E2E均NOT_RUN。
实际交付产物、状态字段和教学测试边界见DEVELOPMENT.md；最终门槛以TEAM_FUNCTIONS为准，不因私有插件创建成功而降低。

## 本轮真实浏览器验收
computer use已操作既有Edge并验证私人插件详情、在聊天中试用、资料结果一致和只读负向拒绝。见[BROWSER_PLUGIN_ACCEPTANCE.md](BROWSER_PLUGIN_ACCEPTANCE.md)。结果PARTIAL，回答正文中的调用自述不算原始日志；四条综合E2E仍NOT_RUN。

## 0.1.1 审查修复（本轮最新）
14项发现均已修复并有对应回归；45项自动化测试、打包和Edge教学UI通过。私有插件同ID更新至0.1.1，release pluginrel_6ae1f921240c8191a65b3ddcac5a1274，已读回核对修改资源。见[REVIEW_FIXES.md](REVIEW_FIXES.md)及build/review-fix-summary.json。完整团队E2E仍未完成，不上调原有T-09整体状态。

## 0.1.2 新会话定向端到端验收（最新）
实际通过 Edge 私人插件详情的“在聊天中试用”进入新会话：
https://chatgpt.com/c/6ae204c4-3204-83ea-b577-5cc1bb0a8a57

页面显示版本 0.1.2、唯一 agency-workflow。新会话回答与四项更新规则一致；获受限执行授权后，通过本地连接器运行 `python -B -m unittest discover -s tests -p test_review2_regressions.py -v`。本轮原始输出及执行元数据保存到 build/host-e2e-012/result.json，Codex 内置文件工具独立读回：11 项通过，exit_code 0。调用引用 87e1b3f3-49f3-45ef-b822-48c791ac2edd，开始 2026-10-28T14:23:44.543Z，结束 2026-10-28T14:23:52.830Z。页面另观察到连接器保存动作卡片和本地实际新增文件；不是仅依赖回答中的 JSON。

结论：插件新会话到本地回归执行及证据落盘的定向链路通过，未发现新的功能失败，无源码修复。调用 ID 和原始输出来自宿主保存记录，尚未与连接器独立审计数据库核对。console/network 未采集，跨第二会话恢复、完整 TEAM/ROLE 与四条综合 E2E 仍 NOT_RUN，不能上调为完整团队交付。焦点抢占与窗口截图黑屏通过 prepare_display、屏幕 zoom 恢复，未改浏览器安全配置。

## ChatGPT 开发 Demo 实测
在既有 ChatGPT 插件测试会话中实际创建 build/demo-taskboard：Python 标准库 HTTP + SQLite + 原生中文前端，新增/状态切换/筛选/删除/刷新持久化。服务 http://127.0.0.1:8765/，PID 34244；独立读取端口绑定为127.0.0.1，HTTP 200。宿主 API 测试 3 项通过，原始结果 build/demo-taskboard/test-output.json。宿主浏览器操作见该目录 REVIEW.md，报告功能通过且 favicon 修正后 console 0 errors/0 warnings。
独立读回发现初始 checkpoint 不符合公开契约和未定位 console error，反馈 ChatGPT 后由其修复；旧 checkpoint 保留 checkpoint.legacy.json，新检查点 schema/load_state/resume 验证通过，原始结果 checkpoint-validation-output.json。Codex 另用内置工具调用 team.resume 对实际保存检查点及11个产物哈希再次核验，返回 PREFLIGHT；未替代 ChatGPT 实现代码。独立桌面最终截图受反复屏保遮挡，未据此宣称独立视觉复验通过。
结论：完成一个可运行 Demo；需独立核对交付契约，不能据此认定完整TEAM/ROLE或四条综合E2E全部通过。没有安装依赖、Git提交或公网部署。
