from pydantic import BaseModel, field_validator

from bugledger_mcp.utils.constant import allowed_values, diff_settings, error_texts

ROOT_CAUSE_TOO_SHORT, INVALID_SEVERITY, INVALID_SOURCE, INVALID_FIX_REF = error_texts()
SEVERITY_VALUES, SOURCE_VALUES, MIN_ROOT_CAUSE_LEN = allowed_values()
_, _, COMMIT_HASH_RE = diff_settings()


class RecordBugSchema(BaseModel):
    symptom: str
    root_cause: str
    feature_area: str
    project: str
    stack: list[str] | None = None
    severity: str | None = None
    fix_ref: str | None = None
    diff_hunk: str | None = None
    source: str = "confirm"

    @field_validator("root_cause")
    @classmethod
    def check_root_cause(cls, value):
        value = value.strip()
        if len(value) < MIN_ROOT_CAUSE_LEN:
            raise ValueError(ROOT_CAUSE_TOO_SHORT)
        return value

    @field_validator("severity")
    @classmethod
    def check_severity(cls, value):
        if value is None or value == "":
            return None
        value = value.strip().lower()
        if value not in SEVERITY_VALUES:
            raise ValueError(INVALID_SEVERITY)
        return value

    @field_validator("fix_ref")
    @classmethod
    def check_fix_ref(cls, value):
        if value is None or value.strip() == "":
            return None
        value = value.strip()
        if not COMMIT_HASH_RE.fullmatch(value):
            raise ValueError(INVALID_FIX_REF)
        return value

    @field_validator("source")
    @classmethod
    def check_source(cls, value):
        value = value.strip().lower()
        if value not in SOURCE_VALUES:
            raise ValueError(INVALID_SOURCE)
        return value
