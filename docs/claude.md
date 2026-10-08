# Claude 分流规则

两份规则按匹配类型和匹配内容去重合并。2026-10-08 核对：本仓库原有 22 条，blackmatrix7 提供 3 条且全部重复，合并后仍为 22 条。两种格式的匹配内容一致。

## Quantumult X

订阅地址（沿用原地址）：

https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Claude.list

添加到 `[filter_remote]`：

```ini
https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Claude.list, tag=Claude, force-policy=AI, update-interval=86400, opt-parser=false, inserted-resource=true, enabled=true
```

策略名为 `AI`；请确保已有同名策略，或将 force-policy 改成自己的策略名。

## Clash Meta / Mihomo

订阅地址：

https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Claude.yaml

这是 classical 类型的规则集，需要通过 rule-providers 引用，并非完整的节点订阅或客户端配置。保留 IP-ASN 规则，需使用支持该规则的 Clash Meta / Mihomo 内核。

将以下内容合并进现有配置对应位置，RULE-SET 放在可能提前匹配的通用规则及 MATCH 之前：

```yaml
rule-providers:
  Claude:
    type: http
    behavior: classical
    format: yaml
    url: https://raw.githubusercontent.com/Xhad709/QuantumultX/main/Rules/Claude.yaml
    path: ./ruleset/Claude.yaml
    interval: 86400

rules:
  - RULE-SET,Claude,AI
```

将 `AI` 改成自己的代理策略组名。规则集内不写策略，由 RULE-SET 统一指定。IP 规则未添加 no-resolve，与当前 QX 规则的解析行为保持一致。

## 来源与维护

- [本仓库原 Claude.list](https://github.com/Xhad709/QuantumultX/blob/bb7005fafdb22d311433e001a1e3d6a4df0edba5/Rules/Claude.list)，文件 blob：`fec59f94665a4833a306ab3eaa309088fde86fb3`。
- [blackmatrix7 Claude.list](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/QuantumultX/Claude/Claude.list)，本次读取的文件 blob：`6a1095eac133026ec2fe79783c0f81b721f93365`。
- [Mihomo 规则集格式说明](https://wiki.metacubex.one/en/config/rule-providers/content/)。

本次是手动合并；客户端更新间隔仅定期下载本仓库文件，不会自动同步上游。
