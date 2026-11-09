# trial-26 独立核查审计文件纠正（追加记录）

前一审计 trial26-independent-readonly-audit-20261101T024756Z.json 在末尾意外追加字面量反引号+n，导致 JSON 解析失败。原件及其 SHA256 a9241760d06df2f367a529661a816a94029ea2c93b105bdf3b6242dabb68f223 保留，不能作为有效 JSON 使用。

纠正后的有效 JSON：build/host-workflow-v2/trial26-independent-readonly-audit-corrected-20261101T024756Z.json
SHA256：841af188c8a355b24402016d90da9e31e17d13f70f020c73bc120e04e5fde814。已用 ConvertFrom-Json 读回验证 revision 26。

此纠正只涉及独立审计的序列化，不涉及 trial-26、runs.json、STATUS.md、TASKS.md、任何 QA 失败证据或宿主试验的更改。原宿主结束仍未得到证明，严格连续成功仍为 0/3。