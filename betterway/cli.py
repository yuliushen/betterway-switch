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
    print("BetterWay：" + ("开启" if status["enabled"] else "关闭"))
    print("搜索来源：" + status["provider"])
    print("配置目录：" + status["home"])
    for name, value in status["targets"].items():
        print(f"{name}: {value['path']} ({'一致' if value['matches'] else '需要检查：路径或规则已变动'})")
    print("全局规则用于新会话；程序级先搜索只适用于 betterway run / 图形任务入口。")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="BetterWay 更优解开关：全局规则 + 先搜索再执行")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="action", required=True)
    install = sub.add_parser("install", help="安装并开启全局规则（自动备份）")
    install.add_argument("--target", action="append", choices=["codex", "claude"], help="默认同时适配 Codex 和 Claude Code")
    install.add_argument("--migrate-legacy", action="store_true", help="将完全匹配的旧版规则纳入开关管理（先备份）")
    sub.add_parser("on", help="开启；首次使用会安装两个客户端的全局规则")
    sub.add_parser("off", help="移除托管规则，停止本工具的搜索步骤")
    sub.add_parser("uninstall", help="移除托管规则并取消客户端注册；保留备份")
    status = sub.add_parser("status", help="检查实际文件和开关状态")
    status.add_argument("--json", action="store_true")
    provider = sub.add_parser("provider", help="选择搜索来源；密钥从环境变量读取")
    provider.add_argument("name", choices=["github", "brave", "deepseek"])
    search_cmd = sub.add_parser("search", help="显式测试搜索（即使开关关闭，也会按此次命令搜索）")
    search_cmd.add_argument("query")
    search_cmd.add_argument("--provider", choices=["github", "brave", "deepseek"])
    run = sub.add_parser("run", help="受开关控制的先搜索再执行入口")
    run.add_argument("agent", choices=["codex", "claude", "deepseek"])
    prompts = run.add_mutually_exclusive_group(required=True)
    prompts.add_argument("--prompt", help="任务；使用 - 从标准输入读取")
    prompts.add_argument("--prompt-file", type=Path, help="UTF-8 任务文件")
    run.add_argument("--query", help="发送给搜索服务的关键词；省略时使用任务开头，最长 180 字符")
    run.add_argument("--cwd", help="客户端的工作目录")
    run.add_argument("--model", help="可选模型名称，默认沿用客户端配置")
    sub.add_parser("ui", help="打开图形开关和任务入口")
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
        print(f"BetterWay：{exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("BetterWay：已取消。", file=sys.stderr)
        return 130
