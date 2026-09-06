import pytest
from pydantic import ValidationError

from bugledger_mcp.database import repository
from bugledger_mcp.schema.get_patterns import GetPatternsSchema
from bugledger_mcp.tools.get_patterns import format_pattern_line
from bugledger_mcp.utils.constant import pattern_settings
from helpers import memory_db as apply_schema

_, MAX_LINES, _, _, _, _ = pattern_settings()


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
        "abc123",
        "this hunk must never appear in get_patterns",
        "confirm",
        "2026-06-01T00:00:00Z",
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
        "2026-07-01T00:00:00Z",
    )
    return conn


def seed_many_auth(conn, n):
    i = 3
    while i <= n + 2:
        month = str(i).zfill(2)
        repository.insert_bug(
            conn,
            f"rec_{i:05d}",
            "shop-app",
            f"auth bug {i}",
            f"root cause for auth bug number {i} xx",
            "auth",
            None,
            "low",
            None,
            None,
            "confirm",
            f"2026-{month}-01T00:00:00Z",
        )
        i = i + 1


def test_empty_feature_area_is_rejected():
    with pytest.raises(ValidationError):
        GetPatternsSchema(feature_area="", project="shop-app")


def test_empty_project_is_rejected():
    with pytest.raises(ValidationError):
        GetPatternsSchema(feature_area="auth", project="   ")


def test_limit_below_one_is_rejected():
    with pytest.raises(ValidationError):
        GetPatternsSchema(feature_area="auth", project="shop-app", limit=0)


def test_limit_above_cap_is_clamped():
    data = GetPatternsSchema(feature_area="auth", project="shop-app", limit=100)
    assert data.limit == MAX_LINES


def test_unknown_area_returns_empty_lines():
    conn = memory_db()
    rows, total = repository.get_patterns(conn, "payments", "shop-app", 5)
    conn.close()
    assert rows == []
    assert total == 0


def test_other_feature_area_is_excluded():
    conn = memory_db()
    rows, total = repository.get_patterns(conn, "auth", "shop-app", 5)
    conn.close()
    assert total == 1
    assert rows[0][1] == "JWT accepted after logout"


def test_diff_hunk_is_not_in_the_line():
    line = format_pattern_line(
        "rec_00001",
        "JWT accepted after logout",
        "jwt.verify called without checking token expiry",
        "shop-app",
        "2026-06-01T00:00:00Z",
    )
    assert "hunk" not in line
    assert line == (
        "rec_00001: JWT accepted after logout → jwt.verify called without checking token expiry "
        "(shop-app, 2026-06)"
    )


def test_truncated_when_more_than_limit():
    conn = memory_db()
    seed_many_auth(conn, 6)
    rows, total = repository.get_patterns(conn, "auth", "shop-app", 5)
    conn.close()
    assert total == 7
    assert len(rows) == 5


def test_resolved_for_one_project_is_hidden_there():
    conn = memory_db()
    repository.resolve_bug(conn, "rec_00001", "shop-app", "2026-08-24T00:00:00Z")
    hidden, total_hidden = repository.get_patterns(conn, "auth", "shop-app", 15)
    shown, total_shown = repository.get_patterns(conn, "auth", "client-portal", 15)
    conn.close()
    assert hidden == []
    assert total_hidden == 0
    assert total_shown == 1
    assert shown[0][0] == "rec_00001"


def test_search_still_finds_a_resolved_bug():
    conn = memory_db()
    repository.resolve_bug(conn, "rec_00001", "shop-app", "2026-08-24T00:00:00Z")
    hits = repository.search_bugs(conn, "jwt", None, None, 10)
    conn.close()
    assert len(hits) == 1
    assert hits[0]["id"] == "rec_00001"
