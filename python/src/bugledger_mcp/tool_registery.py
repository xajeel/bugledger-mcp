from .mcp_server import mcp as bugledger_mcp
from .tools.test_tool import test_tool

bugledger_mcp.add_tool(test_tool)
