# Agency Agents Workflow — Desktop Commander 重启后的主工程 0.2.10 同步（2026-11-04）

## 用户操作与实际观察
用户表示已经重启 Desktop Commander。本轮并未由助手成功重启该程序；助手实际只读确认原 PID20772 已退出，新 Desktop Commander PID50900 已启动，且新进程初检对 agency-agents-mcp 无打开文件句柄，原根三个脚本不再被旧进程持有。重要文件内容仍与同步前基线哈希一致。

## 原子同步
- OmniTool 在独立 build/root-sync-stage-0210-20261104/ 下先测试临时文件 os.replace，exit0，内容读回一致。
- 复核 root/candidate 14 项差异，其中 13 个旧文件、一个新增测试文件。源候选位于 build/release-030-package-20261102，为先前经线上文件和本地回归核验的 0.2.10 版本。
- 运行 apply_guarded_root_sync.py prepare：exit0、13 个旧文件全部备份至 root0210-backup-20261104，固定源和根当前哈希校验、写出 ROOT_SYNC_PREPARED.json。
- 运行 apply_guarded_root_sync.py apply：exit0，14/14 文件通过同目录临时文件 + os.replace 原子写入，错误为 0，落盘 ROOT_SYNC_APPLIED.json。失败防护会仅对无并发修改的已完成项进行条件性回滚；本轮未触发回滚。
- 与上一阶段只涵盖包资源的 11 文件 overlay 不同，本轮额外包括 README.md、tests/test_teaching_integration.py、tests/test_task_board_readiness.py，使正式根开发工作树达到 0.2.10。

## 实测回归
- 在正式主工程根目录启动有唯一 intent 与输出文件的有限 Python unittest 进程。意图路径：build/root-sync-stage-0210-20261104/ROOT_0210_POSTSYNC_INTENT.json。
- 完整回归 **130/130 PASS，exit0**。实际用时 55.739 秒；原始 stdout/stderr、退出码和时间戳位于 ROOT_0210_POSTSYNC_TEST.json；SHA256 88b4a00dae383df9e4cff729f92a777df4b2e55ef3bf4954f20880970eba74b5。本次本地命令返回不代替专用 schema-v2 check_runner 流程内证据，也不能证明宿主端到端完成。
- 最终独立 OmniTool 核查：root plugin.json 版本 **0.2.10**；共计 **100/100** 候选源码/测试/打包相关文件 SHA256 与 release-030-package-20261102 一致，0 项不匹配。

## 历史状态与严格限制
- trial-27/checkpoint.json 及 runs.json 的 SHA256 与用户重启前保存的基线相同；未修改/归档历史 trial。trial-27 宿主终态仍没有经过权威认证。
- 旧 Desktop Commander PID20772 已消失，新 PID50900 仍运行，不能把这当成 trial-27 远端执行已经结束的证明。
- 主工程本地更新成功，已发布私人插件此前确认版本仍是 0.2.10；未在本轮重复发布插件。
- **本次仅完成主工程版本同步与本地 130/130 回归。** 严格自主 0/3、TEAM 0/14、ROLE 0/18、E2E 0/4 仍需独立宿主验收。不可将本地测试或静态文件一致视为全部交付。

## 后续顺序
取得 trial-27 可信远端终态/未知副作用核对；在新认证宿主中独立核验 0.2.10 的精确 Release ID、单写者及完整 E2E 观测；逐项完成正式 TEAM/ROLE/E2E 证据矩阵；最后再作正式交付门禁。
