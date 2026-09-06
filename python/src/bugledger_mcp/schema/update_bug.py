from pydantic import BaseModel, field_validator, model_validator

from bugledger_mcp.schema.record_bug import clean_slug, clean_stack
from bugledger_mcp.utils.constant import (
    allowed_values,
    diff_settings,
    error_texts,
    mutation_settings,
    record_id_settings,
)

ROOT_CAUSE_TOO_SHORT, INVALID_SEVERITY, INVALID_SOURCE, INVALID_FIX_REF = error_texts()
SEVERITY_VALUES, SOURCE_VALUES, MIN_ROOT_CAUSE_LEN = allowed_values()
_, _, COMMIT_HASH_RE = diff_settings()
RECORD_ID_RE, INVALID_RECORD_ID = record_id_settings()
NO_FIELDS_TO_UPDATE = mutation_settings()

UPDATABLE_FIELDS = (
    "symptom",
    "root_cause",
    "feature_area",
    "project",
    "stack",
    "severity",
    "fix_ref",
    "diff_hunk",
)


class UpdateBugSchema(BaseModel):
    id: str
    symptom: str | None = None
    root_cause: str | None = None
    feature_area: str | None = None
    project: str | None = None
    stack: list[str] | None = None
    severity: str | None = None
    fix_ref: str | None = None
    diff_hunk: str | None = None

    @field_validator("id")
    @classmethod
    def check_id(cls, value):
        value = value.strip()
        if not RECORD_ID_RE.fullmatch(value):
            raise ValueError(INVALID_RECORD_ID)
        return value

    @field_validator("symptom")
    @classmethod
    def check_symptom(cls, value):
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("root_cause")
    @classmethod
    def check_root_cause(cls, value):
        if value is None:
            return None
        value = value.strip()
        if len(value) < MIN_ROOT_CAUSE_LEN:
            raise ValueError(ROOT_CAUSE_TOO_SHORT)
        return value

    @field_validator("feature_area", "project")
    @classmethod
    def check_slug(cls, value):
        if value is None:
            return None
        return clean_slug(value) or None

    @field_validator("stack")
    @classmethod
    def check_stack(cls, value):
        return clean_stack(value)

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

    @model_validator(mode="after")
    def check_any_field(self):
        if all(getattr(self, field) is None for field in UPDATABLE_FIELDS):
            raise ValueError(NO_FIELDS_TO_UPDATE)
        return self
