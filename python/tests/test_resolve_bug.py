import sqlite3
from pathlib import Path

import pytest
from pydantic import ValidationError

from bugledger_mcp.database import repository
from bugledger_mcp.schema.resolve_bug import ResolveBugSchema

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "shared" / "schema"


def memory_db():
    conn = sqlite3.connect(":memory:")
    conn.executescript((SCHEMA_DIR / "001_init.sql").read_text())
    conn.executescript((SCHEMA_DIR / "002_fts.sql").read_text())
    conn.executescript((SCHEMA_DIR / "003_resolutions.sql").read_text())
    repository.insert_bug(
        conn,
        "rec_00001",
        "shop-app",
        "JWT accepted after logout",
        "jwt.verify called without checking token expiry",
        "auth",
        None,
        "high",
        None,
        None,
        "confirm",
        "2026-06-01T00:00:00Z",
    )
    return conn


def test_empty_project_is_rejected():
    with pytest.raises(ValidationError):
        ResolveBugSchema(id="rec_00001", project="")


def test_invented_id_pattern_is_rejected():
    with pytest.raises(ValidationError):
        ResolveBugSchema(id="res_9999", project="shop-app")


def test_short_id_is_rejected():
    with pytest.raises(ValidationError):
        ResolveBugSchema(id="rec_1", project="shop-app")


def test_unknown_id_is_missing():
    conn = memory_db()
    row = repository.get_bug(conn, "rec_99999")
    conn.close()
    assert row is None


def test_resolve_twice_is_ignored():
    conn = memory_db()
    first = repository.resolve_bug(conn, "rec_00001", "shop-app", "2026-08-24T00:00:00Z")
    second = repository.resolve_bug(conn, "rec_00001", "shop-app", "2026-08-24T00:00:01Z")
    conn.close()
    assert first == 1
    assert second == 0
