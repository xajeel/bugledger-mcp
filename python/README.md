# Bug Ledger MCP

**Never fix the same bug twice.** A local-first MCP server that gives AI coding agents (Claude Code, Cursor, any MCP client) a permanent memory of fixed bugs. Record a bug at fix time; every future session checks the ledger before writing code.

Everything runs on your machine: one SQLite file in `~/.bugledger/`. No login, no cloud, no telemetry, no network calls.

## Install

Requires [uv](https://docs.astral.sh/uv/).

```sh
claude mcp add bugledger -- uvx bugledger-mcp
```

Restart Claude Code. The tools and the `/mcp__bugledger__logbug` prompt appear.

Cursor, or a whole team via a committed `.mcp.json` / `.cursor/mcp.json`:

```json
{ "mcpServers": { "bugledger": { "command": "uvx", "args": ["bugledger-mcp"] } } }
```

## Tools

| Tool | The agent calls it… | What it does |
|---|---|---|
| `get_patterns(feature_area, project)` | **before** planning or coding in an area | Newest past bugs for that area, one line each, capped at 30 lines |
| `search_bugs(query)` | while debugging | Full-text search over symptoms and root causes; paste the error as is |
| `record_bug(...)` | after a fix, once you confirm | Stores symptom, root cause, feature area, project, stack, severity, and the fix diff |
| `list_areas()` | before naming things | Existing feature areas and projects with counts |
| `resolve_bug(id, project)` | once a project has a guardrail | Hides that bug from `get_patterns` for that project only |
| `update_bug` / `delete_bug` | to correct mistakes | Edit or remove a record |
| `get_guardrails(stack)` | at project setup | Starter pack of Semgrep rules for classic AI-coding mistakes, plus the CI workflow |

**`/logbug`** is an MCP prompt: the agent checks the session really contained a bug fix, drafts the record, shows it to you, and calls `record_bug` only after you confirm.

The server sends standing instructions to the agent on connect, so it works without extra setup. To make it a hard rule, add to `CLAUDE.md` or `.cursorrules`:

```
Before implementing anything in a feature area, call bugledger get_patterns with that area and this project's name, and account for every returned bug. After fixing a bug, run /mcp__bugledger__logbug.
```

## Data and privacy

- Ledger: `~/.bugledger/ledger.db`. Override the folder with `BUGLEDGER_HOME`.
- `record_bug` runs `git show <fix_ref>` in the server's working directory to store the fix diff locally. It is never sent anywhere.

Source, issues, and the rule pack: https://github.com/xajeel/bugledger-mcp

## License

MIT
