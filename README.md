# QuantumultX

## Apple AI 分流

保留原有 Direct / GPT 分配，仅将可用参考列表中此前未覆盖的 9 条规则补充到 Proxy。用户已报告 Apple-AI-xhs 可用；本次拆分保留了原有直连优先策略，实际路由与 xhs 有差异，仍需实机测试。

| 订阅 | 文件内策略 | 规则数 | 用途 |
| --- | --- | --- | --- |
| [Apple AI Direct](Rules/Apple-AI-Direct.list) | direct | 7 | 保留原有直连分配 |
| [Apple AI GPT](Rules/Apple-AI-GPT.list) | AI | 4 | 保留原有 GPT / AI 分配 |
| [Apple AI-Proxy](Rules/Apple-AI-Proxy.list) | proxy | 9 | 补充参考列表中的遗漏覆盖 |
| [Apple-AI-xhs](Rules/Apple-AI-xhs.list) | 1 direct + 17 proxy | 18 | 保留用户报告可用的完整对照快照 |

Direct 已恢复原 7 条规则，GPT 保持原样。Proxy 只补充下表中的 9 条；新增覆盖与其代理必要性尚未逐条验证，不将这份列表认定为最小必要集合。

## 添加订阅

本轮使用原 GPT、Direct 及补充 Proxy，资源顺序为 **GPT → Direct → Proxy**，并保持分流优化关闭。xhs 保留作对照，本轮测试拆分组合时不同时启用。订阅地址保持不变。

```ini
https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Apple-AI-GPT.list, tag=Apple AI GPT, force-policy=AI, update-interval=86400, opt-parser=false, inserted-resource=true, enabled=true
https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Apple-AI-Direct.list, tag=Apple AI Direct, force-policy=direct, update-interval=86400, opt-parser=false, inserted-resource=true, enabled=true
https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Apple-AI-Proxy.list, tag=Apple AI-Proxy, update-interval=86400, opt-parser=false, inserted-resource=true, enabled=true
```

Proxy 使用与成功 xhs 测试相同的代理策略和节点；已有 OpenAI 服务订阅沿用用户自己的分流设置。

没有重复收录同一域名，但存在两处宽范围重叠：Proxy 的 `ls.apple.com` 后缀包含 GPT 的 `gspe1-ssl.ls.apple.com`；Proxy 的 `siri` 关键词包含 Direct 的 `api-siri-prod.apple.com`。按上述顺序保留原有具体规则的优先级。

## Proxy 新增规则

| 域名或关键词 | QX 匹配类型 | 策略 |
| --- | --- | --- |
| mask-api.fe.apple-dns.net | host | proxy |
| mask-api.icloud.com | host | proxy |
| mask-t.apple-dns.net | host | proxy |
| mask.apple-dns.net | host | proxy |
| ls.apple.com | host-suffix | proxy |
| mask-h2.icloud.com | host-suffix | proxy |
| mask.icloud.com | host-suffix | proxy |
| apps.mzstatic.com | host-suffix | proxy |
| siri | host-keyword | proxy |

## 参考快照

xhs 根据 [RocM301 Apple-AI.list](https://raw.githubusercontent.com/RocM301/Apple-Rule/refs/heads/main/Apple-AI.list) 的 blob `aec7bcae4686c273c5d9619a92173f1225b3276f` 转换：DOMAIN → host、DOMAIN-SUFFIX → host-suffix、DOMAIN-KEYWORD → host-keyword。用户指定 Cloudflare relay 直连，其他规则代理。xhs 文件 blob 为 `121700273fe066c1171402304a35e83459cf29c2`，原文件保留不改。

## 测试记录与下一步

- 大陆网络下通过全局代理加重启恢复后，曾出现短期直连可用，约一天后再次失效；持续全局代理跨过此前失效窗口仍正常。
- 香港电话卡下重启也能恢复。上午随后扩大 Apple 代理的成功可能沿用了有效状态，不能单独作为独立恢复验证。
- 2026-10-01 晚间从失效状态重做测试，原专项列表全部代理及扩大 Apple 代理仍无法恢复；同一节点全局代理加重启仍能恢复。
- 2026-10-02 用户报告 Apple-AI-xhs 可用。本轮保留原有 Direct / GPT 分配，仅补入参考列表此前未覆盖的 9 条 Proxy 规则。

下一步验证此补充组合能否从明确失效状态恢复，并观察是否跨过此前的失效窗口。若未恢复，应进一步比较此组合与 xhs 的路由差异；当前不能把成功归因于某个新增域名。恢复后立即撤回仍可用，不能排除有效状态残留。

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
