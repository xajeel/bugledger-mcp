import json
import subprocess
from datetime import datetime, timezone

from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from bugledger_mcp.database import db
from bugledger_mcp.database import repository
from bugledger_mcp.schema.record_bug import RecordBugSchema
from bugledger_mcp.utils.constant import diff_settings

DIFF_CAP, TRUNCATION_MARK, COMMIT_HASH_RE = diff_settings()


def capture_diff(fix_ref, fallback):
    """ Try git show for a commit hash, else use the agent-supplied hunk. """

    if fix_ref and COMMIT_HASH_RE.fullmatch(fix_ref.strip()):
        try:
            result = subprocess.run(
                ["git", "show", fix_ref, "--no-color"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                text = result.stdout
                raw = text.encode("utf-8")
                if len(raw) > DIFF_CAP:
                    text = raw[:DIFF_CAP].decode("utf-8", errors="ignore") + TRUNCATION_MARK
                return text
        except (OSError, subprocess.SubprocessError):
            pass

    if fallback and fallback.strip():
        return fallback

    return None


def record_bug(
    symptom: str,
    root_cause: str,
    feature_area: str,
    project: str,
    stack: list[str] | None = None,
    severity: str | None = None,
    fix_ref: str | None = None,
    diff_hunk: str | None = None,
    source: str = "confirm",
):
    """Record a fixed bug into the local ledger. Call after the user confirms the draft."""

    try:
        data = RecordBugSchema(
            symptom=symptom,
            root_cause=root_cause,
            feature_area=feature_area,
            project=project,
            stack=stack,
            severity=severity,
            fix_ref=fix_ref,
            diff_hunk=diff_hunk,
            source=source,
        )
    except ValidationError as e:
        raise ToolError(e.errors()[0]["msg"].removeprefix("Value error, "))

    hunk = capture_diff(data.fix_ref, data.diff_hunk)
    if data.stack:
        stack_json = json.dumps(data.stack)
    else:
        stack_json = None

    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    conn = db.init_db()
    record_id = repository.next_record_id(conn)
    repository.insert_bug(
        conn,
        record_id,
        data.project,
        data.symptom,
        data.root_cause,
        data.feature_area,
        stack_json,
        data.severity,
        data.fix_ref,
        hunk,
        data.source,
        created_at,
    )
    total = repository.count_in_area(conn, data.feature_area)
    conn.close()

    return {
        "id": record_id,
        "status": "recorded",
        "feature_area": data.feature_area,
        "total_in_area": total,
    }
