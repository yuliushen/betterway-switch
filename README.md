# BetterWay · 更优解开关

[English](README.en.md) · [更新记录](CHANGELOG.md) · [验证范围](VALIDATION.md)

给 AI 加上“遇到困难，主动找成熟工具并验证”的持久偏好，并提供可开关的、由程序执行的搜索前置步骤。

**v0.1.0，MIT 许可证。Python 3.11+，无第三方运行依赖。**

## 能保证什么

| 使用方式 | 开启时 | 关闭时 | 执行边界 |
| --- | --- | --- | --- |
| 原 Codex / Claude Code 客户端 | 加载全局工作规则，要求适时寻找更好的方法 | 移除 BetterWay 自己管理的规则块 | 提示词不能保证模型服从，也不能保证每次搜索 |
| `betterway run` / 图形任务入口 | 程序先发起搜索，取得有效来源后才调用 AI；否则报错停止 | 不搜索、不追加 BetterWay 提示，直接调用客户端或 API | 只保证经过该入口的本次任务先完成搜索 |
| DeepSeek API | 使用同一个程序搜索步骤，再将来源交给模型 | 直接调用 DeepSeek Chat Completions | 需要用户自己的 API 密钥及额度 |
| DeepSeek / Claude / ChatGPT 官方网页聊天 | 暂不支持接管 | 不影响网页自身行为 | 本地文件无法自动改变远程网站的规则 |

**不存在“安装后控制电脑上所有 AI、百分之百服从规则”的功能。** 本项目保证的是受控入口的执行顺序：搜索没有有效结果就不调用模型。网络可用性、来源相关性、模型是否正确采用资料和任务最终质量，仍然需要验证。

Claude 的全局规则适配对象是 **Claude Code**。DeepSeek 模型在 Codex / Claude Code 内运行时，采用对应宿主的全局指令；本工具不改模型路由或账户配置。

## 下载安装

下载源码 ZIP 并解压，先安装 Python 3.11 或更新版本（Windows 安装器勾选 pip 和 tkinter）。

Windows PowerShell，在项目目录执行：

```powershell
python -m pip install .
python -m betterway install
python -m betterway ui
```

也可以执行 `install.ps1` 安装，然后双击 `run-ui.cmd`。若系统不允许执行 PowerShell 脚本，直接使用上面三条命令，无需降低系统执行策略。源码目录里的 `run-ui.pyw` 也可由带 tkinter 的 Python 打开。

如果终端提示找不到 `betterway` 命令，将后面的所有 `betterway ...` 换为 `python -m betterway ...`，并确保使用安装时的同一个 Python。无需修改系统 PATH。

macOS / Linux：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/betterway install
.venv/bin/betterway ui
```

Linux 图形界面可能需要由系统包管理器安装 `python3-tk`；无图形环境时使用 CLI。首次 pip 安装可能需要下载构建工具 setuptools，本程序运行时只使用 Python 标准库。无需管理员权限；不安装或替换 AI 官方客户端。

## 开关

```sh
betterway on
betterway off
betterway status
betterway uninstall
```

- `install` 和首次 `on` 默认将规则安装到 Codex 和 Claude Code 的用户目录。只安装 Codex 规则：`betterway install --target codex`。
- 开关状态在同一 BetterWay 配置目录中共享，跨聊天和项目保留。原客户端一般需要新开会话才能加载文件变化；关闭不能清除已进入旧聊天上下文的文字。
- 关闭和卸载仅移除本工具管理的规则。你原有的其他指令、客户端本身的搜索行为和权限保持其自身设置。
- 开关按每次任务开始时的状态决定；切换不能撤回已发出的搜索，也不会中断已经运行的任务。
- 本工具不会修改 PATH、创建系统服务、绕过 sandbox 或取消权限确认。

## 使用程序控制的搜索步骤

先安装并登录官方 Codex CLI 或 Claude Code CLI，再运行：

```sh
betterway run codex --prompt "给当前项目选择适合的 PDF 提取方案" --query "pdf extraction python"
betterway run claude --prompt "比较两个可行方案后实现并验证" --query "pdf extraction python"
betterway run deepseek --prompt "比较可用的开源方案，说明依据" --query "pdf extraction python"
```

可用 `--cwd` 选择工作目录、`--model` 选择模型、`--prompt-file` 读取 UTF-8 任务文件。`--prompt -` 从标准输入读取。模型生成的代码由原客户端的权限机制管理，本工具本身不下载和执行搜索结果里的代码。DeepSeek API 入口目前只返回文本，不提供文件编辑或代理式多轮工具执行。

开启时，**每次经过此入口的任务都会搜索**，无需等待模型承认自己遇到困难。这样才能在程序层面保证先后顺序；自动、准确地判断“模型现在解决不了”不是本版本能保证的能力。

`--query` 是发送给搜索服务的关键词。省略时使用任务开头最多 180 个字符（DeepSeek 搜索最多 128）；不会扫描项目文件。对私有任务，建议手动填写不含敏感信息的关键词。关键词自动截取不是语义改写，GitHub 工具检索通常使用简短英文词效果更好。输入不当或无结果会明确停止，不会暗中切换搜索来源或关闭开关。

## 搜索来源

默认 **GitHub 公共仓库搜索**，适合寻找开源工具，无需 API 密钥，但有公共接口速率限制。它不是通用网页搜索，也不代表已验证仓库的许可证或代码安全。

```sh
betterway provider github
betterway search "pdf extraction python"
```

通用网页搜索可选择 Brave 或 DeepSeek。用户自行开通服务并承担其费用；本项目不提供密钥、不购买额度、不包含隐藏收费或自动降级：

```powershell
# PowerShell：仅当前终端的示例；请使用你自己的密钥
$env:BRAVE_API_KEY = 'your-own-key'
betterway provider brave

$env:DEEPSEEK_API_KEY = 'your-own-key'
betterway provider deepseek
betterway run deepseek --prompt '比较可行方案' --query 'pdf extraction'
```

macOS / Linux 使用 `export BRAVE_API_KEY='your-own-key'` 等。双击图形界面会继承启动进程的环境变量；在终端设置密钥后从该终端运行 `betterway ui` 最直接。

可选 `BETTERWAY_GITHUB_TOKEN` 用于 GitHub 请求。密钥只从环境变量读取，不保存到项目或配置文件。不要提交 `.env` 或含密钥的脚本。

## 全局文件、备份和恢复

- Codex：`$CODEX_HOME/AGENTS.md`，默认 `~/.codex/AGENTS.md`。若存在非空 `AGENTS.override.md`，写入实际生效的 override 文件。
- Claude Code：`$CLAUDE_CONFIG_DIR/CLAUDE.md`，默认 `~/.claude/CLAUDE.md`。
- BetterWay：`$BETTERWAY_HOME/state.json`，默认 `~/.betterway/state.json`。
- 原文件快照：`~/.betterway/backups/<时间-随机编号>/`；manifest 记录路径及原先是否存在。
- 搜索证据：`~/.betterway/evidence/`，记录时间、来源链接、查询哈希和下游退出码，不记录任务正文、查询原文、搜索摘要、模型答复或密钥。来源 URL 仍可能包含服务返回的查询参数，请按本地资料管理。

仅管理 `<!-- betterway:begin:v1 -->` 到 `<!-- betterway:end:v1 -->` 之间的内容。正常开关保留原文件字节、换行和用户追加的文字；损坏标记会阻止修改。多文件写入失败时尝试回滚，并保留快照。断电或磁盘彻底不可写时不能保证事务完成，请根据 manifest 手动恢复。

`status` 会检查托管规则是否存在、内容是否改变、Codex override 是否让原路径失效。项目规则、企业设置、上下文大小限制仍可能影响加载或执行；本项目不能越过它们。

`install --migrate-legacy` 是可选迁移：仅当 Codex 全局文件**完整匹配**仓库内的 `legacy-policy.md` 时，将此前的单独规则替换为受开关管理的版本。迁移前备份；关闭时移除这份已接管的旧规则。其他用户内容不自动认领，不进行模糊匹配。需要恢复迁移前文件时使用快照。

## 开发和验证

```sh
python -m unittest discover -s tests -v
python -m betterway --help
python -m tools.make_release
```

自动测试使用临时目录和模拟 API，不读取真实账户，不调用付费模型。覆盖原文件保留、开关幂等、override 优先级、迁移备份、写入回滚、无效搜索拒绝、搜索失败不调用模型、搜索先于真实子进程运行、关闭后传递原任务、DeepSeek API 适配和 CLI 进程集成。

可选联网自检：`python -m tools.smoke_search_gate`。它发起一次真实的公共 GitHub 搜索，再把结果交给测试子进程，绝不启动真实 AI 客户端，也不修改全局指令；需要网络且可能受 GitHub 公共接口限流影响。

Windows 已做本地验证；CI 配置会在 Windows、macOS 和 Linux 上执行无网络测试。跨平台通过情况应以实际 CI 结果为准。

具体已验证范围见 [VALIDATION.md](VALIDATION.md)。源码打包脚本使用显式文件清单，不打包用户配置和本地证据；wheel 可用 `python -m pip wheel --no-deps . --wheel-dir dist` 构建。

## 为什么没有只用现成同步器

评估了 [rulesync](https://github.com/dyoshikawa/rulesync) 和 [Ruler](https://github.com/intellectronica/ruler)。它们适合维护多客户端规则；本项目的主要额外需求是关闭后恢复、图形开关，以及在调用模型前执行搜索并在失败时停止。因此首版使用标准库实现小型适配层，没有复制这些项目的代码。后续需要大量客户端支持时，可以集成成熟同步器。

## 接口依据

- [Codex 全局指令加载](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Claude Code 的 CLAUDE.md](https://code.claude.com/docs/en/memory) 与 [CLI](https://code.claude.com/docs/en/cli-reference)
- [GitHub 搜索 API](https://docs.github.com/en/rest/search/search#search-repositories)
- [Brave 搜索 API](https://api-dashboard.search.brave.com/app/documentation/web-search)
- [DeepSeek 搜索](https://api-docs.deepseek.com/guides/search/) 与 [Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/)

## 许可证与贡献

本项目采用 [MIT 许可证](LICENSE)，允许商业使用、修改和分发；欢迎提交客户端适配和缺陷修复，开发约定见 [CONTRIBUTING.md](CONTRIBUTING.md)。

发布者请只上传源码、文档、测试和构建后的发布包。不要上传用户的 `.betterway`、全局配置、快照、密钥或本地证据。
