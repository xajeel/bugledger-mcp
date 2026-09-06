<p align="center">
  <img alt="Bug Ledger" src="https://raw.githubusercontent.com/xajeel/bugledger-mcp/main/artifacts/logo/mark.svg" width="96">
</p>

# Bug Ledger

<p align="center">
  <strong>Never fix the same bug twice.</strong><br>
  A local MCP server that gives AI coding agents a permanent memory of the bugs you already fixed.
</p>

<p align="center">
  <a href="https://pypi.org/project/bugledger-mcp/"><img alt="PyPI" src="https://img.shields.io/pypi/v/bugledger-mcp?color=6366F1"></a>
  <a href="https://pypi.org/project/bugledger-mcp/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/bugledger-mcp"></a>
  <a href="https://github.com/xajeel/bugledger-mcp/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/xajeel/bugledger-mcp/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/xajeel/bugledger-mcp/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-14B8A6"></a>
</p>

## What it does

Your agent fixes a bug. You confirm the record. From then on, every session on that project checks the ledger before writing code in that area and can search it while debugging.

- **Before coding**, the agent calls `get_patterns` and sees the past bugs for that feature area.
- **While debugging**, it calls `search_bugs` with the error text.
- **After a fix**, you run `/logbug`. The agent drafts the record, you approve, it is stored.

Everything stays on your machine: one SQLite file in `~/.bugledger/`. No account, no cloud, no telemetry.

## Install

Requires [uv](https://docs.astral.sh/uv/). It downloads Python if needed.

**Claude Code**

```sh
claude mcp add bugledger -- uvx bugledger-mcp
```

**Cursor**, in `.cursor/mcp.json`:

```json
{ "mcpServers": { "bugledger": { "command": "uvx", "args": ["bugledger-mcp"] } } }
```

**Any other MCP client:** command `uvx`, argument `bugledger-mcp`, transport stdio.

**Whole team:** commit that JSON as `.mcp.json` (Claude Code) or `.cursor/mcp.json` (Cursor) in the repo. Everyone who opens the project gets the server.

Restart the client. `/mcp` lists `bugledger` as connected and `/mcp__bugledger__logbug` is available.

## Use

1. **Fix a bug as usual.**
2. **Run `/mcp__bugledger__logbug`.** The agent checks that the session really contained a bug fix, drafts the symptom, root cause, feature area, and stack, shows you the draft, and stores it only after you say yes. Feature work and refactors are refused.
3. **Keep working.** On connect, the server tells the agent to call `get_patterns` before coding and `search_bugs` while debugging. Nothing else to set up.

To make the check a hard rule, add one line to `CLAUDE.md` or `.cursorrules`:

```
Before implementing anything in a feature area, call bugledger get_patterns with that area and this project's name, and account for every returned bug. After fixing a bug, run /mcp__bugledger__logbug.
```

## Tools

| Tool | Purpose |
|---|---|
| `get_patterns(feature_area, project)` | Past bugs for an area, one line each, capped at 30 lines |
| `search_bugs(query)` | Full-text search over symptoms and root causes; paste the error as is |
| `record_bug(...)` | Store a confirmed bug with its root cause and fix diff |
| `list_areas()` | Existing feature areas and projects, so names stay consistent |
| `update_bug` / `delete_bug` | Correct or remove a record |
| `resolve_bug(id, project)` | Hide a bug from `get_patterns` for one project once a guardrail covers it |
| `get_guardrails(stack)` | Starter Semgrep rules and the CI workflow that installs them |

## Guardrails

`get_guardrails` returns hand-written Semgrep rules for the classic mistakes agents make: SQL and shell injection, hardcoded secrets, unsafe deserialization, `eval`, open CORS, debug mode, insecure random, plain HTTP. The agent writes them to `.bugledger/` in your repo and adds one workflow file. Existing CI files are never touched. ERROR rules block the pull request, WARNING rules only report. Delete a rule file to drop it.

## Data and privacy

- The ledger is `~/.bugledger/ledger.db`. Set `BUGLEDGER_HOME` to move it. Delete it any time; it is recreated on next start.
- `record_bug` runs `git show <commit>` locally to store the fix diff. Diffs are never returned by `get_patterns` and never leave your machine.
- The server makes no network calls.

## Contributing

Bug reports, new rules, and pull requests are welcome. Setup, tests, and the release process are in [CONTRIBUTING.md](https://github.com/xajeel/bugledger-mcp/blob/main/CONTRIBUTING.md).

## License

[MIT](https://github.com/xajeel/bugledger-mcp/blob/main/LICENSE)
