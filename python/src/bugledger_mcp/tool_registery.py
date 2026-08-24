from .mcp_server import mcp as bugledger_mcp
from .tools.test_tool import test_tool
from .tools.record_bug import record_bug
from .tools.search_bugs import search_bugs
from .tools.get_patterns import get_patterns
from .tools.resolve_bug import resolve_bug

bugledger_mcp.add_tool(test_tool)
bugledger_mcp.add_tool(record_bug)
bugledger_mcp.add_tool(search_bugs)
bugledger_mcp.add_tool(get_patterns)
bugledger_mcp.add_tool(resolve_bug)
