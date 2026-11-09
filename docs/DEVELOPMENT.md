# 本地开发与验收

当前候选0.2.7，契约v2；下方0.1.x章节是历史行为。当前公开规则见CONTRACTS.md与WORKFLOW_V2_IMPLEMENTATION.md。

## v2操作
- 有脚本能力时，有限代码QA通过`python -B scripts/check_runner.py <checkpoint> --expected-digest <sha> --task-id <id> --evidence-id <new-id> --output evidence/<new>.json --check test --argv-file <project-argv.json>`执行。先进入EXECUTING并保存真实输入；非零结果返回前已有FAIL及失败状态，复测显式`--supersedes <old-id>`。超时/冲突保留未决意图，禁止自动重放。包内scripts副本用于授权目标实体化，须保持与根源码一致，具体见包内references/local-checks.md。
- `python -B scripts/team.py init <checkpoint> --workspace <project> --project-id <id> --authorization-ref <observed-ref>`：授权目录已存在时初始化，默认v2。
- `validate` / `report --markdown` / `preflight --task-id <id>` / `next`：完整记录检查、状态投影、首次源码写入前门槛和依赖任务列表；不是权限授权或文件写入拦截。
- `update --proposal <document> --expected-digest <old-sha>`：保存完整提案；追加证据/产物/交接，不能重写历史或改变状态。
- `transition --task-id <id> --status <status> --expected-digest <old-sha>`：记录真实阶段转换；开发test+review，集成integration+review，研究/文档inspection。
- `change --requirement-id <id> --description <content> --expected-digest <old-sha>` / `invalidate --task-id <id> --description <reason> --expected-digest <old-sha>`：需求版本变化与非需求输入变化分别处理，失效影响传播到依赖任务和最终集成。
- `migrate <old> --proposal <complete-v2-document> --output <new>`：保留原件和legacy_snapshot，缺少资料阻断，不编造旧时间/证据。
- `ready --candidate <id>` / `resume --workspace <project>`：固定候选、最终集成和完整基线/未知副作用检查；就绪不等于部署，恢复仍需核实实际授权。

以上除init外均在操作名后传入检查点路径；记录完整schema见包内workflow-v2.schema.json。完整说明含可选辅助脚本条件与宿主无脚本时的处理，见包内references/workflow-v2.md。

新项目PATH_NOT_FOUND是预期起点，优先发现结构化目录创建能力后创建授权目录，shell必须使用已有cwd。不要因本地可修复命令/测试错误提前交付。

`python -B -m unittest discover -s tests -v` 执行v1兼容/v2/索引/schema/包/API集成回归。当前125项结果见build/workflow-v27/verification-applied.json及tests-applied.log；build/workflow-v2保留早期版本证据，历史失败和宿主试验保存在build/host-workflow-v2，不重写失败成成功。

## 历史0.1.x说明


Python 3.13，开发依赖见 requirements-dev.txt；没有新增MCP服务。

- `python -m unittest discover -s tests -v`：索引、schema、状态门禁、包和真实HTTP/SQLite教学集成。
- `python scripts/package.py`：官方固定schema校验、来源哈希、包扫描和确定性ZIP。
- `python scripts/browser_smoke.py`：需要本机Edge与Playwright；运行本地隔离教学站点，验证成功和失败UI并保存build/browser-smoke.png。
- `python scripts/index_roles.py build/upstream.zip --output build/full-agent-catalog.json`：按固定SHA源码归档扫描divisions，校验Runbook文件stem引用与重复slug。
- `python scripts/team.py --help`：校验、初始化、下一任务、报告、变更传播、状态转换、就绪与恢复。状态变更需要expected digest；初始化需要明确工作区/项目和授权引用，不能代替真实用户授权。

工作流入口及最少角色见skills/agency-workflow/references/routes.json。宿主使用暴露工具填写模板，不把REQUIRED占位符当作真实数据。开发侧team.py是紧凑任务板校验助手，各阶段完整记录按包内schema另存；它不执行代码修改、部署或远程命令。save的锁只协调合作写入者，不提供OS权限隔离。

本地HTTP/API故障切换与浏览器检查不等于实际CI/CD或生产部署；新会话恢复测试只证明文件与授权重验逻辑，不等于ChatGPT实际跨会话验收。完整E2E-TEAM-A/B/C/D仍需要目标ChatGPT安装副本执行和真实证据。

参考插件技能：[create-plugin](C:/Users/laamm/.codex/plugins/cache/openai-curated-remote/plugin-creator/0.1.28/skills/create-plugin/SKILL.md)。仅本地包内容允许被上传，开发日志和用户项目数据不在ZIP中。

## 0.1.1 审查修复后的契约
- requirements 中每项必须有 acceptance_ids；发布前必须覆盖全部需求。证据必须携带 task_id、acceptance_ids 和 candidate，任务不得引用别人的结果。当前候选的失败只有被相同任务/验收的成功重跑通过 supersedes 明确替代才解除阻断。
- ready 会读取实际交付文件并核对哈希，不是仅校验JSON字段。resume 要求所有登记产物出现在哈希表且与检查点记录及磁盘一致。
- 公开 checkpoint.json 现在包含完整 state；用 scripts.team.checkpoint(state, authorization_ref) 导出，load_state(document) 导入。CLI validate/resume/change/transition 同时支持该格式。旧版仅ID索引没有足够的恢复资料，必须取得原始记录后显式迁移，不能猜测补齐。
- writer_lock 使用OS锁；进程退出或崩溃会释放，持久.lock文件不是锁所有权；不应因为看到文件就删除它。每次写入使用唯一临时文件，失败时保留原状态并清理本次临时文件；旧.tmp不阻塞保存。
- package-files.json 是人工维护的精确发布允许清单；新增资源需经审查加入，任何额外文件/缺失资源都拒绝打包。全部校验为显式异常，-O仍生效。
- requirements-dev.txt 已声明Playwright。安装依赖需授权；Windows浏览器测试使用已安装Edge，不暗中安装浏览器。

## 0.1.2 恢复与产物历史
公开检查点使用 `resume(document, workspace)`，CLI 为 `python scripts/team.py resume checkpoint.json --workspace <项目目录>`，默认检查保存的完整 expected_hashes。可选 `--hashes` 只能补充核验，不能删除或替换保存的基线。不要先 load_state 再传给 resume，否则公开检查点的额外信息不在传入对象中；裸 state 兼容接口仍要求显式基线。

状态推进导出使用 `checkpoint(changed, authorization_ref, previous=document)`，保留里程碑、最后确认动作和下一前置条件。普通 CLI change/transition 已采用该路径。合法内容变化后的重新建基线必须由调用方明确完成；冲突的产物哈希不会自动覆盖。

当前产物通过合法 supersedes 链确定，历史哈希不与更新后的同一文件比较；循环、分叉、缺引用或多个当前版本均阻断。失败重跑须新增记录，使用带时区且严格晚于失败的时间，并保留原证据。缺少可靠时间时调查原始结果，不能补写虚假时间。

验证：`python -B -m unittest discover -s tests -v`，56 项通过；包含 11 项本轮新增回归及 CLI 子进程验证。日志与退出码见 `build/review2-verification.json`、`build/review2-tests.log`。本轮未重复浏览器 UI 或完整 ChatGPT 团队 E2E 验收。
