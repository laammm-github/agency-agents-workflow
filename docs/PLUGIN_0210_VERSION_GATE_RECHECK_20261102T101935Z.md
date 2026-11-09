# Agency Agents Workflow：0.2.10 在线版本变化与严格验收门禁

本次通过本会话实际可用的 Plugin Creator get_plugin_metadata/get_plugin_files 读回：原私人插件 USER/PRIVATE，当前版本 **0.2.10**，Release **pluginrel_6ae857ea7ce4819193bcd1a74d0f83b5**，共 71 个文件。旧的 0.2.9 Release **pluginrel_6ae53a8cc71881919a8e7c98c19f7536** 已不是当前 Release；不能将当前版本当作 0.2.9 宿主核验通过。

与本地 0.2.9 shadow 资源按规范化换行比较：team.py、workflow_v2.py 文本一致；Skill 只有版本标题不同；check_runner.py 新增“成功且显式 supersedes 时，从任务当前 evidence_refs 移除对应失败证据引用”的处理，同时保留不可变 evidence 历史和原始 capture。此项为源码比对，不是 0.2.10 运行验收 PASS。

只读复核：trial-22 checkpoint revision43，HANDOVER EXECUTING，历史 ready FAIL、非清洁归档不变；trial-27 checkpoint revision14，BACKEND FAILED，runs.json 仍为 SUBMITTED_RUNNING；最后观察器样本为 2026-11-01 10:12:18 UTC。进程列表未见对应活动 watcher，但不能据此确认远端 ChatGPT 宿主已结束。严格 0.2.9 连续自主成功仍为 **0/3**。

安全决策：保留 trial-27、runs.json、共享 docs/STATUS.md 与 docs/TASKS.md 原状；不启动并发宿主试验，不对旧试验补发纠错，不把独立子测试计完整 TEAM/ROLE/E2E。下一步先核实原宿主结束，再按其原定 0.2.9 版本要求完成独立终审和原子归档；任何新试验必须按实际在线 0.2.10 重新确定版本门禁，不能伪称使用 0.2.9。

原始五文件 SHA-256 及读前读后比对记录在同时间戳独立 JSON 审计中。新增文档和审计采用同卷临时文件原子重命名，历史失败未覆盖。