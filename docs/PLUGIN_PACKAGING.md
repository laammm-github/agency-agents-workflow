> 当前候选状态以 STATUS.md、WORKFLOW_V2_IMPLEMENTATION.md及实测结果为准。下文历史“尚未创建/待实现”描述不作为当前实现状态；功能范围与安全要求仍有效。

# ChatGPT 插件打包与连接配置规范（设计基准）

当前0.2.7候选在唯一Skill内增加scripts/team.py、workflow_v2.py、check_runner.py及本地检查说明；根scripts为维护源，打包逐字节核对副本并检查允许清单。辅助脚本经已有授权工具有限调用，ChatGPT资源路径不等于本机路径；按包内布局在授权目录实体化后才执行。不分发开发脚本、用户数据、运行日志或常驻执行器。下方结构及0.1.x示例保留为历史设计背景。

> 基于 OpenAI https://developers.openai.com/plugins/build/plugins 和参考项目 `codex-mcp` 的实际打包代码。当前只有方案文档，插件文件尚未创建。

## 一、推荐源码结构
```text
agency-agents-mcp/
├── plugin.json                   # P2 创建：portable 根清单
├── .app.example.json             # P2/P3 视绑定需求创建：无真实 ID 的模板
├── skills/
│   └── agency-workflow/
│       ├── SKILL.md              # 唯一首发 Skill，明确触发范围与停止条件
│       └── references/
│           ├── agent-catalog.json
│           ├── upstream-lock.json
│           └── curated-roles/    # 最小角色文本及其来源
├── scripts/                      # 角色索引/打包/检查脚本（P1/P2 实现）
├── tests/                        # 源数据/manifest/路由/包内容/安全（P1/P2）
├── assets/plugin/                # 可选插件 Logo、Icon
├── docs/                         # 本仓库设计、测试与运维文档
├── AGENTS.md
└── README.md
```
生成物建议统一输出到 `build/plugin/` 与 `build/agency-workflow-plugin.zip`，不提交真实注册 ID、输出 ZIP 或缓存；建立 `.gitignore`。

## 二、根 plugin.json（草案示例，实施时按官方 schema 校验）
```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "agency-agents-workflow",
  "version": "0.1.0",
  "description": "Apply curated Agency Agents workflows using already authorized tools.",
  "skills": "./skills/",
  "extensions": {
    "com.openai": {
      "interface": {
        "displayName": "Agency Agents Workflow",
        "shortDescription": "Role-guided workflows with verifiable tool evidence",
        "longDescription": "Use selected Agency Agents roles to guide local project analysis, controlled changes, reviews, and evidence-based delivery through tools the user has already connected.",
        "developerName": "Private workspace",
        "category": "Developer Tools",
        "capabilities": ["Read"]
      }
    }
  }
}
```
这是设计示例，非已验证的发布包。声明 Write 能力前必须完成权限和受控修改的实测验收。

## 三、与已有 OmniTool App 的映射
- **Skills-only 模式**：包中不存在 `.app.json`，根 manifest 不声明 `extensions.com.openai.apps`；运行期由 ChatGPT 查找用户已经安装、获授权的工具。必须在真实会话验证工具可见性。
- **App 绑定模式**：新建部署生成文件 `.app.json`，结构由平台导出映射确认（本文件不再规定 ID 前缀或把示例当作已验证 schema）；在生成包的 `plugin.json` 设置 `extensions.com.openai.apps = "./.app.json"`。
- 从平台登记/导出获得真实映射，并在目标宿主验证。2026-10-28 官方打包页使用 `plugin_asdk_app...` 登记标识，与此前参考工程的 `asdk_app_...` 写法有差异；禁止自行去掉前缀。以平台产物和宿主实测为准，格式不确定时只阻断绑定版。插件实例 `Plugin_...` 不能代替已注册映射。
- `.app.example.json` 只能包含明显的占位符（如 `REPLACE_WITH_REGISTERED_APP_ID`），绝不写入已绑定用户 ID；源代码与发布归档分别审查。
- `.app.json` 仅声明依赖，既不会安装 OmniTool，也不会绕过管理员/用户对该 App 的连接和操作授权。
- 浏览器连接器只有获得可验证的独立 canonical App ID，且确实需要强依赖时才纳入映射；第一版不要猜测依赖。

## 四、MCP/网络边界
- 本项目不是原有 `codex-mcp` MCP 执行平台，不应复制它的 runtime、原生执行器、审批控制器。
- **不用 `mcp.json`** 是合理的 V1 选择；未来如果要打包属于本插件自己的 MCP 服务，才创建符合 portable schema 的根 `mcp.json`。
- Web 不会因为 ZIP 中含 `stdio` 命令就获得本地执行权；远程 MCP 需要经支持的注册方式、可达 HTTPS/受控隧道及用户认证。

## 五、打包与验收流程（待 P2 实现）
1. 从固定上游 commit 生成最少角色引用，将 `agent-catalog.json` 和源文件/版本注记复制到 `skills/agency-workflow/references/`。
2. 校验 `SKILL.md` 的 YAML Frontmatter、短描述、唯一触发意图；不存在同名的 OmniTool `bug-fix`/`code-review`/`browser-acceptance` Skill。
3. 生成部署专用 `plugin.json`，可选写入匹配的 `.app.json`；静态检查无真实密钥、路径逃逸和本地绝对路径。
4. 仅打包允许的根清单、Skills、引用资源、可选图标和必要的 `.app.json`；不打包本地业务代码、Git 历史、缓存、测试数据或已有 OmniTool runtime。
5. 验证 ZIP 根目录直接包含 `plugin.json`，引用路径与实际文件完全一致，所有可选依赖都是真实绑定。
6. 先安装为私人插件；在 ChatGPT 新对话测试 Skill 路由、App 发现、设备/工作区权限、读操作，再单独测试经授权的小改。
7. 保存脱敏验证证据；对照 12 场景测试，未验证的功能不得标记完成。

## 六、与参考工程的关系
- 参考：`D:\ai-coding-workspace\codex-mcp\plugin.json`、`.app.example.json`、`scripts/prepare-chatgpt-plugin.mjs`、`tests/plugin/`。
- 新项目复用其**打包契约与经验**，不直接运行其脚本构建本项目（脚本包含 omnitool 专用身份、连接及输出路径）。
- 官方：https://developers.openai.com/plugins/build/plugins；插件架构：https://developers.openai.com/plugins/concepts/plugins。

## 七、本轮修订：候选包与发布门槛
- 首版只要求 Skills-only；App 绑定是后续可选产物。绑定未验收不得声称成功，但不阻塞 Skills-only 安装验收。
- 清单示例中的 skills 字段应在 P2 对固定版本的 portable schema 实测兼容性；不能因兼容清单示例含该字段就跳过 schema 验证。记录 schema URL、版本、内容哈希与本地校验输出。
- 构建使用固定输入和允许清单；拒绝目录穿越、软链接/重解析点逃逸、Windows 大小写重名和重复 ZIP 路径。只打包精选角色引用闭包及许可/归属文本。
- 输出内容清单（相对路径、SHA256）及 ZIP 哈希，统一条目排序与时间戳；同输入应得到相同内容清单。日志、真实绑定信息和 ZIP 不进入源码提交。
- 发布能力与 TEST_PLAN.md 对齐；声明修复能力后不能仍以界面的 Read 标签描述全部功能。界面标签是展示信息，不是实际授权。
- 官方复核来源（2026-10-28）：[Package your plugin](https://developers.openai.com/plugins/build/plugins)、[Build skills](https://developers.openai.com/plugins/build/skills)。公开说明只能支持格式与设计依据，不能证明当前账户安装、授权或触发成功。

## 八、全流程角色分批打包
角色目录以 ROLE_COVERAGE.md 为准，不再限制总计五类；每个发布批次只打包已核对来源/许可并通过对应检查的角色与引用闭包。目录中的 PLANNED 角色不宣称运行可用；保持唯一 agency-workflow，不新增同名任务 Skills。

## 九、完整团队交付包内容（必做）
除角色资料，候选包必须包含 agency-workflow 的团队入口、references/workflows/流程、references/schemas/数据约束和 assets/templates/工作产物模板；所有引用随包可读且通过完整性检查。构建侧校验器、fixture与测试留在源码工程，是否需要宿主运行必须明确，不把本地脚本当成Web运行时前置条件。
实际项目任务板、检查点、运行日志、用户代码和发布凭证保存在授权项目产物目录，绝不打包进插件；仅打包脱敏模板和教学资料。只有角色文件的ZIP不能称为完整团队功能包。

## 实施校正
本轮已用固定官方 schema 实测：portable 根不添加 skills 字段，宿主按固定 skills/ 路径发现；旧示例仅作历史设计。当前 Skills-only 包不含 App 绑定。工作流与模板已创建，宿主触发另验。
