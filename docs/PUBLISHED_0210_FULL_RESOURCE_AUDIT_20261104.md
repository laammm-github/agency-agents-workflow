# 2026-11-04 0.2.10 线上完整资源与根同步阻断复核

## 真实工具执行
- Plugin Creator 对原 USER/PRIVATE 插件读取当前 release: 0.2.10 / `pluginrel_6ae857ea7ce4819193bcd1a74d0f83b5`，读取全部 71 文件，无 missing_paths/size_limited_paths。每 15 个文件保存一次线上返回内容到 `build/published-0210-resource-audit-20261104/remote-files-1..5.json`。
- 新隔离比较脚本 `compare_release.py` 实际运行 exit0；输出 `COMPARISON.json`。
- 71 个线上文件中 70 个在候选源码目录可找到，按统一 CRLF/LF 后 70/70 内容一致；候选 ZIP 内 70/70 对应资源同样一致，没有内容差异。线上还有一个 `.codex-plugin/plugin.json`，其不在本地候选目录和固定 ZIP 中；仅报告这一差异，不推断它由何平台自动生成。
- 严格字节逐一相等为 33/71，其余候选文件差异为换行符格式；内容标准化比较 70/70。ZIP SHA256 `005e75607c87d7305b95c6024011f8ba39f09de44442425db44238aea478b0a7`。
- 原根工程同步前置条件只读检查：11 个待同步 root 文件的原 SHA256 与前一轮审计基线全部相符，根 `plugin.json` 仍为 0.2.8；freeze checkpoint revision40，trial-27 revision14、runs status=SUBMITTED_RUNNING。
- OmniTool/psutil 实际查到旧 Desktop Commander Node PID20772 的 open_files 包含根 `scripts/team.py`、`scripts/workflow_v2.py`、`scripts/check_runner.py` 及历史 checkpoint 等；旧 PID 仍在。遵照用户明确要求，不操作其文件句柄、不终止进程、不强行覆盖主目录。
- 之前启动的大范围批量直读在 OmniTool 连接初始化冲突和单次调用上限下未完成，因此改为限定 15 文件一次的真实 Plugin Creator 读取，再保存在独立目录，由本地校验脚本作最终文件级比较；不宣称失败批量调用成功。

## 结论和下一步
- 发布物与固定候选 70 个可打包资源内容一致：PASS，版本 0.2.10，线上额外元文件 1 个；这证明静态文件一致，**不是**独立宿主在测试会话中读取/调用当前插件的证明。
- 根工程仍 0.2.8，11 文件 overlay 已准备，但三主脚本确有共享句柄，不强行写入。下一步须在自然释放或真正隔离的新工作树完成原子同步与测试，不能仅因源文件内容相符就宣称主工程升级。
- trial-27 的宿主结束状态仍未知，不能通过 PID 消失或本地检查点未变化解除未知副作用。真实 W4 连续自主 0/3、TEAM 0/14、ROLE 0/18、E2E 0/4 严格计数维持不变。
- 安全可继续执行的是基于已发布/候选内容一致性的隔离验收准备和全新宿主版本门禁；实际新宿主必须从被测会话读取元数据，不能用本次跨会话的 Plugin Creator 读取代替。

本报告是模型撰写的审计摘要。原始线上内容、比对脚本及逐文件布尔结果保存在独立目录；独立 connector 执行身份不由本报告认证。
