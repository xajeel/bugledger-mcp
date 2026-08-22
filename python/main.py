from bugledger_mcp.mcp_server import mcp
from bugledger_mcp.tool_registery import *
from bugledger_mcp.database import db

def main():
    conn = db.init_db()
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    print(f"Current migration version: {version}")
    conn.close()
    mcp.run()


if __name__ == "__main__":
    main()
