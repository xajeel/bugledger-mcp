import sqlite3
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "shared" / "schema"


def memory_db():
    """In-memory ledger with every migration applied, in order."""
    conn = sqlite3.connect(":memory:")
    for sql_file in sorted(SCHEMA_DIR.glob("*.sql")):
        conn.executescript(sql_file.read_text(encoding="utf-8"))
    return conn
