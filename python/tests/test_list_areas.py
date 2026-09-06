from bugledger_mcp.database import repository
from helpers import memory_db


def seed(conn):
    rows = [
        ("rec_00001", "shop-app", "auth"),
        ("rec_00002", "shop-app", "auth"),
        ("rec_00003", "client-portal", "uploads"),
    ]
    for record_id, project, area in rows:
        repository.insert_bug(
            conn,
            record_id,
            project,
            f"symptom {record_id}",
            "a root cause that is long enough to pass",
            area,
            None,
            None,
            None,
            None,
            "confirm",
            "2026-08-23T00:00:00Z",
        )


def test_empty_ledger():
    conn = memory_db()
    areas, projects, total = repository.list_areas(conn)
    conn.close()
    assert areas == []
    assert projects == []
    assert total == 0


def test_counts_sorted_by_size_then_name():
    conn = memory_db()
    seed(conn)
    areas, projects, total = repository.list_areas(conn)
    conn.close()
    assert total == 3
    assert areas == [("auth", 2), ("uploads", 1)]
    assert projects == [("shop-app", 2), ("client-portal", 1)]
