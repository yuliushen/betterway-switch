# BetterWay �� ���Ž⿪��

[English](README.en.md) �� [���¼�¼](CHANGELOG.md) �� [��֤��Χ](VALIDATION.md)

�� AI ���ϡ��������ѣ������ҳ��칤�߲���֤���ĳ־�ƫ�ã����ṩ�ɿ��صġ��ɳ���ִ�е�����ǰ�ò��衣

**v0.1.0��MIT ����֤��Python 3.11+���޵���������������**

## �ܱ�֤ʲô

| ʹ�÷�ʽ | ����ʱ | �ر�ʱ | ִ�б߽� |
| --- | --- | --- | --- |
| ԭ Codex / Claude Code �ͻ��� | ����ȫ�ֹ�������Ҫ����ʱѰ�Ҹ��õķ��� | �Ƴ� BetterWay �Լ������Ĺ���� | ��ʾ�ʲ��ܱ�֤ģ�ͷ��ӣ�Ҳ���ܱ�֤ÿ������ |
| `betterway run` / ͼ��������� | �����ȷ���������ȡ����Ч��Դ��ŵ��� AI�����򱨴�ֹͣ | ����������׷�� BetterWay ��ʾ��ֱ�ӵ��ÿͻ��˻� API | ֻ��֤��������ڵı���������������� |
| DeepSeek API | ʹ��ͬһ�������������裬�ٽ���Դ����ģ�� | ֱ�ӵ��� DeepSeek Chat Completions | ��Ҫ�û��Լ��� API ��Կ����� |
| DeepSeek / Claude / ChatGPT �ٷ���ҳ���� | �ݲ�֧�ֽӹ� | ��Ӱ����ҳ������Ϊ | �����ļ��޷��Զ��ı�Զ����վ�Ĺ��� |

**�����ڡ���װ����Ƶ��������� AI���ٷ�֮�ٷ��ӹ��򡱵Ĺ��ܡ�** ����Ŀ��֤�����ܿ���ڵ�ִ��˳������û����Ч����Ͳ�����ģ�͡���������ԡ���Դ����ԡ�ģ���Ƿ���ȷ�������Ϻ�����������������Ȼ��Ҫ��֤��

Claude ��ȫ�ֹ������������ **Claude Code**��DeepSeek ģ���� Codex / Claude Code ������ʱ�����ö�Ӧ������ȫ��ָ������߲���ģ��·�ɻ��˻����á�

## ���ذ�װ

����Դ�� ZIP ����ѹ���Ȱ�װ Python 3.11 ����°汾��Windows ��װ����ѡ pip �� tkinter����

Windows PowerShell������ĿĿ¼ִ�У�

```powershell
python -m pip install .
python -m betterway install
python -m betterway ui
```

Ҳ����ִ�� `install.ps1` ��װ��Ȼ��˫�� `run-ui.cmd`����ϵͳ������ִ�� PowerShell �ű���ֱ��ʹ����������������轵��ϵͳִ�в��ԡ�Դ��Ŀ¼��� `run-ui.pyw` Ҳ���ɴ� tkinter �� Python �򿪡�

����ն���ʾ�Ҳ��� `betterway` �������������� `betterway ...` ��Ϊ `python -m betterway ...`����ȷ��ʹ�ð�װʱ��ͬһ�� Python�������޸�ϵͳ PATH��

macOS / Linux��

```sh
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/betterway install
.venv/bin/betterway ui
```

Linux ͼ�ν��������Ҫ��ϵͳ����������װ `python3-tk`����ͼ�λ���ʱʹ�� CLI���״� pip ��װ������Ҫ���ع������� setuptools������������ʱֻʹ�� Python ��׼�⡣�������ԱȨ�ޣ�����װ���滻 AI �ٷ��ͻ��ˡ�

## ����

```sh
betterway on
betterway off
betterway status
betterway uninstall
```

- `install` ���״� `on` Ĭ�Ͻ�����װ�� Codex �� Claude Code ���û�Ŀ¼��ֻ��װ Codex ����`betterway install --target codex`��
- ����״̬��ͬһ BetterWay ����Ŀ¼�й��������������Ŀ������ԭ�ͻ���һ����Ҫ�¿��Ự���ܼ����ļ��仯���رղ�������ѽ�������������ĵ����֡�
- �رպ�ж�ؽ��Ƴ������߹����Ĺ�����ԭ�е�����ָ��ͻ��˱�����������Ϊ��Ȩ�ޱ������������á�
- ���ذ�ÿ������ʼʱ��״̬�������л����ܳ����ѷ�����������Ҳ�����ж��Ѿ����е�����
- �����߲����޸� PATH������ϵͳ�����ƹ� sandbox ��ȡ��Ȩ��ȷ�ϡ�

## ʹ�ó�����Ƶ���������

�Ȱ�װ����¼�ٷ� Codex CLI �� Claude Code CLI�������У�

```sh
betterway run codex --prompt "����ǰ��Ŀѡ���ʺϵ� PDF ��ȡ����" --query "pdf extraction python"
betterway run claude --prompt "�Ƚ��������з�����ʵ�ֲ���֤" --query "pdf extraction python"
betterway run deepseek --prompt "�ȽϿ��õĿ�Դ������˵������" --query "pdf extraction python"
```

���� `--cwd` ѡ����Ŀ¼��`--model` ѡ��ģ�͡�`--prompt-file` ��ȡ UTF-8 �����ļ���`--prompt -` �ӱ�׼�����ȡ��ģ�����ɵĴ�����ԭ�ͻ��˵�Ȩ�޻��ƹ����������߱��������غ�ִ�����������Ĵ��롣DeepSeek API ���Ŀǰֻ�����ı������ṩ�ļ��༭�����ʽ���ֹ���ִ�С�

����ʱ��**ÿ�ξ�������ڵ����񶼻�����**������ȴ�ģ�ͳ����Լ��������ѡ����������ڳ�����汣֤�Ⱥ�˳���Զ���׼ȷ���жϡ�ģ�����ڽ�����ˡ����Ǳ��汾�ܱ�֤��������

`--query` �Ƿ��͸���������Ĺؼ��ʡ�ʡ��ʱʹ������ͷ��� 180 ���ַ���DeepSeek ������� 128��������ɨ����Ŀ�ļ�����˽�����񣬽����ֶ���д����������Ϣ�Ĺؼ��ʡ��ؼ����Զ���ȡ���������д��GitHub ���߼���ͨ��ʹ�ü��Ӣ�Ĵ�Ч�����á����벻�����޽������ȷֹͣ�����ᰵ���л�������Դ��رտ��ء�

## ������Դ

Ĭ�� **GitHub �����ֿ�����**���ʺ�Ѱ�ҿ�Դ���ߣ����� API ��Կ�����й����ӿ��������ơ�������ͨ����ҳ������Ҳ����������֤�ֿ������֤����밲ȫ��

```sh
betterway provider github
betterway search "pdf extraction python"
```

ͨ����ҳ������ѡ�� Brave �� DeepSeek���û����п�ͨ���񲢳е�����ã�����Ŀ���ṩ��Կ���������ȡ������������շѻ��Զ�������

```powershell
# PowerShell������ǰ�ն˵�ʾ������ʹ�����Լ�����Կ
$env:BRAVE_API_KEY = 'your-own-key'
betterway provider brave

$env:DEEPSEEK_API_KEY = 'your-own-key'
betterway provider deepseek
betterway run deepseek --prompt '�ȽϿ��з���' --query 'pdf extraction'
```

macOS / Linux ʹ�� `export BRAVE_API_KEY='your-own-key'` �ȡ�˫��ͼ�ν����̳��������̵Ļ������������ն�������Կ��Ӹ��ն����� `betterway ui` ��ֱ�ӡ�

��ѡ `BETTERWAY_GITHUB_TOKEN` ���� GitHub ������Կֻ�ӻ���������ȡ�������浽��Ŀ�������ļ�����Ҫ�ύ `.env` ����Կ�Ľű���

## ȫ���ļ������ݺͻָ�

- Codex��`$CODEX_HOME/AGENTS.md`��Ĭ�� `~/.codex/AGENTS.md`�������ڷǿ� `AGENTS.override.md`��д��ʵ����Ч�� override �ļ���
- Claude Code��`$CLAUDE_CONFIG_DIR/CLAUDE.md`��Ĭ�� `~/.claude/CLAUDE.md`��
- BetterWay��`$BETTERWAY_HOME/state.json`��Ĭ�� `~/.betterway/state.json`��
- ԭ�ļ����գ�`~/.betterway/backups/<ʱ��-������>/`��manifest ��¼·����ԭ���Ƿ���ڡ�
- ����֤�ݣ�`~/.betterway/evidence/`����¼ʱ�䡢��Դ���ӡ���ѯ��ϣ�������˳��룬����¼�������ġ���ѯԭ�ġ�����ժҪ��ģ�ʹ𸴻���Կ����Դ URL �Կ��ܰ������񷵻صĲ�ѯ�������밴�������Ϲ�����

������ `<!-- betterway:begin:v1 -->` �� `<!-- betterway:end:v1 -->` ֮������ݡ��������ر���ԭ�ļ��ֽڡ����к��û�׷�ӵ����֣��𻵱�ǻ���ֹ�޸ġ����ļ�д��ʧ��ʱ���Իع������������ա��ϵ����̳��ײ���дʱ���ܱ�֤������ɣ������ manifest �ֶ��ָ���

`status` �����йܹ����Ƿ���ڡ������Ƿ�ı䡢Codex override �Ƿ���ԭ·��ʧЧ����Ŀ������ҵ���á������Ĵ�С�����Կ���Ӱ����ػ�ִ�У�����Ŀ����Խ�����ǡ�

`install --migrate-legacy` �ǿ�ѡǨ�ƣ����� Codex ȫ���ļ�**����ƥ��**�ֿ��ڵ� `legacy-policy.md` ʱ������ǰ�ĵ��������滻Ϊ�ܿ��ع����İ汾��Ǩ��ǰ���ݣ��ر�ʱ�Ƴ�����ѽӹܵľɹ��������û����ݲ��Զ����죬������ģ��ƥ�䡣��Ҫ�ָ�Ǩ��ǰ�ļ�ʱʹ�ÿ��ա�

## ��������֤

```sh
python -m unittest discover -s tests -v
python -m betterway --help
python -m tools.make_release
```

�Զ�����ʹ����ʱĿ¼��ģ�� API������ȡ��ʵ�˻��������ø���ģ�͡�����ԭ�ļ������������ݵȡ�override ���ȼ���Ǩ�Ʊ��ݡ�д��ع�����Ч�����ܾ�������ʧ�ܲ�����ģ�͡�����������ʵ�ӽ������С��رպ󴫵�ԭ����DeepSeek API ����� CLI ���̼��ɡ�

��ѡ�����Լ죺`python -m tools.smoke_search_gate`��������һ����ʵ�Ĺ��� GitHub �������ٰѽ�����������ӽ��̣�����������ʵ AI �ͻ��ˣ�Ҳ���޸�ȫ��ָ���Ҫ�����ҿ����� GitHub �����ӿ�����Ӱ�졣

Windows ����������֤��CI ���û��� Windows��macOS �� Linux ��ִ����������ԡ���ƽ̨ͨ�����Ӧ��ʵ�� CI ���Ϊ׼��

��������֤��Χ�� [VALIDATION.md](VALIDATION.md)��Դ�����ű�ʹ����ʽ�ļ��嵥��������û����úͱ���֤�ݣ�wheel ���� `python -m pip wheel --no-deps . --wheel-dir dist` ������

## Ϊʲôû��ֻ���ֳ�ͬ����

������ [rulesync](https://github.com/dyoshikawa/rulesync) �� [Ruler](https://github.com/intellectronica/ruler)�������ʺ�ά����ͻ��˹��򣻱���Ŀ����Ҫ���������ǹرպ�ָ���ͼ�ο��أ��Լ��ڵ���ģ��ǰִ����������ʧ��ʱֹͣ������װ�ʹ�ñ�׼��ʵ��С������㣬û�и�����Щ��Ŀ�Ĵ��롣������Ҫ�����ͻ���֧��ʱ�����Լ��ɳ���ͬ������

## �ӿ�����

- [Codex ȫ��ָ�����](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Claude Code �� CLAUDE.md](https://code.claude.com/docs/en/memory) �� [CLI](https://code.claude.com/docs/en/cli-reference)
- [GitHub ���� API](https://docs.github.com/en/rest/search/search#search-repositories)
- [Brave ���� API](https://api-dashboard.search.brave.com/app/documentation/web-search)
- [DeepSeek ����](https://api-docs.deepseek.com/guides/search/) �� [Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/)

## ����֤�빱��

����Ŀ���� [MIT ����֤](LICENSE)��������ҵʹ�á��޸ĺͷַ�����ӭ�ύ�ͻ��������ȱ���޸�������Լ���� [CONTRIBUTING.md](CONTRIBUTING.md)��

��������ֻ�ϴ�Դ�롢�ĵ������Ժ͹�����ķ���������Ҫ�ϴ��û��� `.betterway`��ȫ�����á����ա���Կ�򱾵�֤�ݡ�
