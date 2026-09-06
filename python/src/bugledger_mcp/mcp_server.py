import sys

from fastmcp import FastMCP

from bugledger_mcp import __version__

# Sent to the client in the MCP initialize response. Claude Code and Cursor
# show it to the agent, so this is the standing instruction for when to use
# the ledger without a human having to remember.
INSTRUCTIONS = """\
Bug Ledger is a local memory of bugs this team has already fixed. Use it so the same bug is never written twice.

- Before planning or implementing work in a feature area, call get_patterns(feature_area, project) and account for every returned bug in your plan and code.
- While debugging, call search_bugs with the key words of the error or symptom to check whether it was seen before.
- After a bug is fixed and the user confirms the details, record it with record_bug. The /logbug prompt walks through this. Never record feature work, refactors, or guesses.
- Call list_areas to see which feature_area slugs and project names already exist, and reuse them so records stay findable.
- project is the name of the repository or package you are working in, usually the git root directory name.
"""

mcp = FastMCP("bugledger", instructions=INSTRUCTIONS, version=__version__)


def main():
    import bugledger_mcp.tool_registry  # noqa: F401  (registers tools and the prompt)
    from bugledger_mcp.database import db

    conn = db.init_db()
    schema_version = conn.execute("PRAGMA user_version").fetchone()[0]
    conn.close()
    print(
        f"bugledger-mcp {__version__} | ledger {db.get_db_path()} | schema v{schema_version}",
        file=sys.stderr,
    )
    # No banner: keeps stderr quiet in MCP client logs and skips FastMCP's
    # update check, so the server makes no network calls at all.
    mcp.run(show_banner=False)


if __name__ == "__main__":
    main()
