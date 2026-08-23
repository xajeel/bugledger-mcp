import sqlite3
from pathlib import Path

from bugledger_mcp.database import repository
from bugledger_mcp.schema.search_bugs import SearchBugsSchema
from bugledger_mcp.tools.search_bugs import search_bugs

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "shared" / "schema"


def memory_db():
    conn = sqlite3.connect(":memory:")
    conn.executescript((SCHEMA_DIR / "001_init.sql").read_text())
    conn.executescript((SCHEMA_DIR / "002_fts.sql").read_text())
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
        "2026-08-23T00:00:00Z",
    )
    repository.insert_bug(
        conn,
        "rec_00002",
        "client-portal",
        "upload hangs on large files",
        "multipart parser had no size cap so the worker blocked",
        "uploads",
        None,
        "medium",
        None,
        None,
        "confirm",
        "2026-08-23T00:00:00Z",
    )
    return conn


def test_empty_query_returns_no_hits():
    assert search_bugs("") == {"hits": []}


def test_whitespace_query_returns_no_hits():
    assert search_bugs("   ") == {"hits": []}


def test_blank_filters_become_none():
    data = SearchBugsSchema(query="jwt", feature_area="", project="")
    assert data.feature_area is None
    assert data.project is None


def test_query_is_stripped():
    data = SearchBugsSchema(query="  jwt  ")
    assert data.query == "jwt"


def test_nonsense_query_returns_no_hits():
    conn = memory_db()
    hits = repository.search_bugs(conn, "zzzznotabug", None, None, 10)
    conn.close()
    assert hits == []


def test_bad_fts_syntax_returns_no_hits():
    conn = memory_db()
    hits = repository.search_bugs(conn, '"""', None, None, 10)
    conn.close()
    assert hits == []


def test_wrong_feature_area_excludes_hit():
    conn = memory_db()
    hits = repository.search_bugs(conn, "jwt", "uploads", None, 10)
    conn.close()
    assert hits == []


def test_wrong_project_excludes_hit():
    conn = memory_db()
    hits = repository.search_bugs(conn, "jwt", None, "client-portal", 10)
    conn.close()
    assert hits == []


def test_combined_filters_miss_when_one_is_wrong():
    conn = memory_db()
    hits = repository.search_bugs(conn, "jwt", "auth", "client-portal", 10)
    conn.close()
    assert hits == []


def test_combined_filters_hit_when_both_match():
    conn = memory_db()
    hits = repository.search_bugs(conn, "jwt", "auth", "shop-app", 10)
    conn.close()
    assert len(hits) == 1
    assert hits[0]["id"] == "rec_00001"
