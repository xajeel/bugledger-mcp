import json

from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from bugledger_mcp.database import db
from bugledger_mcp.database import repository
from bugledger_mcp.schema.update_bug import UpdateBugSchema
from bugledger_mcp.utils.constant import pattern_settings

_, _, _, _, _, UNKNOWN_RECORD = pattern_settings()


def update_bug(
    id: str,
    symptom: str | None = None,
    root_cause: str | None = None,
    feature_area: str | None = None,
    project: str | None = None,
    stack: list[str] | None = None,
    severity: str | None = None,
    fix_ref: str | None = None,
    diff_hunk: str | None = None,
):
    """Correct one or more fields on an existing bug record. Pass the record id
    from get_patterns, search_bugs, or record_bug, plus only the fields that
    changed — omitted fields are left as they are."""

    try:
        data = UpdateBugSchema(
            id=id,
            symptom=symptom,
            root_cause=root_cause,
            feature_area=feature_area,
            project=project,
            stack=stack,
            severity=severity,
            fix_ref=fix_ref,
            diff_hunk=diff_hunk,
        )
    except ValidationError as e:
        raise ToolError(e.errors()[0]["msg"].removeprefix("Value error, "))

    conn = db.init_db()
    row = repository.get_bug(conn, data.id)
    if row is None:
        conn.close()
        raise ToolError(UNKNOWN_RECORD)

    fields = {}
    for name in ("symptom", "root_cause", "feature_area", "project", "severity", "fix_ref", "diff_hunk"):
        value = getattr(data, name)
        if value is not None:
            fields[name] = value
    if data.stack is not None:
        fields["stack"] = json.dumps(data.stack)

    repository.update_bug(conn, data.id, fields)
    conn.close()

    return {
        "id": data.id,
        "status": "updated",
        "fields_updated": sorted(fields.keys()),
    }
