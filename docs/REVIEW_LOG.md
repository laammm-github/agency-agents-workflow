# 三轮方案 Review 与优化记录

> 本文记录设计审查，不等于源代码 Review、平台安装验证或功能测试。
> 审查目标：可行性、可信执行、安全边界、成本和实际可衡量效果。

## 第 1 轮：平台与源码一致性
- 发现：把 GitHub Markdown 当作可执行多 Agent 运行时的风险；Runbook corpus_id 与 TOML slug 不同。
- 发现：旧式 .codex-plugin/plugin.json 与可移植根 plugin.json 的差异；用户当前 ChatGPT 能否跨插件调用需实测。
- 调整：采用分层 Skill + 参考数据 + 已连接工具；保留双标识与来源 SHA。
- 验证点：上游索引一致性、官方 manifest 检查、实际插件触发。

## 第 2 轮：权限、可靠性与证据
- 发现：角色 Prompt 不能真正限制本地文件写入；设备/工作区可能不相同；Codex/Agent 自述不能替代执行证据。
- 调整：默认只读、工具层权限、危险动作确认、脱敏记录、失败转 BLOCKED/UNKNOWN。
- 调整：Dev 与 QA 职责分离；只有真实测试和 Git Diff 支撑完成状态。
- 验证点：路径越权、连接失败、注入诱导、QA 失败四种阻断场景。

## 第 3 轮：范围、性能和产品收益
- 发现：导入全部 Agent、每个任务都启动完整流水线，成本高而价值难证实。
- 调整：MVP 五类核心角色、三种任务模式；先最短本地闭环，再按需求扩展 Runbook 和 Memory。
- 调整：固定 12 个场景，与普通 ChatGPT 同任务对照；设强制安全门槛。
- 验证点：任务成功率、人工介入、工具调用次数、完成证据和耗时。

## 审查结论
- 架构评估：可实施，优先插件化并复用现有连接器。
- 未验证：私人插件创建/安装、跨插件调用、本地 Windows 联通、12 个端到端场景。
- 当前产物：实施文档，仅供后续 AI Coding 工作依顺序执行。

## 第 4 轮：以完成的 codex-mcp 插件为工程基准（2026-10-28）
- 取证：只读检查 `D:\ai-coding-workspace\codex-mcp` 的 portable `plugin.json`、`.app.example.json`、`scripts/prepare-chatgpt-plugin.mjs`、`tests/plugin/` 和 Web 安装说明；Git 位于 `release-v1.0` 且工作树干净。
- 重要问题：缺少 App 绑定生成逻辑、ZIP 包结构契约，以及区分 `Plugin_...` 与注册 `asdk_app_...` ID 的规则。
- 重要问题：原计划多个本地开发与浏览器 Skill 会重复 OmniTool 现有的 bug-fix、code-review、browser-acceptance 等，增加路由冲突。
- 修订：明确唯一 `agency-workflow` Skill、Skills-only / 已注册 App 两种构建模式、上游 references 随包、自动化打包检查、网页版独立验收门槛。
- 证据：[PLUGIN_STANDARD_AUDIT.md](PLUGIN_STANDARD_AUDIT.md)、[PLUGIN_PACKAGING.md](PLUGIN_PACKAGING.md)。
- 结果：**文档已修改**；并未创建插件代码或安装成功的 ChatGPT 插件。

## 第 5 轮：本地开发、契约与交付门槛（2026-10-28）
本轮仅设计文档优化，未实现插件、安装依赖或调用 OmniTool。

| 级别 | 原问题 | 修订与退出条件 |
|---|---|---|
| 高 | P2-04 强依赖绑定版，Skills-only 无法独立交付 | P2-04 改依赖 P2-02/P0-01；绑定 DEFERRED |
| 高 | 其他插件 Skill 被当作可调用执行接口 | 区分可加载指令与工具能力，定义无外部 Skill 的阶段交接路径 |
| 高 | 自动去掉登记 ID 前缀缺乏当前依据 | 保留平台映射并验证宿主；不确定只阻断绑定版 |
| 高 | 10/12 容许失败路径漏验 | 按声明能力列必过项，10/12 仅补充效果指标 |
| 中 | 模式、状态、原因、结论混用，研究也要求测试/Diff | CONTRACTS 统一字段与按模式完成条件 |
| 中 | 当前目录无 Git，缺基线替代方案 | 保存原文快照、哈希和 unified diff，不擅自 git init |
| 中 | 模拟路由被当作真实触发；角色审查被称独立 | 分开静态契约、宿主触发与 ROLE_PHASE/INDEPENDENT_AGENT |
| 中 | 数据许可/引用闭包/包可重复性缺可执行门槛 | 在 P1/P2 与测试计划中补充失败路径和内容清单 |

证据：本地读取全部设计文档；git status 返回非仓库；官方 Package your plugin / Build skills 已实际打开。未改变上游角色、slug 或 Runbook 映射；未来实现 P1 仍须核对真实上游。
修改前快照和本轮检查、统一差异在 STATUS.md 的外部证据目录中；不把历史参考工程结论当作本轮验证。

## 第 6 轮：按用户要求扩展完整研发流程
原五类角色只覆盖理解与前端小修复，缺需求/计划、体验/系统设计、后端/数据、明确测试、安全、交付运维及文档职责。新增 ROLE_COVERAGE 为统一职责/场景目录，同步根约束、PRD、架构、来源映射、契约、计划与验收。
本轮核对固定上游 SHA 的 18 个实际角色文件；GitHub API 返回 403 限流后改用 git ls-remote 与 raw 固定 SHA 读取；一次 TLS 读取失败后只重读缺失文件并成功。没有执行上游脚本或原文中的指令。新增角色验收尚未执行。

## 第 7 轮：按完整团队功能而非角色数量复核
结论：此前仅部分符合。18角色和阶段场景已覆盖职责，但需求/任务运营、产物追踪、缺陷状态、版本门禁、发布执行、事件反馈及跨会话恢复没有完整实现规格；只读MVP与角色验收仍可能被误作最终出口。
修订：新增 TEAM_FUNCTIONS，定义14项必做行为、交付物和失败路径；补 Project/WorkItem/Artifact/Defect/Release/Incident/Checkpoint 契约及模板/流程/校验实现结构；T-01–T-09指定文件/依赖/覆盖和验证，四条综合E2E作为最终门槛；同步README、根约束、PRD、架构、角色/包/测试/安全/任务与状态。
本轮无角色增删或slug改写，无需重新获取上游。全部修改为文档；已有用户改动快照保留，无Git仓库，使用外部统一差异与哈希。未实现插件或运行产品测试。
