import sys

import pytest

from bugledger_mcp import __version__
from bugledger_mcp.mcp_server import main


def test_main_is_callable():
    assert callable(main)


def test_main_version_exits_without_starting_server(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["bugledger-mcp", "--version"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    assert capsys.readouterr().out == f"bugledger-mcp {__version__}\n"


def test_main_help_describes_ledger_home(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["bugledger-mcp", "--help"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    output = capsys.readouterr().out
    assert output.startswith("usage: bugledger-mcp")
    assert "BUGLEDGER_HOME" in output
