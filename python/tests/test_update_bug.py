import json

import pytest
from pydantic import ValidationError

from bugledger_mcp.database import repository
from bugledger_mcp.schema.update_bug import UpdateBugSchema
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
        UpdateBugSchema(id="upd_9999", symptom="new symptom")


def test_no_fields_is_rejected():
    with pytest.raises(ValidationError):
        UpdateBugSchema(id="rec_00001")


def test_short_root_cause_is_rejected():
    with pytest.raises(ValidationError):
        UpdateBugSchema(id="rec_00001", root_cause="fixed it")


def test_unknown_severity_is_rejected():
    with pytest.raises(ValidationError):
        UpdateBugSchema(id="rec_00001", severity="critical")


def test_bad_fix_ref_is_rejected():
    with pytest.raises(ValidationError):
        UpdateBugSchema(id="rec_00001", fix_ref="python/main.py")


def test_valid_fix_ref_is_accepted():
    data = UpdateBugSchema(id="rec_00001", fix_ref="a1b2c3d")
    assert data.fix_ref == "a1b2c3d"


def test_unknown_record_is_missing():
    conn = memory_db()
    row = repository.get_bug(conn, "rec_99999")
    conn.close()
    assert row is None


def test_update_changes_only_given_columns():
    conn = memory_db()
    updated = repository.update_bug(conn, "rec_00001", {"severity": "low"})
    row = conn.execute(
        "SELECT symptom, severity FROM bug_records WHERE id = ?", ("rec_00001",)
    ).fetchone()
    conn.close()
    assert updated == 1
    assert row[0] == "JWT accepted after logout"
    assert row[1] == "low"


def test_update_keeps_fts_in_sync():
    conn = memory_db()
    repository.update_bug(conn, "rec_00001", {"symptom": "session survives logout"})
    rows = conn.execute(
        "SELECT bug_records.id FROM bug_records_fts "
        "JOIN bug_records ON bug_records.rowid = bug_records_fts.rowid "
        "WHERE bug_records_fts MATCH 'survives'"
    ).fetchall()
    conn.close()
    assert rows == [("rec_00001",)]


def test_update_stack_stores_json():
    conn = memory_db()
    repository.update_bug(conn, "rec_00001", {"stack": json.dumps(["python", "sqlite"])})
    row = conn.execute("SELECT stack FROM bug_records WHERE id = ?", ("rec_00001",)).fetchone()
    conn.close()
    assert json.loads(row[0]) == ["python", "sqlite"]
