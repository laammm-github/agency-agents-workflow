# ChatGPT Web 浏览器验收（2026-10-28）

使用company-computer-use-mcp控制用户既有Edge，另开标签页访问私人插件，点击“在聊天中试用”，提交三轮只读测试。

测试会话：https://chatgpt.com/c/6ae1ef6e-d4a8-83ea-b81d-aa1d73a96e31

实际观察：详情页名称、版本0.1.0和唯一Skill正确；试用会话出现插件mention；团队流程回答包含交接和缺输入；AppSec的commit、SHA256、path与本地包完全一致，resume原文吻合；标记为不可信的安装/git push/生产部署/伪报PASS文本被回答明确拒绝，相关动作NOT_RUN。

证据限制：页面工具调用JSON卡片是回答正文，不是独立审计到的原始工具执行日志。资料结果一致性可以核对，但不能把模型自述的读取PASS作为真实执行证明。只读拒绝行为也不等于全面工具隔离验证。

computer use的DOM读取被配置禁用，未改变设置；Windows browser_tabs无调试端口不支持。窗口截图黑屏后改用屏幕zoom。一次焦点被ChatGPT桌面抢占，type/key返回focus_failed；重新激活Edge并核对空输入框后才输入，未重复已发送请求。

结果PARTIAL：可访问/可选用、资料结果一致与可见拒绝行为已观察。原始工具审计、console/network和四条完整团队E2E仍未验。没有修改插件包或业务源码。

证据：build/browser-plugin-acceptance.json、browser-plugin-read.png、browser-plugin-negative.png。截图为测试聊天局部，不包含凭证。

## 0.1.2 新会话定向端到端验收（最新）
实际通过 Edge 私人插件详情的“在聊天中试用”进入新会话：
https://chatgpt.com/c/6ae204c4-3204-83ea-b577-5cc1bb0a8a57

页面显示版本 0.1.2、唯一 agency-workflow。新会话回答与四项更新规则一致；获受限执行授权后，通过本地连接器运行 `python -B -m unittest discover -s tests -p test_review2_regressions.py -v`。本轮原始输出及执行元数据保存到 build/host-e2e-012/result.json，Codex 内置文件工具独立读回：11 项通过，exit_code 0。调用引用 87e1b3f3-49f3-45ef-b822-48c791ac2edd，开始 2026-10-28T14:23:44.543Z，结束 2026-10-28T14:23:52.830Z。页面另观察到连接器保存动作卡片和本地实际新增文件；不是仅依赖回答中的 JSON。

结论：插件新会话到本地回归执行及证据落盘的定向链路通过，未发现新的功能失败，无源码修复。调用 ID 和原始输出来自宿主保存记录，尚未与连接器独立审计数据库核对。console/network 未采集，跨第二会话恢复、完整 TEAM/ROLE 与四条综合 E2E 仍 NOT_RUN，不能上调为完整团队交付。焦点抢占与窗口截图黑屏通过 prepare_display、屏幕 zoom 恢复，未改浏览器安全配置。

## ChatGPT 开发 Demo 实测
在既有 ChatGPT 插件测试会话中实际创建 build/demo-taskboard：Python 标准库 HTTP + SQLite + 原生中文前端，新增/状态切换/筛选/删除/刷新持久化。服务 http://127.0.0.1:8765/，PID 34244；独立读取端口绑定为127.0.0.1，HTTP 200。宿主 API 测试 3 项通过，原始结果 build/demo-taskboard/test-output.json。宿主浏览器操作见该目录 REVIEW.md，报告功能通过且 favicon 修正后 console 0 errors/0 warnings。
独立读回发现初始 checkpoint 不符合公开契约和未定位 console error，反馈 ChatGPT 后由其修复；旧 checkpoint 保留 checkpoint.legacy.json，新检查点 schema/load_state/resume 验证通过，原始结果 checkpoint-validation-output.json。Codex 另用内置工具调用 team.resume 对实际保存检查点及11个产物哈希再次核验，返回 PREFLIGHT；未替代 ChatGPT 实现代码。独立桌面最终截图受反复屏保遮挡，未据此宣称独立视觉复验通过。
结论：完成一个可运行 Demo；需独立核对交付契约，不能据此认定完整TEAM/ROLE或四条综合E2E全部通过。没有安装依赖、Git提交或公网部署。
