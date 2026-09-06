from bugledger_mcp.database import db, repository


def list_areas():
    """List every feature_area slug and project name in the ledger with record counts. Call it before record_bug or get_patterns to reuse existing names instead of inventing new ones, or to see what the ledger holds."""

    conn = db.init_db()
    areas, projects, total = repository.list_areas(conn)
    conn.close()

    return {
        "total": total,
        "feature_areas": [{"feature_area": a, "count": n} for a, n in areas],
        "projects": [{"project": p, "count": n} for p, n in projects],
    }
