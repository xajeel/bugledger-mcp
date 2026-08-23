from pydantic import BaseModel, field_validator


class SearchBugsSchema(BaseModel):
    query: str
    feature_area: str | None = None
    project: str | None = None

    @field_validator("query")
    @classmethod
    def strip_query(cls, value):
        return value.strip()

    @field_validator("feature_area", "project")
    @classmethod
    def strip_optional(cls, value):
        if value is None or value == "":
            return None
        return value.strip()
