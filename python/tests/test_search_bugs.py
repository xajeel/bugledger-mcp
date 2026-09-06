from bugledger_mcp.database import repository
from bugledger_mcp.database.repository import fts_query
from bugledger_mcp.schema.search_bugs import SearchBugsSchema
from bugledger_mcp.tools.search_bugs import search_bugs
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
    assert search_bugs("", feature_area=None, project=None)["hits"] == []


def test_whitespace_query_returns_no_hits():
    assert search_bugs("   ", feature_area=None, project=None)["hits"] == []


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


# --- query building: pasted errors, punctuation, stemming ---


def test_fts_query_quotes_every_word_and_joins_with_or():
    assert fts_query("JWT expiry") == '"jwt" OR "expiry"'


def test_fts_query_drops_punctuation_and_single_chars():
    assert fts_query("TypeError: x (reading 'map')") == '"typeerror" OR "reading" OR "map"'


def test_fts_query_dedupes_words():
    assert fts_query("jwt JWT jwt") == '"jwt"'


def test_fts_query_with_no_words_is_none():
    assert fts_query('"""') is None
    assert fts_query("- - -") is None


def test_hyphenated_query_still_hits():
    conn = memory_db()
    hits = repository.search_bugs(conn, "jwt-expiry", None, None, 10)
    conn.close()
    assert [h["id"] for h in hits] == ["rec_00001"]


def test_pasted_error_message_hits_the_matching_record():
    conn = memory_db()
    repository.insert_bug(
        conn,
        "rec_00003",
        "shop-app",
        "TypeError: Cannot read properties of undefined (reading 'map') on the orders page",
        "orders API returned null instead of an empty list when the user had no orders",
        "orders",
        None,
        "medium",
        None,
        None,
        "confirm",
        "2026-08-23T00:00:00Z",
    )
    hits = repository.search_bugs(
        conn, "TypeError: Cannot read properties of undefined (reading 'map')", None, None, 10
    )
    conn.close()
    assert hits[0]["id"] == "rec_00003"


def test_best_overlap_ranks_first():
    conn = memory_db()
    hits = repository.search_bugs(conn, "upload hangs large files token", None, None, 10)
    conn.close()
    assert hits[0]["id"] == "rec_00002"


def test_stemming_matches_word_forms():
    conn = memory_db()
    hits = repository.search_bugs(conn, "hanging uploads", None, None, 10)
    conn.close()
    assert [h["id"] for h in hits] == ["rec_00002"]


def test_hits_carry_severity():
    conn = memory_db()
    hits = repository.search_bugs(conn, "jwt", None, None, 10)
    conn.close()
    assert hits[0]["severity"] == "high"
