import os
import sqlite3
import sys
from pathlib import Path

from bugledger_mcp.utils.shared_files import list_shared_files


def get_db_path() -> Path:
    """Path of the ledger database. Honors BUGLEDGER_HOME, defaults to ~/.bugledger/."""

    custom_home = os.getenv("BUGLEDGER_HOME")
    base_dir = Path(custom_home) if custom_home else Path.home() / ".bugledger"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / "ledger.db"


def run_migrations(conn: sqlite3.Connection) -> None:
    """Apply every shared/schema/*.sql file newer than PRAGMA user_version, in name order."""

    cursor = conn.cursor()
    user_version = cursor.execute("PRAGMA user_version;").fetchone()[0]
    sql_files = sorted(list_shared_files("schema", suffix=".sql"), key=lambda f: f.name)

    for index, sql_file in enumerate(sql_files, start=1):
        if index > user_version:
            print(f"bugledger-mcp: applying migration {sql_file.name}", file=sys.stderr)
            cursor.executescript(sql_file.read_text(encoding="utf-8"))
            cursor.execute(f"PRAGMA user_version={index}")
            conn.commit()


def init_db() -> sqlite3.Connection:
    """Open the ledger, creating the file and applying migrations if needed."""

    conn = sqlite3.connect(get_db_path(), timeout=10)
    run_migrations(conn)
    return conn
