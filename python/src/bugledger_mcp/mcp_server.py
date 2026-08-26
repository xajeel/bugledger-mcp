import sys

from fastmcp import FastMCP

mcp = FastMCP("BugLedger MCP")


def main():
    from bugledger_mcp.database import db
    import bugledger_mcp.tool_registery  # noqa: F401

    conn = db.init_db()
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    print(f"Current migration version: {version}", file=sys.stderr)
    conn.close()
    mcp.run()


if __name__ == "__main__":
    main()
