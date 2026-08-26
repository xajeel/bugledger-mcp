from pydantic import BaseModel, field_validator

from bugledger_mcp.utils.constant import guardrails_settings

EMPTY_STACK, _INSTALL_NOTE = guardrails_settings()


class GetGuardrailsSchema(BaseModel):
    stack: str

    @field_validator("stack")
    @classmethod
    def check_stack(cls, value):
        value = value.strip().lower()
        if not value:
            raise ValueError(EMPTY_STACK)
        return value
