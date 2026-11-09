# 完整软件研发流程：角色与场景方案

> 2026-10-31 补充：E2E-TEAM-C 隔离事故演练前实际读取了固定 DevOps Automator 和 SRE 角色指导文件，并以同会话 MODEL_JUDGMENT 形成 ROLE_DEVOPS_SRE_REVIEW.md。演练真实执行固定包回滚及故障验证，但没有独立 Agent/真实监控 SLO 和正式 Role V2 handoff；因此它补充了角色指导依据，不等同于 trial-18 已有 16/18 的读取记录被补齐，也不将 ROLE 项目整体升级为 PASS。

> 2026-10-31 独立来源完整性验收：固定 agent-catalog.json 的 18 个角色文件逐个实际 SHA-256 核对，18/18 与本地固定来源声明一致，报告 build/host-workflow-v2/role-source-integrity-20261031.json。trial-18 checkpoint 中有 16/18 个角色读取记录，缺少 engineering-devops-automator 和 engineering-sre；已记录角色均无路径不符或 UNVERIFIED。仅表示本地角色来源与读取记录情况，不是 18 个职责、失败路径及工具执行全项验收。ROLE-01～18 正式总体结论仍 NOT_PASSED。原 2026-10-28 的 0.2.4 为历史候选信息；当前线上私人插件是 0.2.8，参见 STATUS.md。

> 2026-10-28 用户明确要求扩展角色；替代原先五类角色上限。18 个角色来源和索引已随唯一 Skill 打包，当前私人候选为 0.2.4；完整角色场景尚未验收，见 ACCEPTANCE_MATRIX.md。打包及私人插件更新不代表所有角色能力已端到端验证。

## 覆盖范围与加载规则
覆盖通用 Web/服务软件的需求、计划、体验、架构、前后端、数据、测试、审查、安全、构建发布、运行维护和文档反馈流程。移动端、嵌入式、AI训练等专项实现仍需后续有场景的角色扩展；不宣称覆盖所有技术栈。
维护 18 个可选角色，仍只创建一个 agency-workflow Skill。每次按任务选择最小角色集，只读分析不启动完整流水线；同会话顺序阶段是默认方式。角色原文中的自动派发、记忆、固定评分或自动发布要求不赋予宿主能力或权限，以用户授权和本项目证据契约为准。

## 角色、交付与验收
下表职责与验收是本项目适配设计，不是上游能力运行证明。ROLE-01 至 ROLE-18 是本地验收用例 ID，不替代上游 corpus_id。

| 用例 | 阶段 | 上游角色 | 输入 | 输出与职责 | 最小验收（含失败路径） |
|---|---|---|---|---|---|
| ROLE-01 | 全程编排 | Agents Orchestrator | 目标、授权、验收项 | 选择角色与阶段，维护证据和阻断项 | 缺必要工具时阻断，不把角色选择称为真实派发 |
| ROLE-02 | 项目理解 | Codebase Onboarding Engineer | 仓库、问题范围 | 架构/调用链地图与来源引用 | 沿一个真实请求追踪入口到数据层，无法访问时报告未知 |
| ROLE-03 | 需求定义 | Product Manager | 用户问题、业务约束 | PRD、用户故事、范围与验收条件 | 把模糊需求转成可验证标准，假设标记待确认 |
| ROLE-04 | 计划管理 | Senior Project Manager | 已明确需求、依赖 | 任务拆解、里程碑、依赖及风险 | 跨前后端任务有依赖顺序，需求变化可追踪影响 |
| ROLE-05 | 用户研究 | UX Researcher | 已有用户反馈/可用研究数据 | 用户旅程、研究计划与设计依据 | 发现体验风险；无访谈数据时不编造用户结论 |
| ROLE-06 | 界面设计 | UI Designer | 需求、旅程、现有设计系统 | 页面/组件规格、交互状态、无障碍要求 | 覆盖正常/空/加载/错误/键盘状态；无设计工具不冒称已创建文件 |
| ROLE-07 | 系统架构 | Software Architect | 需求、仓库与约束 | 模块边界、接口契约、ADR及取舍 | 跨模块方案有失败路径；重大选择缺依据时不直接实现 |
| ROLE-08 | 后端设计与实现 | Backend Architect | 接口契约、数据模型 | API/服务逻辑及单元/集成测试 | 完整实现一个接口；无权请求和无效输入被拒绝 |
| ROLE-09 | 前端实现 | Frontend Developer | 界面规格、API契约 | 组件、状态处理与前端测试 | 完成表单交互；后端失败不会显示成功 |
| ROLE-10 | 数据设计与迁移 | Database Optimizer | 模型、查询、数据量与环境 | 索引/查询方案、迁移和恢复步骤 | 在隔离库验证迁移与恢复；缺备份或授权不执行生产迁移 |
| ROLE-11 | 自动化测试 | Test Automation Engineer | 验收项、测试环境 | 自动化用例、fixture、运行报告 | 真实运行关键用户路径，失败和不稳定用例不得标通过 |
| ROLE-12 | API与集成测试 | API Tester | 接口契约、测试服务 | 契约/集成/错误码测试及报告 | 验证成功、输入错误、鉴权及依赖失败，不发未经授权的生产请求 |
| ROLE-13 | 验收与发布判定 | Reality Checker | 测试、差异、风险与验收项 | 按证据汇总发布建议/阻断清单 | 故意缺一项必需证据仍阻断；不以默认评分或固定缺陷数量代替证据 |
| ROLE-14 | 代码审查 | Code Reviewer | 补丁、相关源码、测试 | 可定位缺陷、范围/兼容性审查 | 发现一个植入的逻辑回归；同会话审查标 ROLE_PHASE |
| ROLE-15 | 应用安全 | Application Security Engineer | 信任边界、代码与依赖 | 威胁模型、安全发现及修复验证 | fixture 的越权/注入被发现并验证修复；不擅自对外扫描 |
| ROLE-16 | 构建与交付 | DevOps Automator | 候选版本、环境和授权 | CI/CD配置、构建物、部署及回滚方案 | 测试环境构建/部署/回滚有日志；缺发布授权仅生成方案 |
| ROLE-17 | 运行维护 | SRE (Site Reliability Engineer) | 服务指标、SLO、告警与日志 | 监控方案、运行手册、故障排查及恢复建议 | 测试环境演练告警到恢复；缺遥测不声称服务健康 |
| ROLE-18 | 文档交接 | Technical Writer | 接口、实现和验证结果 | README、API说明、变更记录与操作手册 | 隔离环境按文档完成上手；示例与真实接口不符时阻断文档验收 |

## 职责边界与交接
- Product Manager 定义做什么和验收标准；Senior Project Manager 管依赖、范围和推进，不能替用户批准需求或上线。
- UX Researcher 提供用户问题依据；UI Designer 定义交互和视觉规格；Frontend Developer 实现并验证。已有稳定规格时跳过研究/设计，但记录依据。
- Software Architect 管系统边界；Backend Architect 负责服务设计及契约内实现，保留真实上游名称；Database Optimizer 管查询/索引与迁移风险，不独占所有后端实现。
- 开发者负责单元测试；Test Automation Engineer 负责用户路径自动化与回归编排，API Tester 负责接口集成；Code Reviewer 检查代码，Application Security Engineer 检查信任边界，Reality Checker 汇总验收证据。它们不替代真实工具测试。
- DevOps Automator 管构建、部署和回滚；SRE 管可观察性、SLO和恢复。Technical Writer 贯穿各阶段，不等到发布才补文档。
- 每次交接记录需求/验收项 ID、产物和证据引用、未决问题、已选/跳过角色理由、下一阶段前置条件。契约变更必须同步实现、测试和文档；必需门槛失败退回责任阶段，不无限循环。

## 场景组合
| 场景 | 按需角色链 | 完成门槛 |
|---|---|---|
| 只读理解/评估 | Orchestrator → Onboarding，按问题补架构/安全 | 来源可追溯且无业务写入 |
| 新建前后端功能 | 产品 → 项目计划 → 研究/设计 → 架构 → 前后端/数据库 → 测试/审查/安全 → 验收 → 交付/文档 | 需求到代码、测试、文档一一对应；上线单独授权 |
| 已明确小 Bug | Onboarding（需要时）→ 相关开发 → 适用测试 → 审查 | 不强制经过研究设计；真实回归通过 |
| 数据迁移 | Backend Architect + Database Optimizer → API Tester/Reviewer → DevOps/SRE | 隔离库迁移与恢复、差异、授权齐全 |
| 发布与回滚 | Reality Checker → DevOps → SRE + Technical Writer | 候选版本有证据，目标环境核实、显式发布授权、回滚演练 |
| 线上问题与迭代 | SRE → 相关开发/数据库/安全 → 回归/审查 → 文档 → 产品反馈 | 诊断、恢复和复发验证有证据；无遥测保留未知 |

## 分批实施与能力开放
A：现有只读 MVP；B：需求、架构、前后端及数据闭环；C：自动化/API/安全及验收闭环；D：交付、运维、文档反馈闭环。
每批按 ROLE 用例验证来源、路由、交接、失败路径和实际工具执行后才开放相应能力。角色可以先进入设计目录，但未随包验证的角色标为 PLANNED/UNAVAILABLE。角色适配要求 ROLE-01–18 全部适用项通过；最终团队交付还必须通过 TEAM_FUNCTIONS.md 的 TEAM-01–14 及四条综合 E2E，不能只凭角色场景或原 10/12 指标完成。

## 来源证据
固定来源为 commit `b37b5bb33b78f2c1d6567d98e25ca818e3259219` 下的 18 个真实文件和 frontmatter；已生成 `skills/agency-workflow/references/upstream-lock.json` 与 `agent-catalog.json`。本轮重新逐一对比固定提交源码 ZIP、包内角色及索引 SHA256，18 项一致，证据见 `build/workflow-v2/role-source-recheck.json`。角色原文未改；许可及分发要求见 PLUGIN_STANDARD_AUDIT.md，完整宿主角色验证另见 ACCEPTANCE_MATRIX.md。

## 角色与完整团队功能的关系
本文件只定义角色，不是最终功能规格。[TEAM_FUNCTIONS.md](TEAM_FUNCTIONS.md) 定义必须实现的团队行为；需求管理、任务推进、可恢复状态、版本/缺陷/发布/事件记录必须有真实产物和执行路径。无需新增角色即可补齐这些协作功能；本轮未改变上游角色、slug 或来源映射。
