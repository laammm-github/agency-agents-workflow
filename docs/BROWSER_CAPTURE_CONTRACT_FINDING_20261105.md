# 0.2.10 浏览器原始返回结构与 v2 捕获门禁的可重复复现

2026-11-05 使用 **实际 0.2.10 项目脚本** `scripts/workflow_v2.py::tool_capture` 直接校验昨日来自真实 browser_snapshot 与 OmniTool.file_read 的原始捕获文件；本次只读复现，无主工程修改。

复现路径：`build/browser-capture-inquiry-20261105/repro.py`，真实命令 `python -B repro.py` exit0，完整逐例 SHA256 和结果见 `build/browser-capture-inquiry-20261105/RESULT.json`。

- 对照组 `EV-RUNTIME-SOURCE-READ`：inspection，原始捕获具有工具返回结构，校验 ACCEPTED。
- `EV-RUNTIME-BROWSER-1`：真实浏览器空标题拒绝的页面 snapshot，本连接器返回仅由 `text` 承载，当前捕获校验 REJECTED：`Capture lacks an observable tool result`。
- `EV-RUNTIME-BROWSER-3`：真实浏览器非法状态拒绝的页面 snapshot，校验同样 REJECTED。
- 三个案例经校验程序实际执行，不靠文字推断。源检查点 `build/host-0210-live-qa-20261104/checkpoint.json` SHA256 `8de4679737e3fa55deb0e39a609a75c43710956ed53944a485534a2a3aa5c708` 未修改。

**诊断：** 实际浏览器 UI 操作与快照能作为待人工核实的原始材料，但当前连接器纯文本响应没有 `success`/`state`/`content` 等机器可验证终态，v2 tool_capture 正确地拒绝把这种响应直接升级为通过证据。不能为了增加正式 TEAM/ROLE/E2E PASS 将任何含网页文本的对象包装成虚构的 MCP 成功响应。

**后续研发需要的规范化方案：** 让受信任的浏览器 connector/tool adapter 提供真实的结构化调用成功/失败状态及来源，而不是让使用者自行写 `success:true`；对真实成功、浏览器操作拒绝、错误页、断线与虚构快照分别加自动化回归。独立宿主会话 3/3 仍为 0/3；此调查只是隔离组件复现，不是修复或远端认证。

项目主工程仍保持 0.2.10，先前 130/130 PASS 的验收基线未改变。