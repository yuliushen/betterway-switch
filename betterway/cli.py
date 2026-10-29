import argparse
import json
from pathlib import Path
import sys

from . import BetterWayError, __version__
from .manager import Manager
from .runner import execute
from .search import gated_search
from .storage import Store


def show_status(status: dict) -> None:
    print("BetterWay��" + ("����" if status["enabled"] else "�ر�"))
    print("������Դ��" + status["provider"])
    print("����Ŀ¼��" + status["home"])
    for name, value in status["targets"].items():
        print(f"{name}: {value['path']} ({'һ��' if value['matches'] else '��Ҫ��飺·��������ѱ䶯'})")
    print("ȫ�ֹ��������»Ự������������ֻ������ betterway run / ͼ��������ڡ�")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="BetterWay ���Ž⿪�أ�ȫ�ֹ��� + ��������ִ��")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="action", required=True)
    install = sub.add_parser("install", help="��װ������ȫ�ֹ����Զ����ݣ�")
    install.add_argument("--target", action="append", choices=["codex", "claude"], help="Ĭ��ͬʱ���� Codex �� Claude Code")
    install.add_argument("--migrate-legacy", action="store_true", help="����ȫƥ��ľɰ�������뿪�ع������ȱ��ݣ�")
    sub.add_parser("on", help="�������״�ʹ�ûᰲװ�����ͻ��˵�ȫ�ֹ���")
    sub.add_parser("off", help="�Ƴ��йܹ���ֹͣ�����ߵ���������")
    sub.add_parser("uninstall", help="�Ƴ��йܹ���ȡ���ͻ���ע�᣻��������")
    status = sub.add_parser("status", help="���ʵ���ļ��Ϳ���״̬")
    status.add_argument("--json", action="store_true")
    provider = sub.add_parser("provider", help="ѡ��������Դ����Կ�ӻ���������ȡ")
    provider.add_argument("name", choices=["github", "brave", "deepseek"])
    search_cmd = sub.add_parser("search", help="��ʽ������������ʹ���عرգ�Ҳ�ᰴ�˴�����������")
    search_cmd.add_argument("query")
    search_cmd.add_argument("--provider", choices=["github", "brave", "deepseek"])
    run = sub.add_parser("run", help="�ܿ��ؿ��Ƶ���������ִ�����")
    run.add_argument("agent", choices=["codex", "claude", "deepseek"])
    prompts = run.add_mutually_exclusive_group(required=True)
    prompts.add_argument("--prompt", help="����ʹ�� - �ӱ�׼�����ȡ")
    prompts.add_argument("--prompt-file", type=Path, help="UTF-8 �����ļ�")
    run.add_argument("--query", help="���͸���������Ĺؼ��ʣ�ʡ��ʱʹ������ͷ��� 180 �ַ�")
    run.add_argument("--cwd", help="�ͻ��˵Ĺ���Ŀ¼")
    run.add_argument("--model", help="��ѡģ�����ƣ�Ĭ�����ÿͻ�������")
    sub.add_parser("ui", help="��ͼ�ο��غ��������")
    args = parser.parse_args(argv)
    try:
        store = Store()
        manager = Manager(store)
        if args.action == "install":
            show_status(manager.switch(True, args.target, args.migrate_legacy))
        elif args.action in {"on", "off"}:
            show_status(manager.switch(args.action == "on"))
        elif args.action == "uninstall":
            show_status(manager.uninstall())
        elif args.action == "status":
            value = manager.status()
            print(json.dumps(value, ensure_ascii=False, indent=2)) if args.json else show_status(value)
        elif args.action == "provider":
            manager.provider(args.name)
            show_status(manager.status())
        elif args.action == "search":
            packet, identity = gated_search(store, args.query, args.provider or store.load()["provider"])
            print(json.dumps({"evidence_id": identity, **packet}, ensure_ascii=False, indent=2))
        elif args.action == "run":
            prompt = args.prompt_file.read_text(encoding="utf-8-sig") if args.prompt_file else sys.stdin.read() if args.prompt == "-" else args.prompt
            code, output = execute(args.agent, prompt, args.query, args.cwd, args.model, store)
            if output:
                print(output)
            return code
        elif args.action == "ui":
            from .gui import main as gui_main
            gui_main()
        return 0
    except (BetterWayError, OSError, UnicodeError) as exc:
        print(f"BetterWay��{exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("BetterWay����ȡ����", file=sys.stderr)
        return 130
