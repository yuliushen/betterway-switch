"""One live GitHub search followed by a real test child, never an AI client."""

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

from betterway import BetterWayError
from betterway.runner import execute
from betterway.storage import Store


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="pdf extraction python")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        store = Store(root / "state")
        store.save({"version": 1, "enabled": True, "provider": "github", "targets": {}})
        stub = root / "test_child.py"
        stub.write_text("import sys\nsys.stdin.reconfigure(encoding='utf-8')\ntext=sys.stdin.read()\nassert 'https://github.com/' in text\nprint('SEARCH_CONTEXT_RECEIVED')\n", encoding="utf-8")
        child_started = False
        real_run = subprocess.run

        def launch(*values, **kwargs):
            nonlocal child_started
            child_started = True
            return real_run(*values, **kwargs)

        try:
            with patch("betterway.runner.command_for", return_value=[sys.executable, str(stub)]), patch("betterway.runner.subprocess.run", side_effect=launch):
                code, output = execute("codex", "Compare available PDF extraction tools using the supplied references.", args.query, store=store, capture=True)
        except BetterWayError as exc:
            assert not child_started, "Search failure must not launch a child."
            print(f"STOPPED: {exc}\nConfirmed: test child was not launched. Live success path was not validated.", file=sys.stderr)
            return 2
        if code != 0 or "SEARCH_CONTEXT_RECEIVED" not in output:
            raise RuntimeError("The search gate smoke test failed.")
        print("PASS: live GitHub search -> reference context -> real test child. No AI model called.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
