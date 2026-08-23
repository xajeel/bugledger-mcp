from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from bugledger_mcp.database import db
from bugledger_mcp.database import repository
from bugledger_mcp.schema.search_bugs import SearchBugsSchema
from bugledger_mcp.utils.constant import search_settings

SEARCH_LIMIT = search_settings()


def search_bugs(
    query: str,
    feature_area: str | None = None,
    project: str | None = None,
):
    """Search past bugs by symptom or root cause. Omit filters to search the whole ledger. Pass feature_area, project, or both to narrow."""

    try:
        data = SearchBugsSchema(
            query=query,
            feature_area=feature_area,
            project=project,
        )
    except ValidationError as e:
        raise ToolError(e.errors()[0]["msg"].removeprefix("Value error, "))

    if not data.query:
        return {"hits": []}

    conn = db.init_db()
    hits = repository.search_bugs(
        conn,
        data.query,
        data.feature_area,
        data.project,
        SEARCH_LIMIT,
    )
    conn.close()

    return {"hits": hits}
