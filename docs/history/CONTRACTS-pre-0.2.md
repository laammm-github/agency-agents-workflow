# V1 工具与工作流数据契约（设计稿，尚未实现）

## 1. 单一契约来源
本文是模式、任务状态、验收结论和证据字段的权威定义；架构、计划和测试文档引用本文，不另建枚举。以下是待实现的数据约束，不是现有运行时或权限引擎。

## 2. 数据对象
- AgentRecord：corpus_id、codex_slug、name、description、source_path、source_commit、content_sha256、license_reference。文件 stem 与从 frontmatter.name 得到的 slug 分别保存；同名或重复 slug 显式失败，禁止静默覆盖。来源细节见 SOURCE_MAPPING.md；上游原文与本地职责适配分别记录。
- RoleSelection：选用的 corpus_id、理由和来源引用。仅表示角色化阶段，不表示独立 Agent 实例。
- TaskEnvelope：task_id、goal、host_surface、execution_provider、target_identity、workspace、allowed_paths、forbidden_actions、mode、acceptance_criteria、authorization_ref。身份/权限不明时不进入写入。
- Preflight：target_verified、reachable、allowed_scope、capabilities、binding_check（PASS / FAIL / NOT_APPLICABLE）、evidence_refs。内置本地工具无 App 绑定时使用 NOT_APPLICABLE，不伪造连接器 ID。
- Evidence：evidence_id、task_id、timestamp（带时区）、tool、target_scope、operation、mutates、outcome、exit_code、artifact_ref、summary、before_sha256、after_sha256。非命令操作 exit_code 为 null，不编造 0；差异字段仅在文件修改时适用。引用必须能在工具结果或脱敏本地证据中定位。
- Decision：status、verdict、criteria_results、evidence_refs、blockers、tests_status（PASS / FAIL / NOT_RUN / NOT_APPLICABLE）、review_kind（ROLE_PHASE / INDEPENDENT_AGENT / NOT_APPLICABLE）。

## 3. 工作模式
- READ_ONLY：读取、搜索、Git 状态和不改变业务状态的观察；禁止补丁和会产生文件的构建/测试。
- CONTROLLED_WRITE：用户授权范围内的文档/代码补丁和验证；测试产生缓存、快照、构建输出也属于写入，应预先纳入允许范围。
- BROWSER_QA：限定站点与会话；交互是否产生提交、数据变更或外发必须先判断并取得相应授权。
- WORKFLOW_DISCOVERY：只读取已打包的角色资料，默认不联网或读取本地业务文件。

## 4. 工具选择与绑定
- 本项目在 Codex 本地开发时优先内置读取、搜索、补丁、命令和 Git 工具；只有内置能力不足或验收 OmniTool 本身时才使用连接器。
- ChatGPT 运行时发现当前宿主实际暴露、已授权且指向目标设备的工具。Skill 是指令，不是可直接 RPC 调用的 API；其他插件 Skill 只有在宿主公开且允许加载时才复用，缺失时使用本 Skill 的阶段交接规范和现有工具，不复制一套同名工程 Skills。
- portable 根 plugin.json 和唯一 agency-workflow 是包入口；清单字段在 P2 按固定版本 schema 校验，静态校验不证明真实触发。
- Skills-only 不包含 .app.json、不声明 apps；App 绑定版是后续可选交付，映射与 extensions.com.openai.apps 成对存在。
- App ID 必须来自真实登记/导出并按目标宿主验证，不从名称、前缀或页面 URL 猜测或擅自转换。Plugin_... 实例 ID 不能替代注册映射。平台格式差异记录在 PLUGIN_PACKAGING.md。
- 没有必要能力、目标身份不符或权限不足时停止。若明确声明 required 的 App 缺失，不静默切换供应方；可选工具失败后仅允许切换至已经验证且在原授权范围内的工具，并记录原因。

## 5. 状态与终态判定
status：PLANNED → PREFLIGHT → EXECUTING → VERIFYING → COMPLETED；异常终态 BLOCKED / FAILED / UNKNOWN / NEEDS_REVIEW。
verdict：PASS / FAIL / BLOCKED / UNKNOWN。原因代码记录 CONNECTOR_UNAVAILABLE、PERMISSION_DENIED、TARGET_MISMATCH、TEST_FAILED、MISSING_EVIDENCE 等，不把原因混入 status。
- BLOCKED：未具备执行条件；FAILED：实际执行或验收失败；UNKNOWN：证据不足；NEEDS_REVIEW：副作用是否发生不明，不自动重放。
- 仅当本任务所有必需验收项有证据且通过时，status=COMPLETED、verdict=PASS。发现缺陷但只读研究已完整交付，可以完成研究；不能把被研究系统也标为 PASS。
- READ_ONLY / WORKFLOW_DISCOVERY：来源引用、范围核对与结论可追溯即可；测试通常 NOT_APPLICABLE，不强求代码 Diff。
- CONTROLLED_WRITE：授权引用、变更前后差异、适用检查和审查齐全。文档修改以文档检查验收；功能修复缺必要测试时不能完成。没有 Git 时用原文快照、哈希与 unified diff，不自动 git init。
- BROWSER_QA：以可观察业务结果判定，点击返回成功不足以证明验收通过。
- 修改超出范围时停止，不丢弃已有改动；同一模型重新读取 Diff 的审查必须标记 ROLE_PHASE，不能声称独立进程或隔离 QA。
- 纯读取瞬时失败最多重试一次；修复失败后先保留证据并重新诊断，最多三次受控修复尝试；状态不明或非幂等副作用不重放。

## 6. 契约验收（待实现）
自动化覆盖合法/非法状态、证据缺失、命令与非命令 exit_code、按模式完成条件、必需 App 缺失、无 Git 差异、失败不能被后续自评覆盖。工具模拟只证明判定逻辑；宿主加载、权限、真实触发另做在线验收。

## 7. 全流程交接扩展（设计）
RoleSelection 增加 selected_roles、skipped_roles 及理由，引用 ROLE_COVERAGE.md 的角色和用例；不能把计划目录全部当成当前可用角色。
HandoffRecord：stage_id、requirement_ids、acceptance_ids、producer_role、consumer_role、artifact_refs、evidence_refs、open_questions、risks、next_preconditions、authorization_ref。缺少下一阶段必需输入时 BLOCKED；同一产物不得因角色交接丢失版本和失败记录。
需求、API/schema 或设计规格变更后由 Orchestrator 标记受影响实现/测试/文档需重验；发布验收汇总只覆盖声明的能力。RoleAvailability 区分 PLANNED、PACKAGED、HOST_VERIFIED，不与任务 status 混用。

## 8. 团队工作产物契约（最终必做）
字段规范版本 schema_version 必须存在；下列是待实现 schema，不是已有文件。各记录含 project_id、revision、updated_at 和证据/产物引用；写入前比对 expected_revision 与内容哈希，不一致返回 NEEDS_REVIEW，保留原文。
- ProjectRecord：目标、设备/工作区、工具能力、授权范围及引用、产物目录、当前里程碑和版本基线。
- RequirementRecord：requirement_id、版本、来源、目标/非目标、优先级、acceptance_ids、待决问题和确认记录。
- WorkItem：task_id、requirement_ids、owner_role、dependencies、deliverables、acceptance_ids、status、blocker_refs、evidence_refs。复用本文任务 status，不另创任务执行状态；只有依赖和门槛满足才可开始/完成。
- ArtifactRecord：artifact_id、相对路径、内容哈希、版本、producer、requirement/task/acceptance 关联、supersedes；需求到实现到测试到文档必须可追踪。
- DefectRecord：复现条件、预期/实际、严重性、相关版本、证据、owner、修复任务、回归证据。处置阶段 OPEN / FIXING / AWAITING_RETEST / CLOSED / REOPENED，与任务 status 分开；只有真实回归通过可关闭。
- ChangeDecision：变更前后版本、理由、受影响任务/产物/测试、业务决策和授权引用、需重验门槛。过期验收不得沿用到新候选。
- ReleaseRecord：候选 SHA/内容哈希、构建物哈希、环境、门槛矩阵、未决缺陷、发布授权、实际执行引用、冒烟/回滚及结果；准备就绪不等于已部署。
- IncidentRecord：环境、症状、时间线、遥测、诊断、授权动作、恢复验证、根因/未知项和预防任务。
- Checkpoint：schema_version、项目/里程碑、任务与产物索引、预期 revision/hash、最后已确认动作、未决操作、下一前置条件、证据和有效授权引用。不得保存秘密或把旧授权自动扩大到新环境。
- TeamReport：声明范围、已完成/未验收/阻塞项、需求追踪、缺陷风险、候选与环境、门槛结果、当前检查点和下一可执行项。
权限不足或 schema 版本不支持时停止依赖动作并记录；升级必须显式迁移并保留前版本，不静默丢字段。状态/产物写失败则不能声称持久化完成。工作产物保存也属于 CONTROLLED_WRITE；在既有明确授权范围内无需为每条记录反复请求批准。

## 0.1.1 约束补强
证据新增acceptance_ids及supersedes，命令非零不能PASS、非命令exit_code必须null；完成任务需关联所属证据，发布还检查所有需求覆盖、当前失败处置和实际产物哈希。检查点增加完整state与元数据索引一致性检查，旧版仅索引文档不自动恢复。需求变更保存新正文和旧版本。

## 0.1.2 二次审查补强（优先于历史描述）
- 替代失败的 PASS 必须来自新的重跑记录，双方均有带时区的有效 timestamp，且重跑时刻严格晚于失败；时间缺失、无时区、相等或更早均保持阻断。保留原失败和旧 PASS，不修改旧记录冒充重跑；时间字段校验不证明工具已执行，仍需真实输出。
- supersedes 必须指向已存在的不同产物记录，禁止循环、分叉和同一解析路径存在多个当前版本。ready、检查点导出及 resume 以未被替代的当前产物为哈希依据，历史记录保留；当前产物缺失或变化仍阻断。
- 公开 Checkpoint 的 expected_hashes 是恢复的权威基线，包括未登记为产物的源码与配置文件。resume 接收完整检查点，默认检查全部保存哈希；额外映射不得省略或替换已保存项。裸 state 恢复仍须显式哈希表。外部修改需调查并显式授权重建基线，不能用新观测值绕过旧基线。
- 普通 change/transition 保留 milestone、last_confirmed_action、next_preconditions、授权引用及保存基线。重新导出使用 previous=document；当前产物与传入基线冲突时拒绝导出，不能静默覆盖。
