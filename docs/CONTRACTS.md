# 工作流数据与行为契约

## 当前版本
新项目采用schema_version=2，权威文件为 skills/agency-workflow/references/schemas/workflow-v2.schema.json；全部记录定义在$defs，state内嵌完整需求/任务/产物/证据/缺陷/变更/发布/事件/交接记录。根目录原schemas/templates保留v1，原件只通过显式迁移产生新v2文件，缺资料不能补造。

## 状态与证据
任务状态仍为PLANNED/PREFLIGHT/EXECUTING/VERIFYING/COMPLETED及BLOCKED/FAILED/UNKNOWN/NEEDS_REVIEW。就绪verdict、实际部署和证据来源分开。checkpoint.state为事实源，生成报告不能独立更改状态。

模式及必需检查：DEVELOPMENT=test+review，INTEGRATION=integration+review，DOCUMENTATION/RESEARCH=inspection；适用browser/security预先声明。依赖任务须完成且交接有效，必需业务问题未解决不执行。QA失败阻断，重跑须同检查/范围且严格晚于失败，原始证据不修改；初次执行后最多三次修复。

任务证据含requirement_versions、input_hashes、check、provenance、review_kind与output_sha256，另含完整项目/时间/工具/结果/退出码/引用。HOST_RETURN是宿主观测，INDEPENDENT_READBACK是独立核对，MODEL_JUDGMENT不能单独通过验收；它们均不提供密码学执行认证。

候选由当前SOURCE/CONFIG/BUILD产物清单确定；未变任务可复用版本/输入匹配证据，最终集成须绑定固定候选ID和完整清单。RUNTIME数据需一致备份或真实重启持久化测试，不能用刷新替代。报告、输出和检查点不进入自身候选哈希。

## 保存、交接与恢复
交接包含生产/接收任务与角色、需求版本、产物/证据、风险/问题/下一前置条件，resolved必须源于实际核实。事件记录真实阶段转换，不在项目完成后重建成功时间线。

写入比较内容哈希和revision，合作锁及原子保存避免已知覆盖；不提供OS权限隔离。检查点保留完整基线、里程碑、最后动作及下一前置条件，恢复核对所有保存文件和未知副作用，再重核真实目标/授权。发现外部修改先调查，不能替换哈希绕过。检查点自身不纳入哈希；历史产物通过supersedes保留。

CLI读取使用同一合作锁，校验传入的expected digest，并在输出前再次比较文件；检测到写者或快照变化时拒绝输出旧结论。v2 JSON结果附checkpoint_digest，Markdown附快照摘要。迁移写新文件时锁定并重查原件，失败保留原件。锁是检查点旁的.lock元数据文件，CLI可能创建它；不允许该写入的只读任务应使用文件读取并明确没有运行确定性CLI检查。

## 工具与权限
READ_ONLY不创建状态或运行写文件测试；CONTROLLED_WRITE限已授权目录；BROWSER_QA核对站点和副作用。内置能力优先，外部Skill不是RPC；缺能力阻断依赖，不猜App ID、不继承旧授权扩大范围。同会话审查标ROLE_PHASE，发布/安装/外发/生产操作按具体授权。

完整入口与失败语义见 [实现说明](WORKFLOW_V2_IMPLEMENTATION.md) 与包内 references/workflow-v2.md。v1历史完整说明及0.1.x约束保留在 [历史契约](history/CONTRACTS-pre-0.2.md)，读取v1仍走原校验路径。


0.2.5增加独立的state.evidence_policy_version=2（schema_version仍为2）。新检查点要求完整tool_capture返回封装及终态；同会话ROLE_PHASE结论必须为MODEL_JUDGMENT，引用同任务同输入的实际源码读取证据。旧v1和无策略标记的v2保持旧读取路径；策略变更只通过显式迁移到新文件，完整保留原件和历史，并重开需要重采证据的任务。普通update禁止策略升降级。任务完成、依赖启动和实现预检核对当前证据文件。结构门禁无法认证工具返回来源，execution_authentication保持UNKNOWN。

0.2.6修复证据策略2的DOCUMENT绑定遗漏：文档/研究完成时，DOCUMENT产物必须纳入task.input_hashes及实际证据的输入版本；仅需适用inspection，不强制代码测试。无策略/策略1保留旧路径；策略2此前错误接受的缺字段记录不因此有效，不改写历史文件。首次QA失败必须在返修和交接前保存原始返回、FAIL记录和合法失败状态，后续PASS显式supersedes。

0.2.7保持schema_version=2、证据策略2及旧记录读取路径。新增一次性本地QA辅助脚本，保存argv/cwd意图至既有pending_operations，经同一锁/摘要比较执行一次，保留完整stdout/stderr字节、退出码及输入哈希，追加证据后再返回；非零结果转FAILED。超时或结果不确定时未决意图阻断恢复，不自动重放。tool=python.subprocess.run指实际本地Python API，不能冒称外层MCP返回；外层实际调用和独立复验另存，execution_authentication仍UNKNOWN。已有任务完成/审查/交接门槛不因此省略。未使用适配脚本的原始工具不受拦截，漏记实际失败仍判流程失败。

浏览器观察可直接保存任一实际授权提供方的完整原始content返回，使用其实际工具名，不要求伪装成OmniTool，也不凭空补退出码。非源码命令应省略observed_paths，存在时必须非空且对应真实源码内容读取。服务交付须核对启动器时限并记录期限，启动命令返回后再确认实例；过期URL不能报仍可访问。
