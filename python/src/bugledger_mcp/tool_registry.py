from fastmcp.prompts import Prompt
from fastmcp.tools import Tool
from mcp.types import ToolAnnotations

from .mcp_server import mcp as bugledger_mcp
from .prompts.logbug import logbug
from .tools.delete_bug import delete_bug
from .tools.get_guardrails import get_guardrails
from .tools.get_patterns import get_patterns
from .tools.list_areas import list_areas
from .tools.record_bug import record_bug
from .tools.resolve_bug import resolve_bug
from .tools.search_bugs import search_bugs
from .tools.update_bug import update_bug

# Annotations tell MCP clients which tools only read, which write, and which
# destroy data, so they can decide how much to ask the user.
READ_ONLY = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)
WRITE = ToolAnnotations(
    readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False
)
IDEMPOTENT_WRITE = ToolAnnotations(
    readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False
)
DESTRUCTIVE = ToolAnnotations(
    readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=False
)


def _register(fn, title, annotations):
    bugledger_mcp.add_tool(Tool.from_function(fn, title=title, annotations=annotations))


_register(record_bug, "Record a fixed bug", WRITE)
_register(get_patterns, "Past bugs in a feature area", READ_ONLY)
_register(search_bugs, "Search past bugs", READ_ONLY)
_register(list_areas, "Feature areas and projects in the ledger", READ_ONLY)
_register(resolve_bug, "Hide a bug for one project", IDEMPOTENT_WRITE)
_register(update_bug, "Correct a bug record", IDEMPOTENT_WRITE)
_register(delete_bug, "Delete a bug record", DESTRUCTIVE)
_register(get_guardrails, "Semgrep starter rules", READ_ONLY)
bugledger_mcp.add_prompt(Prompt.from_function(logbug))
