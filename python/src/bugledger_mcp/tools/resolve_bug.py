from datetime import datetime, timezone
from typing import Annotated

from fastmcp.exceptions import ToolError
from pydantic import Field, ValidationError

from bugledger_mcp.database import db, repository
from bugledger_mcp.schema.resolve_bug import ResolveBugSchema
from bugledger_mcp.utils.constant import pattern_settings

_, _, _, _, _, UNKNOWN_RECORD = pattern_settings()


def resolve_bug(
    id: Annotated[
        str,
        Field(
            description=("Record id from get_patterns, search_bugs, or record_bug, e.g. rec_00042.")
        ),
    ],
    project: Annotated[
        str, Field(description=("The project that now has a guardrail for this bug."))
    ],
):
    """Hide a bug from get_patterns for one project because that project now guards against it: a regression test, a Semgrep rule, or the fix itself is in place. Other projects still see the bug, and search_bugs finds it everywhere."""

    try:
        data = ResolveBugSchema(id=id, project=project)
    except ValidationError as e:
        raise ToolError(e.errors()[0]["msg"].removeprefix("Value error, ")) from None

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

    status = "resolved" if inserted else "already_resolved"

    return {
        "id": data.id,
        "project": data.project,
        "status": status,
    }
