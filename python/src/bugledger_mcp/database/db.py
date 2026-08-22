import sqlite3
import os
import sqlite3
import importlib.resources
from pathlib import Path

def get_db_path() -> Path:

    """ Returns the absolute path to the ledger database file. 
        respects BUGLEDGER_HOME env var and creates the
        parent directory if it doesn't exist.
    """

    custom_home = os.getenv("BUGLEDGER_HOME")
    if custom_home: 
        base_dir = Path(custom_home)
    else:
        base_dir = Path.home() / ".bugledger"

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / "ledger.db"


def run_migrations(conn: sqlite3.Connection) -> None:
    """ Runs all the migration scripts in the schema directory. """

    schema_dir = importlib.resources.files("bugledger_mcp.shared.schema")
    cursor = conn.cursor()
    user_version = cursor.execute("PRAGMA user_version;").fetchone()[0]
    sql_files = []

    for file in schema_dir.iterdir():
        if file.name.endswith(".sql") and file.name:
            sql_files.append(file)
    
    sorted_sql_files = sorted(sql_files)

    for index, sql_file in enumerate(sorted_sql_files, start=1):
        if index > user_version:
            print(f"MIGRATE :> {sql_file.name}")
            file_content = sql_file.read_text(encoding="utf-8")
            cursor.executescript(file_content)
            cursor.execute(f"PRAGMA user_version={index}")
            conn.commit()

def init_db():
    """ Initializes the database connection. """

    database_path = get_db_path()
    print(f"DATABASE PATH :> {database_path}")
    conn = sqlite3.connect(database_path)
    run_migrations(conn)
    return conn

if __name__ == "__main__":
    conn = init_db()
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    print(f"Current migration version: {version}")
    conn.close()


    
