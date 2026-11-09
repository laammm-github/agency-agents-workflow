# 架构决策记录（ADR）

## ADR-001：ChatGPT Workflow Plugin 优先于自研 Agent Runtime
- 状态：采用；时间：2026-10-28。
- 依据：Agency Agents 主要提供 Markdown 角色与流程指引，ChatGPT 已连接工具可以承担实际执行。
- 决策：做按需加载的 Skills，不在 V1 自研分布式任务调度器。
- 代价：普通 Chat 无法保障持续后台工作；确有长期任务再评估 Work/外部调度。

## ADR-002：只读优先、工具执行与 Prompt 规则分离
- 状态：采用。
- 决策：角色是专业规范；数据、写入与命令权限必须由宿主工具/连接器控制。
- 结果：插件不宣称自己可强制实现独立 QA 沙箱或完整权限隔离。

## ADR-003：上游源码双标识与快照版本
- 状态：采用。
- 决策：分别保存文件 stem/corpus_id 和从 name 得到的 slug；索引固定 Git commit。
- 结果：Runbook 不误指向角色，支持稳定溯源和上游差异审查。

## ADR-004：插件打包规范
- 状态：规划采用，待校验。
- 决策：首选根 plugin.json + skills/ 的可移植 Agent Plugins 格式；仅在兼容需求下加 .codex-plugin/plugin.json。
- 依据：https://developers.openai.com/plugins/build/plugins
- 结果：不提前创建空 MCP 配置，不把现有 OmniTool 伪装为该插件自带服务。

## ADR-005：目标设备连接不可靠时阻断执行
- 状态：采用。
- 决策：连接器断线、429、权限不足、工作区不符均返回 BLOCKED/UNKNOWN。
- 结果：不能把工具注册存在视为真实电脑可操作；有备用连接器时仍需核对机器与权限。

## ADR-006：发布范围与验收
- 状态：采用。
- 决策：首先个人私有部署，12 个真实场景与无插件基线对照。
- 结果：未有真实场景证据前不宣称生产级或明显优于普通 ChatGPT。

## ADR-007：复用 OmniTool Skills，减少工作流路由竞争
- 状态：部分由 ADR-009 替代（直接委派假设）；2026-10-28 对照 `D:\ai-coding-workspace\codex-mcp` 当前 portable 插件。
- 决策：MVP 仅维护 `skills/agency-workflow/SKILL.md`。角色指导与 Agent Handoff 在该 Skill 中；底层 Bug 修复、项目理解、Review、测试、浏览器验收委派给现有已授权 OmniTool Skills/工具。
- 原因：与已存在的 `bug-fix`、`code-review`、`browser-acceptance` 创建同义 Skill 会增加触发冲突与维护成本。

## ADR-008：按部署模式生成 App 绑定，不在源码写死插件 ID
- 状态：采用；正式绑定尚未验证。
- 决策：根 `plugin.json` 是 portable 源，Skills-only 包不引用 App；绑定版必须生成与 `extensions.com.openai.apps` 成对的 `.app.json`，使用经过验证的 canonical App ID。
- 原因：ChatGPT 插件标识 `Plugin_...` 与已注册 App `asdk_app_...` 是不同实体；绑定不会安装 App 或授予权限。
- 参考：[PLUGIN_STANDARD_AUDIT.md](PLUGIN_STANDARD_AUDIT.md)、[PLUGIN_PACKAGING.md](PLUGIN_PACKAGING.md)。

## ADR-009：开发与在线验收分离（替代 ADR-007 的直接委派假设）
- 状态：设计采用；2026-10-28。
- 本地优先内置工具；ChatGPT 使用实际暴露的已授权能力。外部 Skill 仅在宿主允许时加载，不能作为 RPC API。
- 先交付 Skills-only 候选包；在线预检阻塞在线验收，不阻塞本地开发。App 绑定是可选分支，浏览器按能力单独发布。
- 状态/证据只以 CONTRACTS.md 为准；QA 默认 ROLE_PHASE，发布门槛按 TEST_PLAN.md 分级。
- ADR-008 的 ID 处理以平台真实导出与目标宿主验证为准，不根据前缀自动规范化。

## ADR-010：用户授权扩展完整研发流程
- 2026-10-28 设计采用：以 ROLE_COVERAGE.md 的 18 个真实上游角色覆盖通用 Web/服务研发流程，替代原五类上限。
- 唯一 Skill、最小角色加载、默认顺序角色化阶段和证据门禁继续适用；新增角色逐个有验收场景，P7–P9 分批交付，不增加自研 Runtime。
- 本轮仅更改方案，角色存在不等于能力可用；生产动作保留独立授权边界。

## ADR-011：完整团队功能是最终目标，角色覆盖不足以完成
- 用户再次明确要求完整实现研发团队功能，方案必须从角色目录提升为行为/产物/执行/恢复/验收的完整规格。
- TEAM_FUNCTIONS 为14项必做功能与四条综合验收的权威；T-01–T-09全部进入最终范围，只读MVP是中间里程碑，不是可替代终点。
- 轻量项目任务板、检查点和恢复属于必做功能，通过已授权文件工具和包内模板/契约实现；无需常驻Runtime或自建MCP。
- 上游18角色保持不变，默认顺序角色化阶段。独立进程、并行和无人值守不能由角色提示词推导；外部能力缺失应阻断相关最终验收，不能删除必做需求。
