from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from bugledger_mcp.database import db
from bugledger_mcp.database import repository
from bugledger_mcp.schema.get_patterns import GetPatternsSchema


def format_pattern_line(record_id, symptom, root_cause, project, created_at):
    date = created_at[:7]
    return f"{record_id}: {symptom} → {root_cause} ({project}, {date})"


def get_patterns(feature_area: str, project: str, limit: int | None = None):
    """Call this BEFORE planning, writing specs, or implementing a feature. Pass the project you are working in. Records already resolved for that project are hidden. Search still finds them for other projects. This is a requirement-gathering step. Do not skip it."""

    try:
        data = GetPatternsSchema(
            feature_area=feature_area,
            project=project,
            limit=limit,
        )
    except ValidationError as e:
        raise ToolError(e.errors()[0]["msg"].removeprefix("Value error, "))

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
        lines.append(f"+{older} older records — use search_bugs to dig")

    return {
        "feature_area": data.feature_area,
        "project": data.project,
        "count": len(rows),
        "truncated": truncated,
        "lines": lines,
    }
