# Desktop Commander 进程受控重启尝试（2026-11-04）

## 用户授权
用户在建议“正常重启 Desktop Commander、核对文件锁、再安全同步 0.2.10”后明确回复“按你的建议处理”。本次仅尝试非强制停止；未授权直接强杀整个含活跃服务的进程树。

## 前置实测
- OmniTool/psutil 确认 PID=20772，name=node.exe，二进制 C:\\Program Files\\nodejs\\node.exe，cmdline 指向 ChatGPTDesktopCommanderMCP/desktop-commander/dist/index.js，创建于 2026-10-29 09:36:28（机器本地时间）。
- parent 关联 17 个后代进程（含 trial-06、trial-07、trial-23 的历史服务进程与 Python 交互进程），无已知网络 TCP 连接来自 parent 本身。
- parent open_files 明确包含根 scripts/team.py、scripts/workflow_v2.py、scripts/check_runner.py、docs/STATUS.md、docs/TASKS.md 和历史 trial/runs.json。
- 保存重启前身份及关键文件散列到 build/root-sync-stage-0210-20261104/desktop_commander_before_restart.json。关键文件：root team.py b4a929afb9bf8cface3e37a41f4021f65b5005d973c6794a248c0cad0bf948c7；workflow_v2.py eb19e3919a1f22d5b7d5d0b3b005528279c4e2ab594a213d1ca75548afb237f8；check_runner.py a9c6804dc562cdb7a03a1a4545a4890c57440c46634d78e408aa8ad80cee1f73。trial-27 revision14/原 SHA 不变。

## 实际停止尝试
1. 通过 OmniTool 执行 Windows `taskkill /PID 20772` （**无 /F、无 /T**），真实 exit=1，Windows 返回“只能强制终止该进程（/F）”。未终止。
2. 通过 company_computer_use 的 `process_kill(mode=kill,pid=20772,force=false)` 尝试温和停止，工具内部失败，没有成功确认。
3. 再用 OmniTool/psutil 实测 PID20772 仍存在，且 cmdline 仍指向 Desktop Commander。没有使用 `/F`、`/T` 或 `Stop-Process -Force`，未自行杀死服务子进程，也未手工重建无法与原 ChatGPT MCP 标准输入输出连接的独立 Node 进程。

## 判定
- **正常重启未完成**，被当前 Node 进程“仅强制可终止”的操作系统拒绝明确阻断。
- **文件锁不能宣称已释放**；根目录继续 0.2.8，不应用 14 项更新，不执行未知部分同步。
- 已存在完全隔离的 0.2.10 shadow worktree，先前 100/100 文件 hash 与 130/130 回归通过，独立可用，不影响历史根工程。
- 若要进一步执行，选择一：由 Desktop Commander 的宿主/连接管理器正常断开并重连（可能关闭其进程）；选择二：用户另外明确批准强制结束此共享 PID 及其可能中断的历史子进程后，才能执行有风险的强制止进程，并先做好相关服务状态处理。

本文件为同会话执行审计，非已成功重启凭证。
