import asyncio

from bugledger_mcp.prompts.logbug import logbug, read_logbug_text
from bugledger_mcp.tool_registry import bugledger_mcp


def test_logbug_text_tells_the_agent_to_wait():
    text = read_logbug_text()
    assert "record_bug" in text
    assert "confirm" in text.lower()
    assert "slash" in text


def test_logbug_text_skips_feature_work():
    text = read_logbug_text()
    assert "does not look like a bug fix" in text


def test_logbug_returns_the_shared_file():
    assert logbug() == read_logbug_text()
    assert logbug().strip() != ""


def test_logbug_is_registered_on_the_server():
    prompts = asyncio.run(bugledger_mcp.list_prompts())
    names = [p.name for p in prompts]
    assert "logbug" in names
