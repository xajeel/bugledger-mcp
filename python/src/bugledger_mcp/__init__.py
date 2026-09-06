"""Bug Ledger MCP: a local-first memory of fixed bugs for AI coding agents."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("bugledger-mcp")
except PackageNotFoundError:  # source checkout that was never installed
    __version__ = "0.0.0"
