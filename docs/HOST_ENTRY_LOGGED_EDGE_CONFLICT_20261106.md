# 2026-11-06 已登录 Edge 宿主入口与未归属输入冲突

性质：本次续工只读观察与浏览器入口预检归档；不是正式 ChatGPT 宿主试验。

## 实际操作
1. 公司电脑工具 `list_windows` 实际发现已登录的 Edge 窗口 PID28956、windowId1971612，原标签地址在 Open Source Project Research 聊天内；另有 Playwright 独立 about:blank 会话，未修改无关标签页。
2. `company_computer_use/get_ui_tree` 证实原 Edge 地址和登录的 ChatGPT 站点。公司电脑 `click_element` 试图新建标签返回内部工具错误，未见成功。
3. `OmniTool/native.desktop/desktop_key` 在窗口1971612发送 Ctrl+T 成功；重新读回 UI tree 确认新增“新建标签页”，原项目聊天保留。
4. 在新增标签中使用 OmniTool 桌面键盘定位地址栏、输入 `https://chatgpt.com/`、Enter 成功。页面自动出现 `https://chatgpt.com/plugins/plugin_asdk_app_6aae8fcbdf5881918095b95fb15d8fec`，提示“无法加载插件”，未作为插件版本验证。
5. 用 OmniTool `desktop_find` 找到页面“新聊天”，`desktop_click_element` 成功；独立标签显示普通 ChatGPT 新聊天页面和已登录账户。
6. 重新获得 UI tree 时发现“询问 ChatGPT”输入框里已有未发送文本：`Read only host preflight in this new ChatGPT session. Use a connected plugin metadata tool to read the version and release ID of plugin plugins_6ae1de0d0fb481918688acd3e26d7051. Do not create files or execute development. If you cannot access metadata in this session say BLOCKED. Do not infer from the prompt or skill text.`。
7. **上述输入文本不是当前会话通过任何输入工具写入的**，其来源未确证；可能存在独立会话操作或原先草稿。遵守不明写者/状态变化门禁：未点击发送、未清空输入、未创建 trial 目录、未修改历史 checkpoint 或 runs.json。

## 结果
- 登录 Edge 的真实浏览器访问路径已可用，隔离浏览器 Cloudflare403 不再是当前唯一入口。
- 被测独立 ChatGPT 会话内真实插件版本/release 尚未通过工具读取；正式宿主试验 NOT_STARTED，连续3轮仍0/3。
- 待确认该新聊天草稿的归属，并确保测试期间只有一名宿主写者；之后先执行只读版本预检。
