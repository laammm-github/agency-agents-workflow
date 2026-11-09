# 0.2.7 工作流实现与验收

目标：按任务推进、QA返修、完整交接、版本化证据和跨会话恢复。唯一 agency-workflow，角色原文保持固定来源，不新增 Runtime/MCP。

## 实现入口
0.2.7新增`scripts/check_runner.py`有限QA适配：保存未决意图后执行一次argv，在返回前保存真实字节输出及FAIL状态；重跑仍需受控状态转换和显式supersedes。三个辅助脚本随唯一Skill分发，包内副本与根scripts字节一致；可在已授权目标内按包内布局实体化，不能把ChatGPT资源路径当本机路径。它不是新的MCP/Agent Runtime，也不是权限边界。具体操作见包内references/local-checks.md。原型125项通过，主工程复验/私人发布/新会话结果单独记录。

`scripts/team.py` 按版本分派，v1 保留旧校验及读取路径；`scripts/workflow_v2.py` 处理完整记录。公开 `references/schemas/workflow-v2.schema.json` 内含全部 $defs 与 state/checkpoint，根目录旧 schema/templates 保持 v1。新项目 CLI init 默认 v2，显式 --schema-version 1 使用旧格式。新检查点模板在 assets/templates/v2/。

`update` 通过完整 proposal 和 expected digest 写记录，不允许偷改状态、既有需求或证据；`transition` 追加状态事件；`change` 版本化需求并使依赖任务失效；`invalidate` 在输入变化时重开任务和依赖，不伪造需求变更。`report --markdown` 从 state 输出任务板，保存后仍需读回核验。`migrate` 要求完整观察资料，输出到新文件、保留完整 legacy_snapshot；缺字段返回清单，不能填造旧执行时间或历史门禁。

## 门禁
开发 test+review，集成 integration+review，研究/文档 inspection；适用 browser/security 在任务中声明。开始检查依赖交接，完成检查当前需求版本/输入哈希/验收覆盖/输出文件哈希及失败处置。初次执行后最多三次受控返修；保留原始失败和时间有效的匹配成功重跑。

`preflight --purpose implementation --write-path <file>`要求对应开发/集成任务已经EXECUTING，且每个路径属于该任务write_paths或精确deliverables；文档阶段PASS不能代替此门禁。完成证据须发生在任务本轮首次EXECUTING之后；失效重开后旧证据不能直接认证新一轮。该检查仅校验记录，不拦截宿主文件工具，也不认证角色读取或命令执行。

最终集成证据还必须属于相应已完成任务当前有效的PASS集合，错误需求版本不能仅凭候选ID和文件清单通过。CLI读入口采用合作锁及前后摘要比较，不忽略显式expected digest；v2输出附快照摘要。88项完整本地回归通过，原始三个反例与修复前脚本快照保存在build/workflow-v2。

任务证据可在版本标签变化但输入/需求不变时复用；最终集成必须覆盖固定候选 ID 和完整 SOURCE/CONFIG/BUILD 清单。RUNTIME 数据不冻结为源码哈希，通过重启/一致备份验证。生成报告和检查点避免互相哈希引用。

HOST_RETURN、INDEPENDENT_READBACK 与 MODEL_JUDGMENT 分开。角色记录 HOST_RETURN/UNVERIFIED 区分观测来源，ROLE_PHASE 不冒称独立Agent。字段、调用ID、日志文件和一致性检查不能认证真实执行，宿主验收单独记录。

## 批次与最终出口
1. 契约/迁移/报告及兼容性回归。
2. 逐任务门禁、交接、候选复用、失败与变化传播。
3. 全量测试、确定性打包、同身份私人插件更新及读回；三轮隔离新会话独立试验，无人工流程纠正；至少一轮第二会话恢复并验证变化/未知副作用阻断。
4. E2E-TEAM-A 新建交付、B 已有项目变更、C 测试环境发布故障恢复、D 中断与权限/证据阻断。TEAM/ROLE覆盖矩阵逐项提供真实证据。

试验目录位于 build/host-workflow-v2/，不能复制旧 Demo 冒充新开发。记录实际会话、工具证据、退出码、耗时、工具调用数（不可观察记 UNKNOWN）、自主返修及人工纠正次数。人工纠正的轮次保留为失败，修复后重新累计连续三轮；历史失败不得重命名成成功。所有部署/故障注入仅限本轮明确授权的隔离测试环境。

## 验证状态
当前0.2.7主工程结果以build/workflow-v27/verification-applied.json（125项通过）为准；70文件本地ZIP确定性通过，同一私人插件更新并读回71文件库存及8个修改资源。文本读取接口仅CRLF→LF规范化后内容一致，见plugin-readback-normalized-checks.json，严格字节初比的FAIL原件保留。QA适配实际保存原始字节和FAIL状态，但不能拦截未通过它调用的工具，也不认证外层连接器。DOCUMENT输入绑定及适用inspection门槛保留。trial-12整轮FAIL及过期服务记录不改写，新的13/14/15及恢复负例待执行，完整正常路径仍0/3；TEAM/ROLE及A/B/C/D尚未完成。

0.2.4来自宿主试验发现的流程缺口：恢复不能只按命令行目录过滤判断服务不存在；取消状态和并发写者不明时阻断写入/启动；原子保存失败不能复制覆盖绕过；模型摘要与原始工具结果分开；最终任务板从最终修订投影且不注册为演进中的不可变输入。角色原文、唯一Skill和工具执行边界保持不变。该候选88项全量回归及确定性包检查通过，同身份私人更新并读回一致；新的宿主正常路径仍须实测。


0.2.5增加独立的state.evidence_policy_version=2（schema_version仍为2）。新检查点要求完整tool_capture返回封装及终态；同会话ROLE_PHASE结论必须为MODEL_JUDGMENT，引用同任务同输入的实际源码读取证据。旧v1和无策略标记的v2保持旧读取路径；策略变更只通过显式迁移到新文件，完整保留原件和历史，并重开需要重采证据的任务。普通update禁止策略升降级。任务完成、依赖启动和实现预检核对当前证据文件。结构门禁无法认证工具返回来源，execution_authentication保持UNKNOWN。
