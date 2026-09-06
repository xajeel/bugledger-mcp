from typing import Annotated

from fastmcp.exceptions import ToolError
from pydantic import Field, ValidationError

from bugledger_mcp.database import db, repository
from bugledger_mcp.schema.delete_bug import DeleteBugSchema
from bugledger_mcp.utils.constant import pattern_settings

_, _, _, _, _, UNKNOWN_RECORD = pattern_settings()


def delete_bug(
    id: Annotated[
        str,
        Field(
            description=("Record id from get_patterns, search_bugs, or record_bug, e.g. rec_00042.")
        ),
    ],
):
    """Permanently delete a bug record and any resolutions tied to it. This cannot be undone; confirm with the user first. To hide a bug for one project instead, use resolve_bug."""

    try:
        data = DeleteBugSchema(id=id)
    except ValidationError as e:
        raise ToolError(e.errors()[0]["msg"].removeprefix("Value error, ")) from None

    conn = db.init_db()
    row = repository.get_bug(conn, data.id)
    if row is None:
        conn.close()
        raise ToolError(UNKNOWN_RECORD)

    repository.delete_bug(conn, data.id)
    conn.close()

    return {
        "id": data.id,
        "status": "deleted",
    }
