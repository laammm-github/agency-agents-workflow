# Agency Agents Workflow — 2026-11-06 续工独立核查（追加记录）

性质：当前会话实际只读核查与宿主入口预检，非正式宿主试验、非新 checkpoint。历史 trial 不修改。

## 基线实际结果
- OmniTool `team.py validate build/team-role-e2e-sequential-20261105/checkpoint.json` 返回 exit0，valid=true，checkpoint_digest=`7a228496dc9cc49ef7936fb78dc0dfe80b457fe3a6f083550aad267dbdd68919`，注明 execution origin unauthenticated。
- OmniTool file_read 读回 `build/team-role-e2e-sequential-20261105/TASKS.md`，内容 Revision:433，file revision SHA256 `d6b6639f777bc0de825fbd7d8bd255744680d18483847e989601da44556dd8f9`。
- Plugin Creator 所有者元数据确认 USER/PRIVATE `plugins_6ae1de0d0fb481918688acd3e26d7051` version=0.2.10，release=`pluginrel_6ae857ea7ce4819193bcd1a74d0f83b5`；不能代替被测会话自身版本门禁。
- 不完整参数的 `team.py resume <checkpoint>` 返回 exit1 `Resume needs workspace and expected hashes`，没有恢复写入。
- 本轮单独 `team.py ready ... --candidate local-freeze-20261106-r1` 运行30秒后 COMMAND_TIMEOUT，command ID `db19ef51-bc9c-48be-9e19-231a96d70087`；command_status=timed_out、command_logs无 stdout/stderr。**不记本轮 ready PASS**；先前 `LOCAL_CANDIDATE_READY_20261106.md` 的历史 ready PASS 保留。

## 实际独立宿主入口
- OmniTool browser_open 成功创建 owned/isolated Edge `f704eca4-ef6e-4706-baf4-37a91937b420`。
- browser_navigate 到 `https://chatgpt.com/` 工具成功但页面未进入会话；browser_snapshot title=`请稍候…`，interactive=[]。
- native.browser/browser_network 真实可见主 document HTTP403、Cloudflare challenge 和 Turnstile 资源；正式被测插件版本门禁 BLOCKED，未提交研发指令。
- browser_close 对自己创建的隔离 session 返回 completed，未处理其他会话。

## 历史边界
- OmniTool 只读重新读回 `build/host-workflow-v2/trial-27/checkpoint.json`，文件 SHA256 `e34646fc9acdc854293d987630fb50e19a3ec6dca3b3155547252472f9679295`，revision14；远端写者是否停止仍 UNKNOWN。未变更原 checkpoint/runs。
- 正式连续新宿主验收仍为 0/3；TEAM/ROLE/E2E 本地完成不等于正式宿主认证。
- 不绕过 Cloudflare；可用已登录且经确认归属的正常宿主会话才能启动下一轮。snapshot-only 捕获适配仍待可信连接器源头结构化终态，不伪造 success。

## 下一步
1. 获取可操作的已认证 ChatGPT 新宿主和实际插件版本/release 读回；
2. 若有可信结构化 browser-tool 结果，隔离测试 capture 合同；否则保留阻断；
3. 按 HOST_ACCEPTANCE_PROTOCOL 顺序执行独立宿主验收；
4. 继续只读核查 trial-27 远端终态，不以本地 revision 静止宣告停止。
