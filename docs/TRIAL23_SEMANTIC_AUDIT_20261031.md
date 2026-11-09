# trial-23 独立语义核验补充（2026-10-31）

本文件是验收方**旁路只读**核验摘要，不属于原 ChatGPT 宿主提交的交付物；不修改原试验、原失败记录或冻结候选，也不以验收方补救替代自主成功。

独立审计：`build/host-workflow-v2/trial23-semantic-readonly-audit-20261031.json`，SHA-256 `75b186d98d7c0eee4cdd60c6a7c389c445d4ae5a4b75c31585471d1a0a391889`。

核验对象：trial-23 checkpoint revision 52，SHA-256 `59dbaadf3a96f53541e877ae0377ac8feb4cbab8c665ec4ef1c22b9544f74eeb`；5/5 阶段完成、22/22 证据文件哈希一致、4 次正式交接、7/7 冻结源码哈希一致、最终 TASKS.md revision 52、无待处理操作。观察器从空目录开始记录 116 次快照，正常有限期结束，最后一帧观察到 revision52 与最终文件。

本次新增的**语义级**核对不只是读取 PASS 字段，而是逐项检查原始捕获内容及时间顺序：后端两次实际退出码 1 的 FAIL，第三次退出码 0、5/5 OK，最终成功证据 `supersedes` 同时指向两次失败；集成测试退出码 0、2/2 OK，包含同库重启用例；真实 Playwright 点击及快照显示空标题被拒绝、121 字标题被拒绝、非法状态 `UNKNOWN_STATE` 被拒绝；浏览器重启前后分别观察到 `127.0.0.1:18652` 与 `127.0.0.1:23950`，同一中文任务仍存在且处于进行中。所有核验均只读原始 trial 文件，审计输出在独立同级目录原子创建。

**新增待修复的非核心缺陷：** 浏览器控制台只读返回两条 `favicon.ico` HTTP 404（分别来自两个历史实例端口 18652、23950）。核心 HTML/CSS/JS/API 请求均返回 200。该问题不应在已冻结或仍运行的 trial-23 内由验收方事后修改；后续新项目需在设计/前端阶段增加 favicon 资源或返回有效 favicon，并在浏览器阶段检查 console/network。当前记为 `UNRESOLVED_COSMETIC`，不把它伪装为零错误。

**仍未满足严格自主验收：** 原宿主 UI 持续显示「停止」，`runs.json` 仍为 `SUBMITTED_RUNNING`，没有自然完成的最终回执；执行来源认证为 UNKNOWN。不能计入连续 clean 1/3，不能升级 TEAM-01..14、ROLE-01..18、E2E-TEAM-A/B/C/D 的完整宿主结果。主脚本和原有 STATUS/TASKS 文档存在共享进程文件句柄问题，不强制解锁或绕过原子保存。下次先确认宿主自然结束，再按已发布 0.2.9 的独立 validate/ready 及严格证据门禁做 CAS 原子归档。
