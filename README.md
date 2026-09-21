# QuantumultX

## Apple AI 分流

将墨鱼 AppleIntelligence.list 的 11 个域名拆成两份，采用 Quantumult X 原生 host-suffix 语法。两份列表互不重复，保留上游原有的后缀匹配范围；这是按域名划分的路由基线，不代表端点用途互斥。

| 订阅 | 策略 | 规则数 |
| --- | --- | --- |
| [Apple AI GPT](Rules/Apple-AI-GPT.list) | AI代理 | 4 |
| [Apple AI Direct](Rules/Apple-AI-Direct.list) | Direct | 7 |

普通 Apple 服务继续由现有本地规则 `host-suffix, apple.com, direct` 处理。OpenAI / ChatGPT 服务域名继续由既有 blackmatrix7 OpenAI.list → AI 处理；Apple AI GPT 文件仅覆盖本次拆分涉及的 Apple 侧端点。

## 添加订阅

关闭原来整包 `Apple Intelligence → AI` 的插入资源，将下面两行放到现有 `[filter_remote]` 区域的前部：

```ini
https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Apple-AI-GPT.list, tag=Apple AI GPT, force-policy=AI, update-interval=86400, opt-parser=false, inserted-resource=true, enabled=true
https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Apple-AI-Direct.list, tag=Apple AI Direct, force-policy=direct, update-interval=86400, opt-parser=false, inserted-resource=true, enabled=true
```

两份均设置 `inserted-resource=true`，使 GPT 例外先于本地 `apple.com → direct` 命中，并让 Direct 端点先于其他代理订阅命中。原整包订阅必须保持关闭。文件为 QuanX 原生格式，使用 `opt-parser=false`。策略名沿用已有的 `AI` 和 `direct`。

## 域名分配

| 域名 | 策略 | 依据与边界 |
| --- | --- | --- |
| apple-relay.apple.com | AI | Apple 官方归类为 Apple Intelligence Extensions |
| apple-relay.mask.apple-dns.net | AI | v2fly 列入 ChatGPT Extension；不能据此断言其专属用途 |
| apple-relay.akamaized.net | AI | 沿用墨鱼的 relay 候选，具体必要性待实测 |
| gspe1-ssl.ls.apple.com | AI | 社区规则中的地区判断兼容性候选，可能影响地图、eSIM 等其他服务 |
| gateway.icloud.com | direct | 沿用原列表，优先直连；没有认定其为 AI 专用端点 |
| guzzoni.apple.com | direct | Apple 官方归类为 Siri 与听写 |
| smoot.apple.com | direct | Apple 官方归类为搜索服务 |
| api-siri-prod.apple.com | direct | 沿用原列表的 Siri 相关候选，细分用途与必要性待验证 |
| cp4.cloudflare.com | direct | Apple 官方列为 PCC |
| apple-relay.cloudflare.com | direct | Apple 官方列为 PCC，v2fly 也将其列入 ChatGPT Extension |
| apple-relay.fastly-edge.com | direct | Apple 官方列为 PCC，v2fly 也将其列入 ChatGPT Extension |

### 共享 relay 的处理

Cloudflare 和 Fastly 两个端点先采用 direct，以符合 Apple 自有 AI 优先直连的目标。同一个域名的请求无法仅靠这两份域名规则按 PCC / GPT 功能分别路由，因此这不是所有环境下均已验证的最小 GPT 规则集。

若启用本方案后 GPT Extension 失败，而相同环境下全局台湾代理可用，先对照请求记录测试这两个共享端点。确认某个需要 AI 后，将它从 Direct 文件移除，再加入 GPT 文件。被改走 AI 的共享端点也可能承载 PCC 请求，届时这部分 Apple 云端流量也会经过台湾代理。

## 测试依据

用户报告在 iPadOS 27 上，通过全局代理加重启恢复功能后，关闭 QX，文字工具、图乐园、扩图与重构、高质量消除、描述创建快捷指令均可使用；额外重启后，开关代理也没有影响这些功能。

这支持该设备与网络条件下的功能直连可用性。没有逐个端点的完整请求记录，本仓库中的 4 + 7 混合分流尚未在设备上验证，GPT Extension 的最小代理集合及长期稳定性仍需实际使用确认。此前恢复的具体原因未确定。

## RocM301 列表的参考价值

该列表可补充排查候选，未发现足以据此直接新增代理规则的实测证据。本次没有把下列九条新增规则加入活动列表：

| 新增项 | 保留作候选的原因 |
| --- | --- |
| mask-api.icloud.com、mask-h2.icloud.com、mask.icloud.com | Apple 官方列为 iCloud Private Relay，与 PCC 为不同服务 |
| mask-api.fe.apple-dns.net、mask-t.apple-dns.net、mask.apple-dns.net | Apple DNS / relay 相关候选，尚无证据证明本次 AI 功能必须经它们代理 |
| DOMAIN-SUFFIX,ls.apple.com | 比 gspe1-ssl.ls.apple.com 的覆盖范围更宽 |
| DOMAIN-SUFFIX,apps.mzstatic.com | Apple 内容分发相关候选，下载故障时可检查 |
| DOMAIN-KEYWORD,siri | 匹配范围过宽，优先使用明确的 Apple 域名 |

RocM301 没有覆盖 apple-relay.akamaized.net；api-siri-prod.apple.com 虽未单独列出，但可被其 siri 关键词规则覆盖。它也把 guzzoni.apple.com 从后缀匹配收窄为精确匹配，因而不是原列表的完整超集。

## 来源与维护

- [墨鱼 AppleIntelligence.list](https://raw.githubusercontent.com/ddgksf2013/Filter/refs/heads/master/AppleIntelligence.list)，本次读取到的上游标注更新日期为 2026-09-17。
- [Apple 企业网络端点说明](https://support.apple.com/en-us/101555)。
- [v2fly apple-intelligence](https://github.com/v2fly/domain-list-community/blob/master/data/apple-intelligence)。
- [RocM301 Apple-AI.list](https://raw.githubusercontent.com/RocM301/Apple-Rule/refs/heads/main/Apple-AI.list)。
- [Quantumult X 官方示例](https://github.com/crossutility/Quantumult-X/blob/master/sample.conf)。

这两份列表在本仓库手动维护，不自动同步上游。订阅的 update-interval 只会定期下载本仓库的新版本。

## 上游每周检查

已配置每周一北京时间 10:30 的 GitHub Actions 检查，并支持手动 Run workflow。仅在规则变化时创建或更新一个待测试 PR；正式 GPT / Direct 订阅由人工维护，机器人不修改、不自动合并。

[设置权限、邮件通知、日志保留及处理更新的完整说明](docs/apple-ai-upstream.md)。
