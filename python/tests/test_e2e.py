"""End-to-end: drive the real server object through the MCP protocol with
an in-memory client, against a throwaway ledger directory."""

import asyncio
import json
import sqlite3

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from bugledger_mcp.tool_registry import bugledger_mcp

EXPECTED_TOOLS = {
    "record_bug",
    "get_patterns",
    "search_bugs",
    "list_areas",
    "resolve_bug",
    "update_bug",
    "delete_bug",
    "get_guardrails",
}

BUG = {
    "symptom": "login returned 500 when the email had a plus sign",
    "root_cause": "email was used as a path segment and '+' was not percent-encoded",
    "feature_area": "Auth",
    "project": "Shop-App",
    "stack": ["python", "fastapi"],
    "severity": "medium",
    "diff_hunk": "-    path = f'/users/{email}'\n+    path = f'/users/{quote(email)}'",
    "source": "slash",
}


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    monkeypatch.setenv("BUGLEDGER_HOME", str(tmp_path))
    return tmp_path


def run(coro):
    return asyncio.run(coro)


async def call(client, name, **args):
    result = await client.call_tool(name, args)
    return result.data


def test_handshake_exposes_tools_prompt_and_instructions(ledger):
    async def scenario():
        async with Client(bugledger_mcp) as client:
            tools = {t.name: t for t in await client.list_tools()}
            prompts = [p.name for p in await client.list_prompts()]
            init = client.initialize_result
            return tools, prompts, init

    tools, prompts, init = run(scenario())
    assert set(tools) == EXPECTED_TOOLS
    assert "test_tool" not in tools
    assert prompts == ["logbug"]
    assert init.serverInfo.name == "bugledger"
    assert "get_patterns" in init.instructions
    assert tools["get_patterns"].annotations.readOnlyHint is True
    assert tools["delete_bug"].annotations.destructiveHint is True
    assert tools["record_bug"].annotations.readOnlyHint is False
    # parameter descriptions reach the agent
    props = tools["record_bug"].inputSchema["properties"]
    assert "WHY" in props["root_cause"]["description"]
    assert props["severity"]["description"].startswith("low, medium, or high")


def test_logbug_prompt_returns_the_ritual(ledger):
    async def scenario():
        async with Client(bugledger_mcp) as client:
            result = await client.get_prompt("logbug")
            return result.messages[0].content.text

    text = run(scenario())
    assert "record_bug" in text
    assert "this does not look like a bug fix" in text


def test_full_ledger_lifecycle(ledger):
    async def scenario():
        async with Client(bugledger_mcp) as client:
            out = {}
            out["empty"] = await call(client, "list_areas")
            out["recorded"] = await call(client, "record_bug", **BUG)
            out["areas"] = await call(client, "list_areas")
            out["patterns"] = await call(
                client, "get_patterns", feature_area="auth", project="shop-app"
            )
            out["patterns_other_case"] = await call(
                client, "get_patterns", feature_area="AUTH", project="Shop-App"
            )
            out["search"] = await call(client, "search_bugs", query="HTTP 500: plus-sign in e-mail")
            out["resolved"] = await call(
                client, "resolve_bug", id=out["recorded"]["id"], project="shop-app"
            )
            out["resolved_again"] = await call(
                client, "resolve_bug", id=out["recorded"]["id"], project="shop-app"
            )
            out["patterns_hidden"] = await call(
                client, "get_patterns", feature_area="auth", project="shop-app"
            )
            out["patterns_elsewhere"] = await call(
                client, "get_patterns", feature_area="auth", project="client-portal"
            )
            out["search_still"] = await call(
                client, "search_bugs", query="plus sign", project="shop-app"
            )
            out["updated"] = await call(
                client, "update_bug", id=out["recorded"]["id"], severity="high", stack=["python"]
            )
            out["deleted"] = await call(client, "delete_bug", id=out["recorded"]["id"])
            out["after"] = await call(client, "list_areas")
            return out

    out = run(scenario())

    assert out["empty"]["total"] == 0

    rec = out["recorded"]
    assert rec["id"] == "rec_00001"
    assert rec["status"] == "recorded"
    assert rec["feature_area"] == "auth"
    assert rec["project"] == "shop-app"
    assert rec["total_in_area"] == 1
    assert rec["diff_source"] == "agent"

    assert out["areas"]["feature_areas"] == [{"feature_area": "auth", "count": 1}]
    assert out["areas"]["projects"] == [{"project": "shop-app", "count": 1}]

    assert out["patterns"]["count"] == 1
    assert out["patterns"]["lines"][0].startswith("rec_00001: login returned 500")
    assert "percent-encoded" in out["patterns"]["lines"][0]
    assert "quote(email)" not in json.dumps(out["patterns"])  # diff never leaks into patterns
    assert out["patterns_other_case"]["lines"] == out["patterns"]["lines"]

    assert out["search"]["count"] == 1
    assert out["search"]["hits"][0]["id"] == "rec_00001"
    assert out["search"]["hits"][0]["severity"] == "medium"

    assert out["resolved"]["status"] == "resolved"
    assert out["resolved_again"]["status"] == "already_resolved"
    assert out["patterns_hidden"]["lines"] == []
    assert out["patterns_elsewhere"]["count"] == 1
    assert out["search_still"]["count"] == 1

    assert out["updated"]["fields_updated"] == ["severity", "stack"]
    assert out["deleted"]["status"] == "deleted"
    assert out["after"]["total"] == 0

    # the row really landed in the SQLite file with the diff and stack stored
    db_file = ledger / "ledger.db"
    assert db_file.exists()
    conn = sqlite3.connect(db_file)
    assert conn.execute("PRAGMA user_version").fetchone()[0] >= 4
    conn.close()


def test_stored_row_has_diff_stack_and_source(ledger):
    async def scenario():
        async with Client(bugledger_mcp) as client:
            return await call(client, "record_bug", **BUG)

    rec = run(scenario())
    conn = sqlite3.connect(ledger / "ledger.db")
    row = conn.execute(
        "SELECT stack, diff_hunk, source, severity FROM bug_records WHERE id = ?", (rec["id"],)
    ).fetchone()
    conn.close()
    assert json.loads(row[0]) == ["python", "fastapi"]
    assert "quote(email)" in row[1]
    assert row[2] == "slash"
    assert row[3] == "medium"


def test_validation_errors_reach_the_agent_as_text(ledger):
    async def scenario():
        async with Client(bugledger_mcp) as client:
            bad = dict(BUG, root_cause="fixed it")
            with pytest.raises(ToolError) as err:
                await client.call_tool("record_bug", bad)
            return str(err.value)

    message = run(scenario())
    assert "root_cause is too vague" in message


def test_unknown_id_is_a_clean_error(ledger):
    async def scenario():
        async with Client(bugledger_mcp) as client:
            with pytest.raises(ToolError) as err:
                await client.call_tool("delete_bug", {"id": "rec_99999"})
            return str(err.value)

    assert "no bug record with that id" in run(scenario())


def test_ids_stay_unique_across_records(ledger):
    async def scenario():
        async with Client(bugledger_mcp) as client:
            ids = []
            for i in range(3):
                rec = await call(client, "record_bug", **dict(BUG, symptom=f"symptom {i}"))
                ids.append(rec["id"])
            return ids

    assert run(scenario()) == ["rec_00001", "rec_00002", "rec_00003"]


def test_guardrails_over_protocol(ledger):
    async def scenario():
        async with Client(bugledger_mcp) as client:
            return await call(client, "get_guardrails", stack="python")

    result = run(scenario())
    names = {r["filename"] for r in result["rules"]}
    assert "sql-injection.yaml" in names
    assert "todo-fixme.yaml" not in names
    severities = {r["filename"]: r["severity"] for r in result["rules"]}
    assert severities["sql-injection.yaml"] == "ERROR"
    assert severities["empty-catch.yaml"] == "WARNING"
    assert "--severity ERROR --error" in result["install_note"]
