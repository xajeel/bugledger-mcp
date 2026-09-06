import pytest
from pydantic import ValidationError

from bugledger_mcp.database import repository
from bugledger_mcp.schema.delete_bug import DeleteBugSchema
from helpers import memory_db as apply_schema


def memory_db():
    conn = apply_schema()
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


def test_invented_id_pattern_is_rejected():
    with pytest.raises(ValidationError):
        DeleteBugSchema(id="del_9999")


def test_short_id_is_rejected():
    with pytest.raises(ValidationError):
        DeleteBugSchema(id="rec_1")


def test_unknown_record_is_missing():
    conn = memory_db()
    row = repository.get_bug(conn, "rec_99999")
    conn.close()
    assert row is None


def test_delete_removes_record():
    conn = memory_db()
    deleted = repository.delete_bug(conn, "rec_00001")
    row = repository.get_bug(conn, "rec_00001")
    conn.close()
    assert deleted == 1
    assert row is None


def test_delete_removes_fts_entry():
    conn = memory_db()
    repository.delete_bug(conn, "rec_00001")
    rows = conn.execute(
        "SELECT rowid FROM bug_records_fts WHERE bug_records_fts MATCH 'JWT'"
    ).fetchall()
    conn.close()
    assert rows == []


def test_delete_removes_resolutions():
    conn = memory_db()
    repository.resolve_bug(conn, "rec_00001", "shop-app", "2026-08-24T00:00:00Z")
    repository.delete_bug(conn, "rec_00001")
    rows = conn.execute(
        "SELECT * FROM bug_resolutions WHERE record_id = ?", ("rec_00001",)
    ).fetchall()
    conn.close()
    assert rows == []


def test_delete_missing_record_is_noop():
    conn = memory_db()
    deleted = repository.delete_bug(conn, "rec_99999")
    conn.close()
    assert deleted == 0
