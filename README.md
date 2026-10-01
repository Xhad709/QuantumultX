# QuantumultX

## Apple AI 分流

保留原有 Direct / GPT 分配，Proxy 仅补充 4 个候选域名：它们既未被原专项列表覆盖，也不在此前扩大 `apple` 关键词代理的测试范围内。Apple-AI-xhs 保留为用户报告可用的对照快照。

| 订阅 | 文件内策略 | 规则数 | 用途 |
| --- | --- | --- | --- |
| [Apple AI Direct](Rules/Apple-AI-Direct.list) | direct | 7 | 保留原有直连分配 |
| [Apple AI GPT](Rules/Apple-AI-GPT.list) | AI | 4 | 保留原有 GPT / AI 分配 |
| [Apple AI-Proxy](Rules/Apple-AI-Proxy.list) | proxy | 4 | 补充本轮待确认的候选域名 |
| [Apple-AI-xhs](Rules/Apple-AI-xhs.list) | 1 direct + 17 proxy | 18 | 保留用户报告可用的完整对照快照 |

Direct 和 GPT 保持原样。`mask-api.fe.apple-dns.net`、`mask-t.apple-dns.net`、`mask.apple-dns.net`、`ls.apple.com` 已在此前扩大 `apple` 关键词代理的测试范围内，本轮不再加入 Proxy。`siri` 关键词也暂不加入，先测试下表的 4 个具体域名。

## 添加订阅

本轮使用原 GPT、Direct 及补充 Proxy，资源顺序为 **GPT → Direct → Proxy**，放在普通 Apple / iCloud / mzstatic 分流之前，并保持分流优化关闭。xhs 保留作对照，本轮测试时不同时启用。订阅地址保持不变。

```ini
https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Apple-AI-GPT.list, tag=Apple AI GPT, force-policy=AI, update-interval=86400, opt-parser=false, inserted-resource=true, enabled=true
https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Apple-AI-Direct.list, tag=Apple AI Direct, force-policy=direct, update-interval=86400, opt-parser=false, inserted-resource=true, enabled=true
https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Apple-AI-Proxy.list, tag=Apple AI-Proxy, update-interval=86400, opt-parser=false, inserted-resource=true, enabled=true
```

Proxy 使用与成功 xhs 测试相同的代理策略和节点；已有 OpenAI 服务订阅沿用用户自己的分流设置。


## Proxy 新增规则

| 域名或关键词 | QX 匹配类型 | 策略 |
| --- | --- | --- |
| mask-api.icloud.com | host | proxy |
| mask-h2.icloud.com | host-suffix | proxy |
| mask.icloud.com | host-suffix | proxy |
| apps.mzstatic.com | host-suffix | proxy |

## 参考快照

xhs 根据 [RocM301 Apple-AI.list](https://raw.githubusercontent.com/RocM301/Apple-Rule/refs/heads/main/Apple-AI.list) 的 blob `aec7bcae4686c273c5d9619a92173f1225b3276f` 转换：DOMAIN → host、DOMAIN-SUFFIX → host-suffix、DOMAIN-KEYWORD → host-keyword。用户指定 Cloudflare relay 直连，其他规则代理。xhs 文件 blob 为 `121700273fe066c1171402304a35e83459cf29c2`，原文件保留不改。

## 测试记录与下一步

- 大陆网络下通过全局代理加重启恢复后，曾出现短期直连可用，约一天后再次失效；持续全局代理跨过此前失效窗口仍正常。
- 香港电话卡下重启也能恢复。上午随后扩大 Apple 代理的成功可能沿用了有效状态，不能单独作为独立恢复验证。
- 2026-10-01 晚间从失效状态重做测试，原专项列表全部代理及扩大 Apple 代理仍无法恢复；同一节点全局代理加重启仍能恢复。
- 2026-10-02 用户报告 Apple-AI-xhs 可用。本轮保留原有 Direct / GPT 分配，Proxy 缩减为原列表未覆盖、且不在此前扩大 `apple` 关键词测试范围内的 4 个域名。

先从明确失效状态测试这 4 条组合能否恢复。如果成功，再逐条确认：每轮只改变一条规则，并在失效状态下验证是否能恢复。恢复后立即撤回仍可用，不能作为该规则无关的依据。

## 来源与维护

- [墨鱼 AppleIntelligence.list](https://raw.githubusercontent.com/ddgksf2013/Filter/refs/heads/master/AppleIntelligence.list)，本次读取到的上游标注更新日期为 2026-09-17。
- [Apple 企业网络端点说明](https://support.apple.com/en-us/101555)。
- [v2fly apple-intelligence](https://github.com/v2fly/domain-list-community/blob/master/data/apple-intelligence)。
- [RocM301 Apple-AI.list](https://raw.githubusercontent.com/RocM301/Apple-Rule/refs/heads/main/Apple-AI.list)。
- [Quantumult X 官方示例](https://github.com/crossutility/Quantumult-X/blob/master/sample.conf)。

这些列表在本仓库手动维护，不自动同步上游。订阅的 update-interval 只会定期下载本仓库的新版本。

## 上游每周检查

已配置每周二北京时间 10:30 的 GitHub Actions 检查，并支持手动 Run workflow。仅在规则变化时创建或更新一个待测试 PR；正式 GPT / Direct 订阅由人工维护，机器人不修改、不自动合并。

[设置权限、邮件通知、日志保留及处理更新的完整说明](docs/apple-ai-upstream.md)。
