> 当前候选状态以 STATUS.md、WORKFLOW_V2_IMPLEMENTATION.md及实测结果为准。下文历史“尚未创建/待实现”描述不作为当前实现状态；功能范围与安全要求仍有效。

# ChatGPT 插件标准对照审查（2026-10-28）

> 历史设计审查；下述 ID 前缀转换和跨 Skill 委派假设已由文末本轮修订替代，不能直接作为实现契约。

## 审查对象与证据来源
- 参照工程：`D:\ai-coding-workspace\codex-mcp`；实际读取 `plugin.json`、`.app.example.json`、`package.json`、`scripts/prepare-chatgpt-plugin.mjs`、`tests/plugin/plugin-manifest.test.ts`、`tests/plugin/plugin-package.test.ts`、`tests/plugin/skill-contract.test.ts`、`docs/CHATGPT_WEB_PLUGIN_SETUP.md`。
- 参照工程 Git：读取时位于 `release-v1.0`，工作树干净；仅作参考，不修改代码。
- 官方规范：https://developers.openai.com/plugins/build/plugins ，https://developers.openai.com/plugins/concepts/plugins 。
- 目标文档：本目录下 README、ARCHITECTURE、IMPLEMENTATION_PLAN、CONTRACTS、TEST_PLAN、SECURITY、TASKS。
- 审查仅证明架构与文档一致性，**不能代替插件包校验、ChatGPT 私人插件安装或本地能力端到端验证**。

## 逐项对照
| 事项 | codex-mcp 已有事实 | agency-agents-mcp 修订后要求 |
|---|---|---|
| 插件入口 | 根 `plugin.json`，带 `$schema=https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` | 根清单作为唯一权威身份；`name/version/description/skills` 明确 |
| Skill 目录 | 根 `skills/<skill>/SKILL.md` | 首版一个 `skills/agency-workflow/SKILL.md`；不得复制 OmniTool 同名工程 Skill |
| 平台扩展 | `extensions.com.openai.interface` 与可选 `apps: ./.app.json` | 可选品牌信息；只在确有注册 App 绑定时生成 .app.json 并声明 apps |
| App 连接映射 | `.app.example.json` 用占位 ID；生成包中 `.app.json` 引用已注册 `asdk_app_...` | 同样使用占位模板+部署时注入真实 canonical App ID，禁止把 `Plugin_...` 当 App ID |
| MCP | 工程支持注册 App 绑定或携带 portable `mcp.json` 的两种打包模式 | V1 首先重用已有 OmniTool / 浏览器连接；不创建无意义 `mcp.json` |
| 本地 Web 连接 | ChatGPT Web 无法直接访问未公开的 `localhost` 或运行电脑上的 stdio 进程 | 复用已经验证的注册连接；需新 MCP 才研究 HTTPS/受控 Tunnel |
| 打包 | `scripts/prepare-chatgpt-plugin.mjs` 创建清单、技能、资源、生成 `.app.json`、ZIP | 设计独立轻量构建脚本，只复制所需文件，验证归档内容与路径 |
| 自动化测试 | manifest、package、Skill contract、Skill routing、security、smoke | V1 建同等级的轻量契约/路由/安全/安装包测试，不照搬整个执行器测试 |
| 授权 | OmniTool MCP 本地 runtime 负责路径、命令、审批和审计 | 新插件只做流程/角色指南；不得绕过 OmniTool 既有权限 |
| 生命周期 hooks | 参照源码保留 `hooks/` 资源和脚本逻辑 | ChatGPT Web V1 不启用 hooks；仅适用的桌面宿主后续再单独评估 |

## 发现的问题与修正
- Important：原计划只有 `plugin.json` 和 Skills，但没规定打包清单、生成目录、`.app.json` 的绑定/不绑定模式，容易产出不可安装或误绑定的 ZIP。
- Important：原计划创建 `browser-acceptance`、`local-code-task` 等工作流，容易与 OmniTool 自带工程 Skills 重叠并争抢触发。V1 更适合唯一 `agency-workflow` 负责路由，实际开发/测试/审查委托现有 OmniTool Skill。
- Important：此前没有将“连接器已安装、已注册、已获用户授权、指向正确设备、可调用”拆成独立验收门槛。已补强为 P0 与发布证据。
- Important：原文未区分 `Plugin_...`（插件实例 ID）、`plugin_asdk_app_...`（页面形态）及 `asdk_app_...`（注册 App 映射 ID）。现在要求只从官方登记过程获得有效 App ID。
- Minor：缺乏技能名冲突检查、引用文件复制完整性、ZIP 根目录正确性和上游版本锁等测试清单，现已补入。

## 推荐落地模式
1. **本地验证版（Skills-only）**：根 `plugin.json` + `skills/agency-workflow/` + 必要静态引用；要求宿主已安装可用的 OmniTool，但不假定它是本插件的依赖。先验证角色/流程触发。
2. **ChatGPT 已注册 App 绑定版**：在证实部署方式支持后，生成私有 `.app.json` 并使 `extensions.com.openai.apps` 指向它；`.app.json` 使用从 ChatGPT 注册页面获取的有效 App ID，按需要设置 `required`。该映射**不会**创建 App、不会授予权限。
3. **独立 MCP 版（后续）**：只有现有连接器无法提供所需角色检索能力且已验证需求时，才引入 `mcp.json` 和服务器。不能把直接在本机运行 stdio 当作 Web 端可达方案。

## 不应直接复制的部分
- 参照工程的 `src/`、`native/`、`console/`、`installer/`、Rust/Desktop/Browser Runtime、MCP 网关不属于本插件 MVP。
- `codex-mcp` 的 `package.json`、Node >=22、编译和 installer 是它的工程实现，不是所有 ChatGPT Skills 插件的强制要求。
- 参照项目的测试曾执行过，不代表本项目的任何功能或插件包已经通过同样测试。

## 修订后的阻断条件
- 找不到有效 `plugin.json` 或技能入口。
- 归档内容、manifest 引用路径不一致，或包含未签发的连接映射占位符。
- 不具备用户允许的连接器/目标工作区时仍试图访问或写入。
- 把简单角色提示词、模型自评或模拟结果误称为真实 Agent、真实测试。

## 本轮修订（2026-10-28，优先于上文历史结论）
- 本地开发优先内置工具；其他插件 Skill 不构成 RPC API，必须区分宿主可加载指令与可调用工具。Skills-only 运行要求必要能力，不强制要求 OmniTool 品牌。
- 官方打包页使用 plugin_asdk_app... 登记标识，不能据参考工程推导统一去前缀规则。绑定使用真实平台产物并在目标宿主验证；不满足只阻断绑定版。
- Skills-only 首发独立于绑定版；静态路由测试只检查样本与约束，不能证明真实 Skill 激活。在线新会话验收仍是必需门槛。
- 统一状态契约、按能力发布和失败路径门槛见 CONTRACTS.md、IMPLEMENTATION_PLAN.md 与 TEST_PLAN.md。固定 schema 后再校验清单字段，当前没有创建或校验插件包。
- 本轮已实际打开官方 [Package your plugin](https://developers.openai.com/plugins/build/plugins) 和 [Build skills](https://developers.openai.com/plugins/build/skills)；没有重查参考工程当前 Git 状态，前文 Git 结论仅属历史记录。
