import json
import subprocess
from datetime import datetime, timezone
from typing import Annotated

from fastmcp.exceptions import ToolError
from pydantic import Field, ValidationError

from bugledger_mcp.database import db, repository
from bugledger_mcp.schema.record_bug import RecordBugSchema
from bugledger_mcp.utils.constant import diff_settings

DIFF_CAP, TRUNCATION_MARK, COMMIT_HASH_RE = diff_settings()


def cap_diff(text):
    """Keeps the first 32KB of a diff and marks the cut."""

    raw = text.encode("utf-8")
    if len(raw) > DIFF_CAP:
        return raw[:DIFF_CAP].decode("utf-8", errors="ignore") + TRUNCATION_MARK
    return text


def capture_diff(fix_ref, fallback):
    """Returns (diff_text, source). Tries `git show` for a commit hash in the
    server's working directory, then the agent-supplied hunk, then nothing.
    source is one of git, agent, none so the agent can tell what was stored."""

    if fix_ref and COMMIT_HASH_RE.fullmatch(fix_ref.strip()):
        try:
            result = subprocess.run(
                ["git", "show", "--no-color", fix_ref.strip()],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                return cap_diff(result.stdout), "git"
        except (OSError, subprocess.SubprocessError):
            pass

    if fallback and fallback.strip():
        return cap_diff(fallback), "agent"

    return None, "none"


def record_bug(
    symptom: Annotated[
        str,
        Field(
            description=(
                "What was observed before the fix, e.g. 'login returned 500 when the "
                "email had a plus sign'. Not 'fixed auth'."
            )
        ),
    ],
    root_cause: Annotated[
        str,
        Field(
            description=(
                "WHY it happened: the mechanism that made the failure possible. At "
                "least 20 characters. Not the patch, not 'fixed it'."
            )
        ),
    ],
    feature_area: Annotated[
        str,
        Field(
            description=(
                "Short stable slug used for later lookup: auth, uploads, billing. "
                "Reuse an existing slug from list_areas when one fits."
            )
        ),
    ],
    project: Annotated[
        str,
        Field(
            description=(
                "Repository or package name you are working in, usually the git root "
                "directory name."
            )
        ),
    ],
    stack: list[str] | None = Field(
        default=None, description=("Relevant technologies only, e.g. ['python', 'sqlite'].")
    ),
    severity: str | None = Field(
        default=None, description=("low, medium, or high. Omit if you cannot justify it.")
    ),
    fix_ref: str | None = Field(
        default=None,
        description=(
            "Git commit hash of the fix, 7 to 40 hex chars. The server runs "
            "`git show` on it to store the diff. Omit if there is no commit yet."
        ),
    ),
    diff_hunk: str | None = Field(
        default=None,
        description=(
            "The fix diff itself, used when there is no commit or git show fails. "
            "Only the change that made it correct. Capped at 32KB."
        ),
    ),
    source: str = Field(
        default="confirm",
        description=(
            "Capture channel: slash (from the /logbug prompt), confirm (you asked "
            "and the user confirmed), or import (bulk import from old notes)."
        ),
    ),
):
    """Record a fixed bug into the local ledger. Call only after the user has confirmed the symptom, root cause, and feature area. Returns the new record id; show it to the user."""

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
        raise ToolError(e.errors()[0]["msg"].removeprefix("Value error, ")) from None

    hunk, diff_source = capture_diff(data.fix_ref, data.diff_hunk)
    stack_json = json.dumps(data.stack) if data.stack else None
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    conn = db.init_db()
    record_id = repository.create_bug(
        conn,
        project=data.project,
        symptom=data.symptom,
        root_cause=data.root_cause,
        feature_area=data.feature_area,
        stack=stack_json,
        severity=data.severity,
        fix_ref=data.fix_ref,
        diff_hunk=hunk,
        source=data.source,
        created_at=created_at,
    )
    total = repository.count_in_area(conn, data.feature_area)
    conn.close()

    return {
        "id": record_id,
        "status": "recorded",
        "feature_area": data.feature_area,
        "project": data.project,
        "total_in_area": total,
        "diff_source": diff_source,
    }
