import json
from typing import Annotated

from fastmcp.exceptions import ToolError
from pydantic import Field, ValidationError

from bugledger_mcp.database import db, repository
from bugledger_mcp.schema.update_bug import UpdateBugSchema
from bugledger_mcp.utils.constant import pattern_settings

_, _, _, _, _, UNKNOWN_RECORD = pattern_settings()


def update_bug(
    id: Annotated[
        str,
        Field(
            description=("Record id from get_patterns, search_bugs, or record_bug, e.g. rec_00042.")
        ),
    ],
    symptom: str | None = Field(default=None, description="New symptom text."),
    root_cause: str | None = Field(
        default=None, description=("New root cause, at least 20 characters explaining WHY.")
    ),
    feature_area: str | None = Field(default=None, description="New feature area slug."),
    project: str | None = Field(default=None, description="New project name."),
    stack: list[str] | None = Field(
        default=None, description=("New technology list, replaces the old one.")
    ),
    severity: str | None = Field(default=None, description="low, medium, or high."),
    fix_ref: str | None = Field(
        default=None, description=("Git commit hash of the fix, 7 to 40 hex chars.")
    ),
    diff_hunk: str | None = Field(
        default=None,
        description=(
            "The fix diff. Use this when record_bug reported diff_source 'none' "
            "and you have the change in front of you."
        ),
    ),
):
    """Correct one or more fields on an existing bug record. Pass only the fields that changed; omitted fields are left as they are."""

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
        raise ToolError(e.errors()[0]["msg"].removeprefix("Value error, ")) from None

    conn = db.init_db()
    row = repository.get_bug(conn, data.id)
    if row is None:
        conn.close()
        raise ToolError(UNKNOWN_RECORD)

    fields = {}
    for name in (
        "symptom",
        "root_cause",
        "feature_area",
        "project",
        "severity",
        "fix_ref",
        "diff_hunk",
    ):
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
