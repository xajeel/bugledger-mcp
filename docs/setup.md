# Set up Bug Ledger in an MCP client

Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/) first.
Each configuration below starts Bug Ledger as a local stdio MCP server with
`uvx bugledger-mcp`.

## Codex CLI

Add the server from a terminal:

```sh
codex mcp add bugledger -- uvx bugledger-mcp
```

Run `codex mcp list` to confirm that `bugledger` is enabled, then restart any
Codex session that was already open.

## Windsurf

Open **Cascade > MCPs > Configure**, or edit
`~/.codeium/windsurf/mcp_config.json`, and add:

```json
{
  "mcpServers": {
    "bugledger": {
      "command": "uvx",
      "args": ["bugledger-mcp"]
    }
  }
}
```

Restart Windsurf and check the MCPs panel for the server status.

## Zed

Open **Settings > AI > MCP Servers > Add Server > Add Local Server**. To edit
the settings file directly, add this `context_servers` entry:

```json
{
  "context_servers": {
    "bugledger": {
      "command": "uvx",
      "args": ["bugledger-mcp"],
      "env": {}
    }
  }
}
```

The indicator beside `bugledger` in the MCP Servers settings should turn
green when the server is active.

## Continue

Add the following entry to the `mcpServers` list in
`~/.continue/config.yaml`:

```yaml
mcpServers:
  - name: Bug Ledger
    command: uvx
    args:
      - bugledger-mcp
```

Restart Continue and use Agent mode, where MCP tools are available.

## Other clients

Configure a local stdio server with command `uvx` and one argument,
`bugledger-mcp`. The server writes protocol messages to stdout and diagnostics
to stderr.

See the client documentation for the surrounding configuration format:

- [Codex MCP commands](https://developers.openai.com/codex/mcp/)
- [Windsurf MCP configuration](https://docs.windsurf.com/windsurf/cascade/mcp)
- [Zed MCP configuration](https://zed.dev/docs/ai/mcp)
- [Continue MCP configuration](https://docs.continue.dev/customize/mcp-tools)
