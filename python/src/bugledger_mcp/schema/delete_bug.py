from pydantic import BaseModel, field_validator

from bugledger_mcp.utils.constant import record_id_settings

RECORD_ID_RE, INVALID_RECORD_ID = record_id_settings()


class DeleteBugSchema(BaseModel):
    id: str

    @field_validator("id")
    @classmethod
    def check_id(cls, value):
        value = value.strip()
        if not RECORD_ID_RE.fullmatch(value):
            raise ValueError(INVALID_RECORD_ID)
        return value
