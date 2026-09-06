from typing import Annotated

from fastmcp.exceptions import ToolError
from pydantic import Field, ValidationError

from bugledger_mcp.database import db, repository
from bugledger_mcp.schema.search_bugs import SearchBugsSchema
from bugledger_mcp.utils.constant import search_settings

SEARCH_LIMIT = search_settings()


def search_bugs(
    query: Annotated[
        str,
        Field(
            description=(
                "Words from an error message, symptom, or root cause. Paste the key "
                "part of the error as is: punctuation is ignored, any word may match, "
                "and the best matches come first."
            )
        ),
    ],
    feature_area: str | None = Field(
        default=None, description=("Optional feature area slug to narrow the search.")
    ),
    project: str | None = Field(
        default=None, description=("Optional project name to narrow the search.")
    ),
):
    """Search past bugs by symptom or root cause: 'have we seen this before?'. Use it while debugging. Omit the filters to search the whole ledger, including bugs already resolved for this project."""

    try:
        data = SearchBugsSchema(
            query=query,
            feature_area=feature_area,
            project=project,
        )
    except ValidationError as e:
        raise ToolError(e.errors()[0]["msg"].removeprefix("Value error, ")) from None

    if not data.query:
        return {"query": data.query, "count": 0, "hits": []}

    conn = db.init_db()
    hits = repository.search_bugs(
        conn,
        data.query,
        data.feature_area,
        data.project,
        SEARCH_LIMIT,
    )
    conn.close()

    return {"query": data.query, "count": len(hits), "hits": hits}
