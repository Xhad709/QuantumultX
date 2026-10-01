# QuantumultX

## Apple AI 分流

当前 Direct / Proxy 两份列表按 [Apple-AI-xhs](Rules/Apple-AI-xhs.list) 的可用组合拆分，合计 18 条规则，保持相同的匹配类型、范围和策略。用户已报告 xhs 可用；这尚未确定必要域名、具体恢复机制或长期稳定性。

| 订阅 | 文件内策略 | 规则数 | 本轮状态 |
| --- | --- | --- | --- |
| [Apple AI Direct](Rules/Apple-AI-Direct.list) | direct | 1 | 启用 |
| [Apple AI-Proxy](Rules/Apple-AI-Proxy.list) | proxy | 17 | 启用 |
| [Apple AI GPT](Rules/Apple-AI-GPT.list) | AI | 4 | 停用，保留旧分配作对照 |
| [Apple-AI-xhs](Rules/Apple-AI-xhs.list) | 1 direct + 17 proxy | 18 | 停用，保留已报告可用的完整快照 |

仅 `apple-relay.cloudflare.com` 留在 Direct；其他 17 条参考规则全部放在 Proxy。Direct / Proxy 无重复规则。保留来源的 `siri` 关键词及 `ls.apple.com` 后缀匹配，不将宽范围规则直接认定为最小必要集合。

此前 Proxy 中试加的 `configuration.apple.com`、`gsa.apple.com`、`gsas.apple.com`、`pbs2i.cdn-apple.com`、`albert.apple.com`、`gdmf.apple.com`、`setup.icloud.com`、`gateway.icloud.com.cn` 等独立候选规则均不再单独加入当前列表。撤除表示本轮按可用参考组合复现，不等于实测确认这些请求无关。`ls.apple.com` 仍保留在当前参考集合内。

## 添加订阅

本轮只启用 Direct 和 Proxy，将它们放在 `[filter_remote]` 前部。GPT、xhs、原整包 Apple Intelligence 订阅停用，临时 `apple` 关键词代理恢复为原来的直连策略。已有 OpenAI 服务订阅沿用用户自己的分流设置。

```ini
https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Apple-AI-Direct.list, tag=Apple AI Direct, force-policy=direct, update-interval=86400, opt-parser=false, inserted-resource=true, enabled=true
https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Apple-AI-Proxy.list, tag=Apple AI-Proxy, update-interval=86400, opt-parser=false, inserted-resource=true, enabled=true
```

更新两份资源，Direct 保持 direct；Proxy 的代理策略选择与成功 xhs 测试相同的节点。GPT 文件保持原样，但本轮停用，因此其中的 Apple relay 不再以旧 AI 分配覆盖本轮参考组合。未自动修改设备上的配置。

## 域名分配

| 域名或关键词 | QX 匹配类型 | 策略 | 列表 |
| --- | --- | --- | --- |
| guzzoni.apple.com | host | proxy | Proxy |
| mask-api.fe.apple-dns.net | host | proxy | Proxy |
| mask-api.icloud.com | host | proxy | Proxy |
| mask-t.apple-dns.net | host | proxy | Proxy |
| mask.apple-dns.net | host | proxy | Proxy |
| smoot.apple.com | host-suffix | proxy | Proxy |
| apple-relay.apple.com | host-suffix | proxy | Proxy |
| apple-relay.cloudflare.com | host-suffix | direct | Direct |
| apple-relay.fastly-edge.com | host-suffix | proxy | Proxy |
| apple-relay.mask.apple-dns.net | host-suffix | proxy | Proxy |
| cp4.cloudflare.com | host-suffix | proxy | Proxy |
| gspe1-ssl.ls.apple.com | host-suffix | proxy | Proxy |
| gateway.icloud.com | host-suffix | proxy | Proxy |
| ls.apple.com | host-suffix | proxy | Proxy |
| mask-h2.icloud.com | host-suffix | proxy | Proxy |
| mask.icloud.com | host-suffix | proxy | Proxy |
| apps.mzstatic.com | host-suffix | proxy | Proxy |
| siri | host-keyword | proxy | Proxy |

## 参考快照

xhs 根据 [RocM301 Apple-AI.list](https://raw.githubusercontent.com/RocM301/Apple-Rule/refs/heads/main/Apple-AI.list) 的 blob `aec7bcae4686c273c5d9619a92173f1225b3276f` 转换：DOMAIN → host、DOMAIN-SUFFIX → host-suffix、DOMAIN-KEYWORD → host-keyword。用户指定 Cloudflare relay 直连，其他规则代理。当前拆分使用的 xhs 文件 blob 为 `121700273fe066c1171402304a35e83459cf29c2`。xhs 原文件保留不改，便于对照。

## 测试记录与下一步

- 大陆网络下通过全局代理加重启恢复后，曾出现短期直连可用，约一天后再次失效；持续全局代理跨过此前失效窗口仍正常。
- 香港电话卡下重启也能恢复。上午随后扩大 Apple 代理的成功可能沿用了有效状态，不能单独作为独立恢复验证。
- 2026-10-01 晚间从失效状态重做测试，原专项列表全部代理及扩大 Apple 代理仍无法恢复；同一节点全局代理加重启仍能恢复。
- 2026-10-02 用户报告 Apple-AI-xhs 可用，并要求修改原有列表。本次将相同 18 条规则拆成 1 条 Direct 和 17 条 Proxy，先保留整组可用配置。

先验证拆分后实际路径与 xhs 一致，并观察是否跨过此前的失效窗口。后续只围绕参考组合与失败组合的差异做对照；新增的 iCloud / mzstatic 覆盖与 Cloudflare 直连例外均未被单独证明必要。若继续定位，从明确失效状态做恢复测试；恢复后立刻撤回仍可用不能排除有效状态残留。

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
