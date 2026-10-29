# BetterWay

[����](README.md) �� [Changelog](CHANGELOG.md) �� [Validation](VALIDATION.md)

A reversible research-first switch for Codex, Claude Code, and the DeepSeek API. Help agents look for better tools when their current approach stalls, and provide an explicit search-before-run entry point.

Python 3.11+. No third-party runtime dependencies. MIT licensed.

## Two distinct mechanisms

| Mechanism | What it does | Boundary |
| --- | --- | --- |
| Global instructions | Adds a managed instruction block to the user's Codex / Claude Code configuration | Instructions influence behavior; they do not enforce model compliance |
| Task launcher | Runs a real search before invoking the selected client or API when enabled | No valid search results means no downstream model call |

Turning the switch off removes only BetterWay's managed blocks and stops its launcher from adding research instructions or making search requests. Other user instructions and the client's own search behavior remain in effect. Start a new client conversation to pick up instruction changes.

This project does not control every AI application on a computer, modify official web chat products, guarantee successful searches, or guarantee that an AI will use the best solution. The DeepSeek API adapter returns text; it is not a file-editing agent.

## Install

From the downloaded and extracted source directory:

```sh
python -m pip install .
python -m betterway install
python -m betterway ui
```

On macOS / Linux, use a virtual environment where required. The graphical interface uses tkinter, which may need a separate system package on Linux. Windows users can also open `run-ui.cmd` or `run-ui.pyw` from the source directory. No administrator access is required.

Install only one rule adapter with `python -m betterway install --target codex` or `--target claude`. The default installs both adapters. The corresponding official AI clients must be installed and authenticated separately; BetterWay does not install them or change their model providers.

## Use the switch

```sh
python -m betterway on
python -m betterway off
python -m betterway status
python -m betterway uninstall
```

The enabled state is shared across projects in the same BetterWay configuration environment. A running task uses the state it read when it started. Switching off cannot cancel a request already sent or remove instructions from an existing model context.

## Search before running a task

```sh
python -m betterway run codex --prompt "Compare PDF extraction tools for this project" --query "pdf extraction python"
python -m betterway run claude --prompt "Compare tools and implement a suitable approach" --query "pdf extraction python"
python -m betterway run deepseek --prompt "Compare suitable tools with sources" --query "pdf extraction python"
```

Use `--cwd` to select a project directory, `--model` to select a model, and `--prompt-file` to read a UTF-8 task file. With the switch enabled, every task through this launcher searches first. In the original client, the global instructions instead ask the model to search when needed; that behavior cannot be guaranteed.

The `--query` value is sent to the selected search provider. If omitted, BetterWay uses the beginning of the task, up to 180 characters (128 for DeepSeek Search). It does not scan project files. Supply non-sensitive keywords explicitly for private tasks. Queries are truncated, not semantically rewritten, and can produce irrelevant or empty results.

## Providers

The default provider searches public **GitHub repositories**, useful for finding tools. It is not general web search and is subject to GitHub rate limits. Optionally set `BETTERWAY_GITHUB_TOKEN` for authenticated requests.

```sh
python -m betterway provider github
python -m betterway search "pdf extraction python"
```

For general web search, select `brave` or `deepseek`. Set `BRAVE_API_KEY` or `DEEPSEEK_API_KEY` in the launching process's environment. The DeepSeek model adapter also requires `DEEPSEEK_API_KEY`. Users supply their own accounts, keys, and service credits; provider charges are separate from this project.

No automatic provider switching, paid account creation, or execution of code found in search results is performed.

## Local files

- Codex instructions: `$CODEX_HOME/AGENTS.md`, defaulting to `~/.codex/AGENTS.md`. A non-empty `AGENTS.override.md` takes precedence.
- Claude Code instructions: `$CLAUDE_CONFIG_DIR/CLAUDE.md`, defaulting to `~/.claude/CLAUDE.md`.
- BetterWay state: `$BETTERWAY_HOME/state.json`, defaulting to `~/.betterway/state.json`.
- Snapshots and evidence: `backups/` and `evidence/` inside BetterWay's home.

Only the block between BetterWay's markers is managed. Existing content is preserved, writes are backed up, malformed markers are rejected, and failed multi-file updates attempt rollback. A power failure or unwritable disk may still require manual snapshot recovery.

Evidence records contain timestamps, query hashes, source URLs, and downstream exit codes. They do not contain API keys, raw queries, task bodies, snippets, or model responses. Returned source URLs can themselves contain query parameters. Keys are read only from environment variables.

The optional `install --migrate-legacy` migrates a previous standalone Codex rule only when the entire file exactly matches the bundled `legacy-policy.md`. It is backed up first. No unrelated instructions are adopted through fuzzy matching.

## Development

```sh
python -m unittest discover -s tests -v
python -m tools.make_release
```

Optional live smoke test: `python -m tools.smoke_search_gate`. It uses a real GitHub search and a test subprocess, never an actual AI client. See [VALIDATION.md](VALIDATION.md) for the actual scope of testing and limitations.

Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under [MIT](LICENSE).
