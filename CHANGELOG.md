# Changelog

## 0.1.0 — 2026-10-29

Initial public release.

- Reversible, backed-up global instruction adapters for Codex and Claude Code.
- Shared on/off switch with a local tkinter interface and command-line controls.
- Search-before-run launcher for Codex CLI, Claude Code CLI, and DeepSeek Chat Completions.
- GitHub repository search, Brave web search, and DeepSeek Search adapters.
- Search evidence records without raw task bodies, queries, model replies, or credentials.
- Exact-match migration for a previous standalone policy.
- Regression coverage for file preservation, rollback, adapter behavior, and gate ordering.
- Chinese and English documentation, source ZIP, wheel, and SHA-256 checksums.

### Scope

Global instructions guide behavior; they do not enforce compliance. Program-controlled search ordering applies only to BetterWay's launcher when enabled. Official web chat products are not intercepted. GitHub search can be rate limited; other providers require user-supplied credentials and may charge fees. See `VALIDATION.md` for what has and has not been tested.
