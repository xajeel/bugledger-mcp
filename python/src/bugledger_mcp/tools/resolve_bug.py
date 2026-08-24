from datetime import datetime, timezone

from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from bugledger_mcp.database import db
from bugledger_mcp.database import repository
from bugledger_mcp.schema.resolve_bug import ResolveBugSchema
from bugledger_mcp.utils.constant import pattern_settings

_, _, _, _, _, UNKNOWN_RECORD = pattern_settings()


def resolve_bug(id: str, project: str):
    """Mark a bug resolved for one project after a test or fix exists there. 
    Other projects still see it in get_patterns and search until they resolve it too."""

    try:
        data = ResolveBugSchema(id=id, project=project)
    except ValidationError as e:
        raise ToolError(e.errors()[0]["msg"].removeprefix("Value error, "))

    conn = db.init_db()
    row = repository.get_bug(conn, data.id)
    if row is None:
        conn.close()
        raise ToolError(UNKNOWN_RECORD)

    inserted = repository.resolve_bug(
        conn,
        data.id,
        data.project,
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    conn.close()

    if inserted == 0:
        status = "already_resolved"
    else:
        status = "resolved"

    return {
        "id": data.id,
        "project": data.project,
        "status": status,
    }
