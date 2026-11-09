# TEAM-14 同一证据目标并发与重复写入拒绝（2026-11-03）

本轮仅在新隔离目录执行，未改动历史试验和共享状态。线上原私人插件元数据为 USER/PRIVATE 0.2.10；被测 check_runner.py SHA-256 为 \`7ad73950c45a12bd21fc9e5f84d17259cf9c7b4e9628bef70e9e79a5400fda64\`。

真实 Windows Python 子进程对相同 checkpoint 摘要及相同 evidence/SHARED.json 目标并发执行，共 3 轮。每轮预期仅一个子进程成功、另一个被拒绝，且只产生一份 capture 与一次业务副作用。随后使用最新 checkpoint 摘要再次尝试写入相同 capture，必须在启动业务子进程前拒绝，旧 capture 与 checkpoint 哈希保持不变。

实际结果：3/3 并发单写者检查通过；3/3 重复目标拒绝通过；3/3 validate PASS / ready 预期 FAIL。全部 5 项共享文件 SHA-256 前后不变。

审计文件：\`build/host-workflow-v2/team14-same-target-parallel-20261103T0750JST/SAME_TARGET_AUDIT.json\`；SHA-256：\`4779fd077e3607b4e8185beb83f9a60b5ae53567806786cee37c1403367b24c2\`。每轮原始 stdout/stderr、PID、退出码、capture、checkpoint 和副作用文件均保留。

此为 TEAM-14 的局部隔离并发安全验证，不计入完整 TEAM-14、ROLE 或严格连续宿主验收。trial-27 原宿主结束证据仍 UNKNOWN，runs.json 的 SUBMITTED_RUNNING 不作事后修改；历史失败全部保留。
