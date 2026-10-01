# QuantumultX

## Apple AI 分流

将墨鱼 AppleIntelligence.list 的 11 个域名拆成两份，采用 Quantumult X 原生 host-suffix 语法。两份列表互不重复，保留上游原有的后缀匹配范围；这是按域名划分的路由基线，不代表端点用途互斥。

| 订阅 | 策略 | 规则数 |
| --- | --- | --- |
| [Apple AI GPT](Rules/Apple-AI-GPT.list) | AI代理 | 4 |
| [Apple AI Direct](Rules/Apple-AI-Direct.list) | Direct | 7 |

普通 Apple 服务继续由现有本地规则 `host-suffix, apple.com, direct` 处理。OpenAI / ChatGPT 服务域名继续由既有 blackmatrix7 OpenAI.list → AI 处理；Apple AI GPT 文件仅覆盖本次拆分涉及的 Apple 侧端点。

## 2026-10-01 香港出口排查测试

[Apple AI-Proxy](Rules/Apple-AI-Proxy.list) 当前包含 7 条临时规则：原有 `configuration.apple.com`、`gsa.apple.com`、`gsas.apple.com`、`ls.apple.com` 四组候选，以及新增的 `pbs2i.cdn-apple.com`、`albert.apple.com`、`gdmf.apple.com` 三个精确域名，均使用 `🇺🇳` 策略。

候选的必要性及具体作用尚未确认。新增三个域名曾在成功日志出现，原专项列表未覆盖；这只构成测试线索，不证明它们参与 AI 验证。本轮不加入整个 `apple.com` 或 `cdn-apple.com` 后缀，也不加入 `itunes.apple.com`；Apple Music 可以解释部分后台请求，但 itunes 尚未被独立实测排除。

三个 PCC 端点 `cp4.cloudflare.com`、`apple-relay.cloudflare.com`、`apple-relay.fastly-edge.com` 仍只列在 Direct 文件中，文件默认策略保留 direct。设备上本轮已将三份专项订阅全部切为香港代理；这是当前失败对照，不要在新增域名测试时同时恢复 PCC 直连。

测试记录：
- 大陆网络下恢复后约一天可能再次失效；全局香港代理持续超过此前失效窗口仍正常；香港电话卡下重启也能恢复。
- 11:24 香港电话卡恢复后，11:32 扩大 Apple 代理覆盖的成功可能沿用了有效状态，不能将该轮单独视为独立恢复验证。
- 晚间用户报告三份专项列表全部代理后重启仍失败，并确认 Apple 整体代理可行。下一轮扩大覆盖到上述三个具体域名，不重复整段 Apple 代理测试。

将下行放在 `[filter_remote]` 的最前部，先于现有 GPT、Direct 和其他插入资源：

```ini
https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Apple-AI-Proxy.list, tag=Apple AI-Proxy, force-policy=🇺🇳, update-interval=86400, opt-parser=false, inserted-resource=true, enabled=true
```

本轮操作：
1. 手动更新 Proxy 订阅，确认新增三个域名已加载。
2. 使用大陆网络，固定已实测可用的香港节点；保持专项列表此前的香港代理组合及关闭的分流匹配优化。不要同时更改 DNS、UDP 或排除路由。
3. 保持宽泛 Apple 代理规则关闭，以免它覆盖新增规则之外的请求；检查新增三个域名出现时的实际命中策略。
4. 从明确失效状态重启并测试同一个写作工具操作，记录结果及相关请求。若恢复，停止增加规则。
5. 本次按用户要求同时加入三个域名；若恢复，只能先定位到新增三域名这一组，不能直接认定其中某个为唯一根因。需要后续失效状态下的分组或单域名重复对照。
6. 失败仅说明当前组合不足，不能排除已加入规则的必要性。恢复后立即撤回规则仍能使用，也不能反证新增代理是否必要。

本列表会临时覆盖原 GPT 列表中的 `gspe1-ssl.ls.apple.com`。原 Direct / GPT 文件未改动。撤回本列表时停用该订阅；设备上另行改过的 force-policy 需要按自己的对照方案恢复。未自动修改设备上的 QX 配置。

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

已配置每周二北京时间 10:30 的 GitHub Actions 检查，并支持手动 Run workflow。仅在规则变化时创建或更新一个待测试 PR；正式 GPT / Direct 订阅由人工维护，机器人不修改、不自动合并。

[设置权限、邮件通知、日志保留及处理更新的完整说明](docs/apple-ai-upstream.md)。
