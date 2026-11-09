# 2026-11-06 已登录 Edge 宿主入口复核

## 验证事实
- 新建 OmniTool 隔离 Edge 进入 ChatGPT 遇到 Cloudflare HTTP 403，此问题只适用于隔离浏览器配置。
- 用户指出当前浏览器已登录。通过 company_computer_use_mcp 的 Windows 窗口列表和 UI tree，确认普通 Edge 个人用户配置中有 ChatGPT 已登录页面，显示项目列表、插件入口、新聊天和消息输入框，无登录/注册门禁。
- 用 OmniTool 授权系统命令 `Start-Process ... msedge.exe --new-window https://chatgpt.com/` 打开普通 Edge 同一配置下的独立窗口，实际 HWND 3806496。UI tree 读取到 ChatGPT 网页、Open Source Project Research 项目和输入框。
- Desktop UI 控制工具 `activate_window`、`click_element`、`set_value`、`openai_computer` 连续返回工具内部错误；Shell Windows SendKeys 及 UIAutomation ValuePattern 尝试均未成功在新窗口输入框保留文本，实际 UI tree 独立读取确认输入仍为空。
- Desktop doctor 通过 9 项诊断，但其检查时前台焦点位于 Cursor.exe。为避免干扰用户其他窗口，停止前台抢占/模拟输入。
- **没有提交 ChatGPT 消息、没有执行被测新会话中的 Plugin Creator 版本核验，没有创建新的正式宿主试验目录**。
- 最新独立回读本地 checkpoint revision 433，SHA256 `7a228496dc9cc49ef7936fb78dc0dfe80b457fe3a6f083550aad267dbdd68919`，所有38项本地 COMPLETED，pending_operations=[]，候选 `local-freeze-20261106-r1`。

## 门禁
- 已登录宿主可见性：CONFIRMED。
- 在新 ChatGPT 被测会话里实际读取插件版本/Release：NOT_RUN（桌面自动输入失败）。
- 正式独立宿主试验：NOT_STARTED；不能凭所有者端插件版本替代宿主加载认证。
- 后续可以通过用户在该已登录独立窗口手动发送只读版本预检请求、或者恢复可靠可控的 GUI automation，再继续严格宿主验收。不得将本次失败写成已认证。

这是隔离的审计说明，不修改冻结候选或历史 trial。
