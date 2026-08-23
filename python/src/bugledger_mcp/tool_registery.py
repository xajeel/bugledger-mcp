from .mcp_server import mcp as bugledger_mcp
from .tools.test_tool import test_tool
from .tools.record_bug import record_bug
from .tools.search_bugs import search_bugs

bugledger_mcp.add_tool(test_tool)
bugledger_mcp.add_tool(record_bug)
bugledger_mcp.add_tool(search_bugs)
