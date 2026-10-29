import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from betterway import BetterWayError
from betterway.cli import main
from betterway.manager import Manager, START, END, block
from betterway.runner import execute, prepare
from betterway.search import search, clean_result, gated_search, request_json
from betterway.storage import Store


class Isolated(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {
            "BETTERWAY_HOME": str(self.root / "state"),
            "CODEX_HOME": str(self.root / "codex"),
            "CLAUDE_CONFIG_DIR": str(self.root / "claude"),
        })
        self.env.start()
        self.store = Store()
        self.manager = Manager(self.store)
        self.codex = self.root / "codex" / "AGENTS.md"
        self.claude = self.root / "claude" / "CLAUDE.md"

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def put(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


class ManagerTests(Isolated):
    def test_roundtrip_preserves_existing_bytes(self):
        original = "\ufeff# �û�ԭ�й���\r\n���ָ�ʽ\r\n".encode("utf-8")
        self.put(self.codex, original)
        self.manager.switch(True)
        self.assertIn(original, self.codex.read_bytes())
        self.manager.switch(False)
        self.assertEqual(self.codex.read_bytes(), original)
        self.assertFalse(self.claude.exists())

    def test_no_trailing_newline_roundtrip(self):
        self.put(self.codex, b"keep original")
        self.manager.switch(True)
        self.manager.switch(False)
        self.assertEqual(self.codex.read_bytes(), b"keep original")

    def test_repeated_on_off_is_idempotent(self):
        self.manager.switch(True)
        first = self.codex.read_bytes()
        self.manager.switch(True)
        self.assertEqual(first, self.codex.read_bytes())
        self.assertEqual(first.count(START), 1)
        self.manager.switch(False)
        self.manager.switch(False)
        self.assertFalse(self.codex.exists())

    def test_user_additions_survive_switch_off(self):
        self.put(self.codex, b"initial")
        self.manager.switch(True)
        self.codex.write_bytes(self.codex.read_bytes() + b"\nnew user rule")
        self.manager.switch(False)
        self.assertEqual(self.codex.read_bytes(), b"initial\nnew user rule")

    def test_foreign_prefix_edit_survives(self):
        self.put(self.codex, b"old")
        self.manager.switch(True)
        self.codex.write_bytes(self.codex.read_bytes().replace(b"old", b"new", 1))
        self.manager.switch(False)
        self.assertIn(b"new", self.codex.read_bytes())
        self.assertNotIn(START, self.codex.read_bytes())

    def test_nonempty_codex_override_selected(self):
        override = self.root / "codex" / "AGENTS.override.md"
        self.put(override, b"override")
        self.put(self.codex, b"base")
        self.manager.switch(True, ["codex"])
        self.assertIn(START, override.read_bytes())
        self.assertEqual(self.codex.read_bytes(), b"base")
        self.manager.switch(False)
        self.assertEqual(override.read_bytes(), b"override")

    def test_later_override_detected(self):
        self.manager.switch(True, ["codex"])
        override = self.root / "codex" / "AGENTS.override.md"
        self.put(override, b"new override")
        self.assertFalse(self.manager.status()["targets"]["codex"]["matches"])
        with self.assertRaises(BetterWayError):
            self.manager.switch(True)
        self.manager.switch(False)
        self.assertEqual(override.read_bytes(), b"new override")

    def test_malformed_marker_no_partial_write(self):
        self.put(self.claude, START + b"missing end")
        with self.assertRaises(BetterWayError):
            self.manager.switch(True)
        self.assertFalse(self.codex.exists())
        self.assertEqual(self.claude.read_bytes(), START + b"missing end")

    def test_duplicate_markers_refused(self):
        self.put(self.codex, block() + block())
        with self.assertRaises(BetterWayError):
            self.manager.switch(True)

    def test_write_error_rolls_back_all_targets(self):
        self.put(self.codex, b"original")
        with patch.object(self.store, "save", side_effect=OSError("disk problem")):
            with self.assertRaises(BetterWayError):
                self.manager.switch(True)
        self.assertEqual(self.codex.read_bytes(), b"original")
        self.assertFalse(self.claude.exists())
        self.assertFalse(self.store.path.exists())

    def test_legacy_migration_backed_up_and_switchable(self):
        legacy = Path(__file__).resolve().parents[1] / "betterway" / "legacy-policy.md"
        original = legacy.read_bytes()
        self.put(self.codex, original)
        self.manager.switch(True, ["codex"], migrate_legacy=True)
        self.assertTrue(self.codex.read_bytes().startswith(START))
        snapshots = list((self.store.root / "backups").rglob("*.bin"))
        self.assertTrue(any(path.read_bytes() == original for path in snapshots))
        self.manager.switch(False)
        self.assertFalse(self.codex.exists())

    def test_legacy_with_other_user_text_not_adopted(self):
        self.put(self.codex, b"another policy")
        self.manager.switch(True, ["codex"], migrate_legacy=True)
        self.manager.switch(False)
        self.assertEqual(self.codex.read_bytes(), b"another policy")

    def test_uninstall_keeps_unrelated_rules_and_backups(self):
        self.put(self.claude, b"personal")
        self.manager.switch(True)
        self.manager.uninstall()
        self.assertEqual(self.claude.read_bytes(), b"personal")
        self.assertEqual(self.store.load()["targets"], {})
        self.assertTrue((self.store.root / "backups").exists())

    def test_corrupt_state_fails_closed(self):
        self.put(self.store.path, b'{"enabled": false}')
        with self.assertRaises(BetterWayError):
            self.store.load()
        with patch("betterway.runner.subprocess.run") as child:
            with self.assertRaises(BetterWayError):
                prepare(self.store, "task")
            child.assert_not_called()

    def test_lock_blocks_concurrent_mutation(self):
        with self.store.lock():
            with self.assertRaises(BetterWayError):
                self.manager.switch(True)
        self.assertFalse(self.codex.exists())

    def test_drift_detected(self):
        self.manager.switch(True, ["codex"])
        self.codex.write_bytes(self.codex.read_bytes().replace(b"BetterWay", b"EditedWay", 1))
        self.assertFalse(self.manager.status()["targets"]["codex"]["matches"])

    def test_add_target_reenables_all_registered_targets(self):
        self.manager.switch(True, ["codex"])
        self.manager.switch(False)
        self.manager.switch(True, ["claude"])
        self.assertTrue(all(t["matches"] for t in self.manager.status()["targets"].values()))


class SearchTests(Isolated):
    def test_rate_limit_error_does_not_expose_request_secret(self):
        error = HTTPError("https://api.github.com/search?secret=do-not-print", 403, "rate limit exceeded", {}, None)
        with patch("betterway.search.build_opener") as opener:
            opener.return_value.open.side_effect = error
            with self.assertRaises(BetterWayError) as raised:
                request_json("https://api.github.com/search/repositories?q=pdf")
        self.assertNotIn("do-not-print", str(raised.exception))
        self.assertIn("BETTERWAY_GITHUB_TOKEN", str(raised.exception))

    def test_github_normalization_and_provenance(self):
        response = {"items": [{"full_name": "org/tool", "html_url": "https://github.com/org/tool", "description": "useful", "license": {"spdx_id": "MIT"}}]}
        with patch("betterway.search.request_json", return_value=response) as http:
            packet, identity = gated_search(self.store, "pdf extraction", "github")
        self.assertIn("api.github.com/search/repositories", http.call_args.args[0])
        self.assertEqual(packet["results"][0]["url"], "https://github.com/org/tool")
        evidence = (self.store.root / "evidence" / (identity + ".json")).read_text(encoding="utf-8")
        self.assertNotIn("pdf extraction", evidence)
        self.assertIn("search_succeeded", evidence)

    def test_empty_and_incomplete_results_rejected(self):
        for data in ({"items": []}, {"items": [], "incomplete_results": True}, {"message": "error"}):
            with patch("betterway.search.request_json", return_value=data):
                with self.assertRaises(BetterWayError):
                    search("pdf")

    def test_untrusted_url_never_counts_as_source(self):
        for url in ("javascript:alert(1)", "file:///etc/passwd", "https://user:secret@example.com/", "https://", "https://[broken"):
            self.assertIsNone(clean_result("title", url, "text"))

    def test_missing_search_key_stops_before_network(self):
        with patch.dict(os.environ, {"BRAVE_API_KEY": ""}), patch("betterway.search.request_json") as http:
            with self.assertRaises(BetterWayError):
                search("question", "brave")
            http.assert_not_called()

    def test_deepseek_search_adapter(self):
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}), patch("betterway.search.request_json", return_value={"results": [{"title": "docs", "url": "https://example.org/", "summary": "text"}]}) as http:
            packet = search("pdf", "deepseek")
        self.assertEqual(packet["provider"], "deepseek")
        self.assertEqual(http.call_args.args[2]["query"], "pdf")

    def test_invalid_query_no_network(self):
        for query in ("", " " * 5, "a" * 201):
            with patch("betterway.search.request_json") as http:
                with self.assertRaises(BetterWayError):
                    search(query)
                http.assert_not_called()


class GateTests(Isolated):
    def packet(self):
        return {"provider": "github", "query": "pdf", "results": [{"title": "Source", "url": "https://example.org/", "snippet": "reference"}]}

    def test_enabled_search_precedes_actual_child_process(self):
        self.manager.switch(True, ["codex"])
        output_file = self.root / "received.txt"
        child_script = self.root / "child.py"
        child_script.write_text("import sys\nfrom pathlib import Path\nsys.stdin.reconfigure(encoding='utf-8')\nPath(sys.argv[1]).write_text(sys.stdin.read(), encoding='utf-8')\n", encoding="utf-8")
        events = []

        def searched(*args):
            self.assertFalse(output_file.exists())
            events.append("searched")
            return self.packet(), "evidence-id"

        with patch("betterway.runner.command_for", return_value=[sys.executable, str(child_script), str(output_file)]), patch("betterway.runner.gated_search", side_effect=searched):
            code, _ = execute("codex", "task with `literal` & $(text)", "pdf", store=self.store, capture=True)
        self.assertEqual(code, 0)
        self.assertEqual(events, ["searched"])
        received = output_file.read_text(encoding="utf-8")
        self.assertIn("evidence-id", received)
        self.assertIn("task with `literal` & $(text)", received)

    def test_search_failure_never_launches_model(self):
        self.manager.switch(True, ["codex"])
        with patch("betterway.runner.command_for", return_value=["codex"]), patch("betterway.search.search", side_effect=BetterWayError("offline")), patch("betterway.runner.subprocess.run") as child:
            with self.assertRaises(BetterWayError):
                execute("codex", "task", "pdf", store=self.store)
            child.assert_not_called()
        events = [json.loads(p.read_text()) for p in (self.store.root / "evidence").glob("*.json")]
        self.assertEqual(events[0]["event"], "search_failed")

    def test_disabled_passes_original_prompt_with_no_search(self):
        prompt = "�û�ԭ��\n`quoted` & $(literal)"
        with patch("betterway.runner.command_for", return_value=["codex"]), patch("betterway.runner.gated_search") as gate, patch("betterway.runner.subprocess.run", return_value=subprocess.CompletedProcess([], 7)) as child:
            code, _ = execute("codex", prompt, store=self.store)
        gate.assert_not_called()
        self.assertEqual(child.call_args.kwargs["input"], prompt)
        self.assertFalse(child.call_args.kwargs["shell"])
        self.assertEqual(code, 7)

    def test_deepseek_uses_presearched_context(self):
        self.manager.switch(True, ["codex"])
        timeline = []

        def gate(*args):
            timeline.append("search")
            return self.packet(), "abc"

        def chat(*args, **kwargs):
            timeline.append("chat")
            self.assertIn("abc", args[2]["messages"][0]["content"])
            return {"choices": [{"message": {"content": "answer"}, "finish_reason": "stop"}]}

        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test"}), patch("betterway.runner.gated_search", side_effect=gate), patch("betterway.runner.request_json", side_effect=chat):
            self.assertEqual(execute("deepseek", "task", "pdf", store=self.store), (0, "answer"))
        self.assertEqual(timeline, ["search", "chat"])

    def test_deepseek_incomplete_answer_not_success(self):
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test"}), patch("betterway.runner.request_json", return_value={"choices": [{"message": {"content": "partial"}, "finish_reason": "length"}]}):
            with self.assertRaises(BetterWayError):
                execute("deepseek", "task", store=self.store)

    def test_cli_subprocess_install_off_status(self):
        project = Path(__file__).resolve().parents[1]
        for action in (["install", "--target", "codex"], ["off"]):
            result = subprocess.run([sys.executable, "-m", "betterway", *action], cwd=project, capture_output=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, "-m", "betterway", "status", "--json"], cwd=project, capture_output=True, encoding="utf-8")
        self.assertFalse(json.loads(result.stdout)["enabled"])
        self.assertFalse(self.codex.exists())

    def test_cli_invalid_state_nonzero(self):
        self.put(self.store.path, b"not json")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["status"]), 2)


if __name__ == "__main__":
    unittest.main()
