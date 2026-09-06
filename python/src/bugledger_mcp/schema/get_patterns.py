from pydantic import BaseModel, field_validator

from bugledger_mcp.schema.record_bug import clean_slug
from bugledger_mcp.utils.constant import pattern_settings

(
    DEFAULT_LIMIT,
    MAX_LINES,
    EMPTY_FEATURE_AREA,
    EMPTY_PROJECT,
    INVALID_LIMIT,
    UNKNOWN_RECORD,
) = pattern_settings()


class GetPatternsSchema(BaseModel):
    feature_area: str
    project: str
    limit: int | None = None

    @field_validator("feature_area")
    @classmethod
    def check_feature_area(cls, value):
        value = clean_slug(value)
        if not value:
            raise ValueError(EMPTY_FEATURE_AREA)
        return value

    @field_validator("project")
    @classmethod
    def check_project(cls, value):
        value = clean_slug(value)
        if not value:
            raise ValueError(EMPTY_PROJECT)
        return value

    @field_validator("limit")
    @classmethod
    def check_limit(cls, value):
        if value is None:
            return DEFAULT_LIMIT
        if value < 1:
            raise ValueError(INVALID_LIMIT)
        if value > MAX_LINES:
            return MAX_LINES
        return value
