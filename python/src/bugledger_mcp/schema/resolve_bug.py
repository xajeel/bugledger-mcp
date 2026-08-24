from pydantic import BaseModel, field_validator

from bugledger_mcp.utils.constant import pattern_settings, record_id_settings

(
    DEFAULT_LIMIT,
    MAX_LINES,
    EMPTY_FEATURE_AREA,
    EMPTY_PROJECT,
    INVALID_LIMIT,
    UNKNOWN_RECORD,
) = pattern_settings()
RECORD_ID_RE, INVALID_RECORD_ID = record_id_settings()


class ResolveBugSchema(BaseModel):
    id: str
    project: str

    @field_validator("id")
    @classmethod
    def check_id(cls, value):
        value = value.strip()
        if not RECORD_ID_RE.fullmatch(value):
            raise ValueError(INVALID_RECORD_ID)
        return value

    @field_validator("project")
    @classmethod
    def check_project(cls, value):
        value = value.strip()
        if not value:
            raise ValueError(EMPTY_PROJECT)
        return value
