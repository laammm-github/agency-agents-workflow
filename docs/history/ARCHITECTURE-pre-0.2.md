# 架构设计 — 技术边界与数据流

## 1. 分层
1. ChatGPT Chat / Work：理解用户意图、推理、选择 Skill；Work 能力与账户权益需实测。
2. Plugin Skill：角色选择、工作流步骤、工具使用条件、QA 与报告格式。
3. 角色知识层：从上游 Markdown/Runbook 建立版本化角色索引；只按需读取。
4. 工具执行层：本地开发优先宿主内置工具；ChatGPT 运行期使用实际可见且授权的工具，OmniTool 是可选提供方。执行能力由工具边界约束。
5. 本地 Windows：经连接器许可的目录、进程、浏览器和软件。
6. 证据层：从工具结果构造结构化报告；MVP 不自行发明持久事务库。

## 2. 典型工作流
用户需求 → 工作空间预检 → 模式选择 → 按需装载角色 → 计划/受限执行 → 测试/审查 → 证据汇总 → 终态。
只读模式：探测 → 搜索/读取 → 事实核对 → 报告，禁止写入。
代码模式：读取 Git 状态 → 明确目标/允许路径 → 小补丁 → 真实测试 → Diff 审查 → PASS/FAIL/BLOCKED。
浏览器模式：会话/域名确认 → 语义快照 → 交互 → 可观察结果 → 截图/日志证据。
禁止凭测试计划推定测试已执行；失败的 QA 检查不得被 Developer 自评覆盖。

## 3. 上游映射
- 角色部门：divisions.json；源代理：部门目录下有合规 Frontmatter 的 Markdown 文件。
- 角色双标识：file stem 为 corpus ID（如 engineering-frontend-developer），slug 由 frontmatter.name 转换（frontend-developer）。
- Orchestrator：specialized/agents-orchestrator.md（流程规范，不是实际派发代码）。
- Runbook：strategy/runbooks.json 中 roster 列表引用 corpus ID；strategy/runbooks/ 是流程文档。
- Codex 生成规则：scripts/lib.sh、scripts/convert.sh；本插件不能假装它们直接适配 ChatGPT。
- Memory：integrations/mcp-memory/ 是接入外部服务的指南，不是内置持久化服务器。

## 4. 计划的插件结构（尚未创建）
- `plugin.json`：portable Agent Plugins 根清单，声明 `$schema`、`name`、`version`、`description` 和 `skills: "./skills/"`。
- `skills/agency-workflow/SKILL.md`：**唯一 MVP Skill**，指导角色选择、流程路由、工具前置条件和质量门禁。
- `skills/agency-workflow/references/`：随技能一起打包的角色索引、固定上游 SHA、精选原文和 Runbook 摘录。
- `scripts/`、`tests/`：生成上游索引、验证清单与打包、检验 Skill 路由；它们不是 ChatGPT 必需的插件运行时。
- `assets/plugin/`：可选品牌图标；`.app.example.json` 是不含真实 ID 的源码模板。
- `build/plugin/.app.json`：**仅注册 App 绑定模式生成**，并在对应的构建产物 `plugin.json` 中声明 `extensions.com.openai.apps = "./.app.json"`。
- `mcp.json`：只有需要随本插件分发一个受控 MCP 服务时才引入；V1 优先使用已有 OmniTool 连接。
- 详见 [PLUGIN_PACKAGING.md](PLUGIN_PACKAGING.md)；不要复制 `codex-mcp` 的 `src/`、`console/` 或 `native/` 运行时。

## 5. 插件打包与依赖边界
OpenAI 推荐 portable 根 `plugin.json`（Agent Plugins schema）；`.codex-plugin/plugin.json` 是兼容布局，不作为本项目首版的第二份身份来源。
首版仅引入 `agency-workflow` Skill，不再另建 `bug-fix`、`code-review` 或 `browser-acceptance` 等与 OmniTool 重复的 Skills；其他插件 Skill 不是 RPC API；仅在宿主允许加载时复用其指令。缺失时按本 Skill 的角色化阶段交接规范使用现有工具，不假设跨插件派发。
ChatGPT 插件不自动获得已经安装的第三方插件权限；若需要声明对已注册 OmniTool 的依赖，可在构建时生成 `.app.json`，其 App ID 必须来自真实注册过程且连接/授权依旧要逐项核查。
本地 stdio MCP 不等于网页端可直连本机；若需要自建服务，须按平台支持选用注册的远程连接或受控桥接。

## 6. 状态与证据
统一使用 [CONTRACTS.md](CONTRACTS.md) 的 status、verdict、模式和按模式完成条件；不把读取/写入模式混入状态。默认 QA 是角色化审查阶段，不代表独立 Agent 或隔离环境。

## 7. 构建与运行边界
本地 P0-L → P1 索引 → P2 Skills-only 候选包，不依赖 ChatGPT 登录、App ID 或浏览器连接。在线 P0-H + 候选包 → P3 只读 → P4 修复；浏览器验收单独推进。App 绑定是可选分支。
开发侧目录与发布侧精选资料分离；发布包只携带精选角色及其引用闭包，保留 SHA、哈希、许可。宿主不能运行构建脚本时，仍应能直接读取包内静态资料。

## 8. 完整研发流程角色层
[ROLE_COVERAGE.md](ROLE_COVERAGE.md) 定义 18 个可选角色及职责交接，替代原五类角色总上限。角色目录规模与单次加载集合分开；仍只有一个 Skill，不引入派发器或独立服务。
阶段交接遵循 CONTRACTS.md；新增能力按 P7–P9 实施并验证源资料、路由、权限和真实验收。发布、运维和数据迁移角色的存在不授予执行权。

## 9. 团队功能实现结构（必做）
完整行为以 [TEAM_FUNCTIONS.md](TEAM_FUNCTIONS.md) 为准。包内仍只有一个 Skill，按入口加载 references/workflows/ 的项目启动、迭代、缺陷、发布、事件和恢复流程；references/schemas/ 保存字段约束，assets/templates/ 保存任务板、需求、交接、缺陷、验收、发布/恢复和检查点模板。具体文件清单由实施任务 T-02/T-03 创建并验证，不在本轮生成。
宿主模型按流程选择下一可执行任务，经现有工具操作；构建侧 scripts/ 用于索引、契约/追踪/检查点校验和打包，不成为网页运行时前置条件。JSON schema 与模型指令不等同实际权限执行器。
项目运行资料在用户授权的项目产物目录保存（默认候选 .agency-workflow/，初始化前确定路径和纳入写入范围）；不保存在插件安装缓存，不打入发布包。只读模式可返回临时报告，但没有持久化证据不能宣称跨会话恢复已实现。
任务依赖、产物版本、失败证据与变更影响形成可追踪图；同一会话默认单写入者，写前核对 revision/hash，外部修改时停止而非覆盖。跨会话恢复必须重新核验目标、权限、工作树和未决副作用，不自建常驻服务或自动重放。
