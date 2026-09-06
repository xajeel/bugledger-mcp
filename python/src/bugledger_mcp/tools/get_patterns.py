from typing import Annotated

from fastmcp.exceptions import ToolError
from pydantic import Field, ValidationError

from bugledger_mcp.database import db, repository
from bugledger_mcp.schema.get_patterns import GetPatternsSchema


def format_pattern_line(record_id, symptom, root_cause, project, created_at):
    date = created_at[:7]
    return f"{record_id}: {symptom} → {root_cause} ({project}, {date})"


def get_patterns(
    feature_area: Annotated[
        str,
        Field(
            description=(
                "Feature area slug you are about to work in, e.g. auth, uploads, "
                "billing. Call list_areas to see which slugs exist."
            )
        ),
    ],
    project: Annotated[
        str,
        Field(
            description=(
                "Repository or package name you are working in. Bugs already "
                "resolved for this project are hidden."
            )
        ),
    ],
    limit: int | None = Field(
        default=None, description=("Maximum records to return, 1 to 30. Default 15.")
    ),
):
    """Call this BEFORE planning, writing specs, or implementing anything in a feature area. Returns the newest past bugs for that area, one line each (symptom → root cause), capped at 30 lines. Account for every line in your plan. Bugs resolved for this project are hidden; search_bugs still finds them."""

    try:
        data = GetPatternsSchema(
            feature_area=feature_area,
            project=project,
            limit=limit,
        )
    except ValidationError as e:
        raise ToolError(e.errors()[0]["msg"].removeprefix("Value error, ")) from None

    conn = db.init_db()
    rows, total = repository.get_patterns(
        conn,
        data.feature_area,
        data.project,
        data.limit,
    )
    conn.close()

    lines = []
    for row in rows:
        lines.append(format_pattern_line(row[0], row[1], row[2], row[3], row[4]))

    truncated = total > len(lines)
    if truncated:
        older = total - len(lines)
        lines.append(f"+{older} older records: use search_bugs to dig")

    return {
        "feature_area": data.feature_area,
        "project": data.project,
        "count": len(rows),
        "truncated": truncated,
        "lines": lines,
    }
