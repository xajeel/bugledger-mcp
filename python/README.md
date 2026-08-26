# Bug Ledger MCP

**Never fix the same bug twice.** A local-first MCP server that gives AI coding agents a permanent memory of fixed bugs — record a bug at fix time, and every future session checks the ledger before writing code.

## How it works

- `/logbug` — record a fixed bug (symptom, root cause, feature area, fix diff) into a local SQLite ledger at `~/.bugledger/`
- `get_patterns` — the agent pulls past bugs for the area it's about to touch, *before* coding
- `search_bugs` — full-text search over the ledger
- `get_guardrails` — Semgrep rules for recurring patterns, wired into CI

Everything runs locally. No login, no cloud, nothing leaves your machine.

## Install

```sh
claude mcp add bugledger -- uvx bugledger-mcp
```

## License

MIT
