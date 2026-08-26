import pytest
from fastmcp.exceptions import ToolError

from bugledger_mcp.tools.get_guardrails import get_guardrails


def test_returns_all_rules_for_stack_all():
    result = get_guardrails(stack="all")
    assert result["count"] >= 12
    assert len(result["rules"]) == result["count"]
    assert result["stack"] == "all"


def test_every_rule_has_filename_and_content():
    result = get_guardrails(stack="all")
    for rule in result["rules"]:
        assert rule["filename"].endswith(".yaml")
        assert "rules:" in rule["content"]
        assert len(rule["content"]) > 0


def test_stack_python_includes_universal_and_python_rules():
    result = get_guardrails(stack="python")
    filenames = [r["filename"] for r in result["rules"]]
    assert "hardcoded-secret.yaml" in filenames
    assert "sql-injection.yaml" in filenames
    assert "shell-injection.yaml" in filenames
    assert "eval-usage.yaml" in filenames


def test_stack_javascript_includes_universal_and_js_rules():
    result = get_guardrails(stack="javascript")
    filenames = [r["filename"] for r in result["rules"]]
    assert "hardcoded-secret.yaml" in filenames
    assert "sql-injection.yaml" in filenames
    assert "insecure-random.yaml" in filenames


def test_includes_install_note():
    result = get_guardrails(stack="all")
    assert "install_note" in result
    assert ".bugledger/" in result["install_note"]
    assert "bugledger.yml" in result["install_note"]


def test_empty_stack_rejected():
    with pytest.raises(ToolError):
        get_guardrails(stack="")


def test_whitespace_stack_rejected():
    with pytest.raises(ToolError):
        get_guardrails(stack="   ")


def test_stack_is_lowercased():
    result = get_guardrails(stack="Python")
    assert result["stack"] == "python"


def test_rules_sorted_by_filename():
    result = get_guardrails(stack="all")
    filenames = [r["filename"] for r in result["rules"]]
    assert filenames == sorted(filenames)


def test_unknown_stack_returns_only_universal_rules():
    result = get_guardrails(stack="cobol")
    for rule in result["rules"]:
        assert "bugledger-stacks: [all]" in rule["content"]
