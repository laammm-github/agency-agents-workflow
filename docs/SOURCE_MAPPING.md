# Agency Agents 上游源码映射

> 上游仓库：https://github.com/msitarzewski/agency-agents
> 早期设计依据为 2026-10-28 的 main；正式打包已固定 commit `b37b5bb33b78f2c1d6567d98e25ca818e3259219`，记录在包内 upstream-lock.json。当前工程没有 Git；源码来源通过固定提交 ZIP 及逐文件 SHA256 核对，不声称执行了不存在的本地 Git 操作。

| 上游路径 | 已核对用途 | 本项目的使用方式 |
|---|---|---|
| divisions.json | 部门目录的权威清单 | 列出可扫描角色目录 |
| engineering/engineering-frontend-developer.md | 前端 Developer 的 Markdown 专家定义 | 按需参考，不直接执行 |
| engineering/engineering-code-reviewer.md | 代码审查角色 | 只读 QA 阶段指南 |
| engineering/engineering-codebase-onboarding-engineer.md | 陌生代码仓库理解角色 | 只读分析阶段参考，实施前复核当前路径 |
| specialized/agents-orchestrator.md | Dev-QA Loop、阶段交接、最多 3 次重试等规范 | Orchestrator Skill 来源 |
| specialized/specialized-mcp-builder.md | MCP 工具服务开发最佳实践 | 仅在需要新服务器时参考 |
| strategy/runbooks.json | NEXUS 可机器读取的 Runbook roster | 未来按场景组队 |
| strategy/runbooks/ | Runbook 说明文档（非 Agent） | P1 后选用 |
| scripts/lib.sh | get_field、slugify、agent_slug、is_agent_file | 数据索引需要匹配行为 |
| scripts/convert.sh | convert_codex 把 Markdown 转为 TOML | 研究角色格式映射，不复用为 ChatGPT 插件生成器 |
| integrations/codex/README.md | Codex 自定义 Agent 的安装与使用说明 | 对比宿主差异 |
| integrations/mcp-memory/README.md | 连接外部 Memory MCP 的指导 | 不等于内置持久化 Memory Server |

## 身份一致性规则
- corpus_id：文件 stem，例 engineering-frontend-developer；Runbook roster 引用此类 ID。
- display_name：Frontmatter name，例 Frontend Developer。
- tool_slug：从 name 做 slugify，例 frontend-developer；Codex 转换时用。
- 索引必须保留三者并显式校验重名/缺失，不能随意将 stem 当 slug。
- Markdown 的描述能指导 ChatGPT，但不能证明宿主拥有具体派发或隔离能力。

## 源版本管理
1. 构建使用固定提交来源并写入 skills/agency-workflow/references/upstream-lock.json（已实现）；若使用 Git 克隆则记录 git rev-parse HEAD，使用提交 ZIP 则核对固定提交目录及文件哈希，不混称两种获取方式。
2. 生成角色索引时记录 source path + SHA；运行源文件存在性和 frontmatter 检查。
3. 上游更新时先比较角色 ID、目录、Runbook、职责变化；复核许可与意外指令变更。
4. 自动生成内容不得编辑上游仓库；本地扩展记录差异与授权来源。

## 插件引用文件放置要求
- 源码阶段保留固定 SHA、双标识及角色原文来源。
- 发布时将精选角色与 `agent-catalog.json`、`upstream-lock.json` 一起放到 `skills/agency-workflow/references/`，确保 ZIP 打包后 Skill 引用仍然有效。
- 不从本地未包含在 ZIP 的 `references/` 或绝对路径读取运行时依赖；用户机器和 ChatGPT Hosted 环境的文件系统不能混为一谈。

## 全流程角色来源核对（本轮新增）
设计与打包依据 commit `b37b5bb33b78f2c1d6567d98e25ca818e3259219`；下表名称来自真实 frontmatter，未改写上游文件。codex_slug 已按上游名称规则生成到 agent-catalog.json，不由中文职责推断。

| 上游路径 / corpus_id 对应文件 | Frontmatter name |
|---|---|
| `specialized/agents-orchestrator.md` | Agents Orchestrator |
| `engineering/engineering-codebase-onboarding-engineer.md` | Codebase Onboarding Engineer |
| `product/product-manager.md` | Product Manager |
| `project-management/project-manager-senior.md` | Senior Project Manager |
| `design/design-ux-researcher.md` | UX Researcher |
| `design/design-ui-designer.md` | UI Designer |
| `engineering/engineering-software-architect.md` | Software Architect |
| `engineering/engineering-backend-architect.md` | Backend Architect |
| `engineering/engineering-frontend-developer.md` | Frontend Developer |
| `engineering/engineering-database-optimizer.md` | Database Optimizer |
| `testing/testing-test-automation-engineer.md` | Test Automation Engineer |
| `testing/testing-api-tester.md` | API Tester |
| `testing/testing-reality-checker.md` | Reality Checker |
| `engineering/engineering-code-reviewer.md` | Code Reviewer |
| `security/security-appsec-engineer.md` | Application Security Engineer |
| `engineering/engineering-devops-automator.md` | DevOps Automator |
| `engineering/engineering-sre.md` | SRE (Site Reliability Engineer) |
| `engineering/engineering-technical-writer.md` | Technical Writer |

正式角色索引、来源路径、固定提交与 SHA256 见包内 agent-catalog.json / upstream-lock.json。本轮对 build/upstream.zip 中固定提交的 18 个原文、包内副本和索引重新比较全部一致，证据见 build/workflow-v2/role-source-recheck.json；完整宿主角色验收仍以 ACCEPTANCE_MATRIX.md 为准，许可分发要求见 PLUGIN_STANDARD_AUDIT.md。
