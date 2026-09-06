import re
from typing import Annotated

from fastmcp.exceptions import ToolError
from pydantic import Field, ValidationError

from bugledger_mcp.schema.get_guardrails import GetGuardrailsSchema
from bugledger_mcp.utils.constant import guardrails_settings
from bugledger_mcp.utils.shared_files import list_shared_files

_EMPTY_STACK, INSTALL_NOTE = guardrails_settings()

_STACKS_RE = re.compile(r"bugledger-stacks:\s*\[([^\]]+)\]")
_SEVERITY_RE = re.compile(r"^\s*severity:\s*(\w+)", re.MULTILINE)


def _extract_stacks(content):
    stacks = []
    for match in _STACKS_RE.finditer(content):
        stacks.extend(s.strip().lower() for s in match.group(1).split(","))
    return stacks or ["all"]


def _rule_matches(stacks, requested_stack):
    if "all" in stacks or requested_stack == "all":
        return True
    return requested_stack in stacks


def _highest_severity(content):
    order = {"ERROR": 3, "WARNING": 2, "INFO": 1}
    found = [m.group(1).upper() for m in _SEVERITY_RE.finditer(content)]
    if not found:
        return "WARNING"
    return max(found, key=lambda s: order.get(s, 0))


def get_guardrails(
    stack: Annotated[
        str,
        Field(
            description=(
                "Primary language of the project: python, javascript, typescript, "
                "ruby, java, go, and so on. Use 'all' for every rule. Language-neutral "
                "rules are always included."
            )
        ),
    ],
):
    """Returns the Bug Ledger starter pack of Semgrep rules for classic AI-coding mistakes (injection, hardcoded secrets, unsafe deserialization, open CORS, and more) as files to write into .bugledger/, plus the CI workflow to add. ERROR rules block PRs, WARNING rules are advisory. Never edit existing CI files."""

    try:
        data = GetGuardrailsSchema(stack=stack)
    except ValidationError as e:
        raise ToolError(e.errors()[0]["msg"].removeprefix("Value error, ")) from None

    matched = []

    for yaml_file in sorted(list_shared_files("rules", suffix=".yaml"), key=lambda p: p.name):
        content = yaml_file.read_text(encoding="utf-8")
        stacks = _extract_stacks(content)
        if _rule_matches(stacks, data.stack):
            matched.append(
                {
                    "filename": yaml_file.name,
                    "severity": _highest_severity(content),
                    "content": content,
                }
            )

    return {
        "stack": data.stack,
        "rules": matched,
        "count": len(matched),
        "install_note": INSTALL_NOTE,
    }
