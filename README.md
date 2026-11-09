# Agency Agents × ChatGPT Workflow Plugin

当前独立发布候选 **0.2.10**，采用完整 **schema_version=2** 工作记录。完整团队宿主验收尚未完成；本地测试、插件更新和宿主验收分别报告。已发布线上版本需另行核验，本地候选并非自动发布。

唯一 agency-workflow Skill 按需加载18个固定上游角色，指导需求、计划、开发、QA返修、交接、发布和恢复。ChatGPT/Codex使用真实已授权工具执行；角色不是独立进程，插件不是本机执行服务。

## 当前实现
- v1兼容路径与显式迁移；v2完整schema/模板、检查点事实源和任务报告投影。
- 任务依赖、模式验收、阶段交接、失败重跑、历史保护与变化传播。
- 需求版本/输入哈希绑定证据，固定候选的最终集成，完整基线恢复。
- 包内有限QA辅助脚本：执行前保存意图，返回前保存真实输出与FAIL状态；超时/冲突保留未决操作，不自动重放。独立宿主认证仍需另行核对。
- 0.2.10修复：后续真实PASS显式supersedes失败证据时，仅移除任务的历史失败当前引用，不删除原始FAIL证据及文件。

## 文档
[工程规则](AGENTS.md)、[需求](docs/PRD.md)、[架构](docs/ARCHITECTURE.md)、[契约](docs/CONTRACTS.md)、[实施与验收](docs/WORKFLOW_V2_IMPLEMENTATION.md)、[开发命令](docs/DEVELOPMENT.md)、[任务板](docs/TASKS.md)、[实际状态](docs/STATUS.md)。

最终出口为 [完整团队功能](docs/TEAM_FUNCTIONS.md)，包含TEAM-01–14、ROLE-01–18及四条综合E2E，不以单个Demo替代。历史0.1.x验证和Demo保留在docs/history与build，不能据此推定0.2.0通过。

## 历史证据归档与检索

历史 trial、原始失败、观察器和原子写入提案均原地保留，不因生成索引或清理策略而移动、覆盖或删除。开发侧只读索引工具见 `scripts/evidence_archive.py`；归档入口为 `build/evidence-archive-index/README.md`，包含按轮次导航、证据哈希复核和零删除清理提案。规则与恢复边界见 [证据归档策略](docs/EVIDENCE_ARCHIVE_POLICY.md)。索引不替代 `runs.json` 或原始宿主回执。

私人插件：https://chatgpt.com/plugins/plugins_6ae1de0d0fb481918688acd3e26d7051 。本地候选版本不等于该页面已更新；以本轮工具读回结果为准。源码角色来源与许可见docs/SOURCE_MAPPING.md及包内ATTRIBUTION。
