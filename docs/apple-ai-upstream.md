# Apple AI 上游每周检查

每周二北京时间 10:30 检查，UTC cron 为 `30 2 * * 2`。GitHub 的定时调度可能延迟，不能保证准点。也可在 Actions → Check Apple AI upstream → Run workflow，选择 main 手动运行。

## 文件与权限边界

- `.github/workflows/check-apple-ai.yml`：GitHub 托管 ubuntu-latest，最长 5 分钟，只使用 GitHub 官方 actions/checkout，固定完整提交 SHA。
- `scripts/check_apple_ai.py`：Python 标准库下载、比较和调用 GitHub API，不调用 AI、OpenAI、SMTP 或第三方服务。
- `upstream/AppleIntelligence.list`：已审阅的上游基准。初始版本为上游标注 2026-09-17 的 11 条规则，与现有 4 + 7 分流对应。
- `automation/apple-ai-upstream`：机器人专用分支，只提交基准文件。不要在这个分支手动编辑正式订阅。
- `Rules/Apple-AI-GPT.list` 与 `Rules/Apple-AI-Direct.list` 始终人工维护。

工作流只申请 `contents: write` 与 `pull-requests: write`，其余权限不授予。GITHUB_TOKEN 是 GitHub 为每次任务自动生成的，不需要自行创建 Token。GitHub 的 contents 权限不能限制到单个文件，因此只写基准的边界由脚本固定路径、单文件 tree 和分支检查实现。工作流仅接收 schedule 与 workflow_dispatch，不执行外部 PR 代码。

## GitHub 需要设置什么

仓库 Settings → Actions → General：

1. Actions permissions 允许 GitHub 官方 Actions。若采用选择性允许，勾选 Allow actions created by GitHub，使 actions/checkout 可运行。
2. Workflow permissions 下勾选 **Allow GitHub Actions to create and approve pull requests** 并保存。开关的名称包括 approve，但本脚本不审批、不自动合并。
3. 默认 Token 权限可以继续保留 **Read repository contents and packages permissions**。workflow 已单独声明两个必要的 write 权限，不必为了本任务把所有工作流的默认权限改成 Read and write。
4. Artifact and log retention 或对应的日志保留设置填写 **14 days** 并保存。这是仓库设置，不能靠 workflow 中添加 retention-days 控制日志。它可能同时影响仓库其他 Actions 记录；新设置不追溯既有记录。

## 邮件通知

个人 Settings → Notifications，地址 https://github.com/settings/notifications ：

- Subscriptions 下的 Watching 和 Participating / @mentions 开启 Email，检查默认通知邮箱已验证且正确。
- 邮件活动选项保留 Comments；如希望提交也通知，开启 Pull request pushes。
- System → Actions 开启 Email，并勾选 **Only notify for failed workflows**，保存。成功且无变化的检查不发 Actions 成功邮件。

仓库页面右上角 Watch → Custom → **Pull requests** → Apply。确保没有 Ignore；待处理 PR 的 Notifications 保持订阅，不要只订阅 merged / closed 等状态。

创建 PR 后，后续每组新的差异会更新正文并添加一次评论，让 GitHub 的常规订阅通知提醒你；同样的差异不重复评论。邮件可能合并或延迟，正文修改本身不保证单独发送邮件，因此这里使用评论通知。实际邮箱投递需要在你的账户设置完成后验证。

Actions 失败通知通常发给触发运行的人；定时任务与创建 workflow / 最后修改 cron 的用户有关，单独 Watch 仓库不能保证收到全部失败邮件。部署后请用自己的账号手动 Run workflow。若 workflow 的 cron 提交者显示为机器人，请由自己的账号在网页编辑 cron 为等价写法 `30 2 * * TUE`，保持周二北京时间 10:30，让定时通知关联到自己的账号。

## 检测行为

只比较实际规则集合，忽略注释、空白、大小写和顺序。完全相同或仅格式变化不产生 commit、PR、评论或仓库文件修改。支持 DOMAIN、DOMAIN-SUFFIX、DOMAIN-KEYWORD 两字段语法。

新增和删除逐条展示；同域名匹配方式变化另列。域名替换只能可靠识别为删除旧域名、新增新域名，不猜测对应关系。

无响应、非 200、重定向、非 text/plain、无效 UTF-8、HTML、空文件、重复规则、未知格式、超过 64 KiB、少于 3 条或超过 200 条都会失败。相对基准条数小于一半、超过两倍，或超过一半旧规则消失，也停止并报错。即使这种大改是合法的，也需要人工核查；保护阈值有意保守。

尚未处理的变化一直保留在同一个开放 PR。上游再次变化时只更新该 PR 和基准候选。失败中断后的重跑会补齐未完成的 PR 或通知，避免相同快照反复提交。自动化分支出现其他文件改动时停止。

上游回退到已确认基准时，任务按无变化处理，不自动关闭已有 PR。合并待处理 PR 前应手动运行一次，并核对最新结果；如果最新结果是无变化，旧候选可能已过时，应人工关闭。

## 收到 PR 后如何处理

PR 标题：**Apple AI：上游规则变更待测试**。

正文包括新增规则、删除规则、同域名匹配方式变化和人工检查清单。Files changed 只应出现 `upstream/AppleIntelligence.list`。

测试并核查后，决定域名加入 GPT、加入 Direct 或暂不加入。需要修改正式订阅时在另一个人工提交中完成。审阅完成后合并基准 PR，表示这批上游变化已经处理；合并基准 PR 本身不会改变路由。即使暂不采用新域名，也可以确认基准。仅关闭而不合并不会更新基准，下次会重新提醒。

合并后可以删除自动化分支，下一次变化会重新创建。没有自动合并、自动审批或按域名猜测策略的代码。

## 验证与持续运行

本地可运行：

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/check_apple_ai.py --dry-run --candidate upstream/AppleIntelligence.list
```

第二条使用真实基准作为无变化样本，预期输出：

```text
No rule changes (11 rules). No commit, PR or file changes.
```

真实云端验证：Actions → Check Apple AI upstream → Run workflow → main。绿色运行中查看 Compare upstream and maintain review PR 步骤及 Summary；上游未变时应显示上面的无变化信息。检查 Pull requests 没有新增候选，main 没有新检查提交，正式订阅历史没有变化。一次无变化成功不能证明创建 PR 的权限已经开启，仍需核对上面的开关。

确认定时任务启用：打开 workflow 页面，若出现 Enable workflow 则点击恢复；菜单有 Disable workflow 表示目前启用。每周检查是否有事件类型为 schedule 的运行，只有手动运行成功不代表定时调度已经发生。

**公开仓库 60 天无活动时，GitHub 会自动停用定时 workflow。** 本方案不制造保活提交。长期不更新仓库时，需要留意停用提示并手动恢复；仅检查日志不能替代恢复。GitHub 调度也可能延迟或丢弃排队任务。

不上传 artifact，不使用 cache，不保存每周副本。正常无变化运行只有 GitHub 日志。确认更新后的旧基准仍属于正常 Git 提交历史，不会抹除历史；每批真实变化只有一个很小的规则文本。

## 官方说明

- Actions 设置与日志保留：https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
- Actions 邮件：https://docs.github.com/en/subscriptions-and-notifications/how-tos/managing-github-actions-notifications
- 运行通知归属：https://docs.github.com/en/actions/concepts/workflows-and-actions/notifications-for-workflow-runs
- 通知订阅：https://docs.github.com/en/subscriptions-and-notifications/get-started/configuring-notifications
- 定时任务限制：https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
