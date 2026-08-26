import re
from pathlib import Path

from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from bugledger_mcp.schema.get_guardrails import GetGuardrailsSchema
from bugledger_mcp.utils.constant import guardrails_settings

_EMPTY_STACK, INSTALL_NOTE = guardrails_settings()

_STACKS_RE = re.compile(r"bugledger-stacks:\s*\[([^\]]+)\]")


def _find_rules_dir():
    for parent in Path(__file__).resolve().parents:
        path = parent / "shared" / "rules"
        if path.is_dir():
            return path
    raise FileNotFoundError("shared/rules/ not found")


def _extract_stacks(content):
    stacks = []
    for match in _STACKS_RE.finditer(content):
        stacks.extend(s.strip().lower() for s in match.group(1).split(","))
    return stacks or ["all"]


def _rule_matches(stacks, requested_stack):
    if "all" in stacks or requested_stack == "all":
        return True
    return requested_stack in stacks


def get_guardrails(stack: str):
    """Returns Semgrep rule files for the given stack. The agent writes
    these into .bugledger/ and adds a new CI workflow. Never edits
    existing CI files."""

    try:
        data = GetGuardrailsSchema(stack=stack)
    except ValidationError as e:
        raise ToolError(e.errors()[0]["msg"].removeprefix("Value error, "))

    rules_dir = _find_rules_dir()
    matched = []

    for yaml_file in sorted(rules_dir.glob("*.yaml")):
        content = yaml_file.read_text(encoding="utf-8")
        stacks = _extract_stacks(content)
        if _rule_matches(stacks, data.stack):
            matched.append({
                "filename": yaml_file.name,
                "content": content,
            })

    return {
        "stack": data.stack,
        "rules": matched,
        "count": len(matched),
        "install_note": INSTALL_NOTE,
    }
