import subprocess

import pytest
from pydantic import ValidationError

from bugledger_mcp.schema.record_bug import RecordBugSchema
from bugledger_mcp.tools.record_bug import cap_diff, capture_diff
from bugledger_mcp.utils.constant import diff_settings

DIFF_CAP, TRUNCATION_MARK, _ = diff_settings()

VALID = {
    "symptom": "JWT accepted after logout",
    "root_cause": "jwt.verify called without checking token expiry",
    "feature_area": "auth",
    "project": "shop-app",
}


def with_root_cause(root_cause):
    data = VALID.copy()
    data["root_cause"] = root_cause
    return data


def test_root_cause_too_short():
    with pytest.raises(ValidationError):
        RecordBugSchema(**with_root_cause("fixed it"))


def test_root_cause_just_under_min_length():
    with pytest.raises(ValidationError):
        RecordBugSchema(**with_root_cause("a" * 19))


def test_root_cause_whitespace_only():
    with pytest.raises(ValidationError):
        RecordBugSchema(**with_root_cause("                    "))


def test_empty_symptom_is_rejected():
    data = VALID.copy()
    data["symptom"] = "   "
    with pytest.raises(ValidationError):
        RecordBugSchema(**data)


def test_unknown_severity():
    with pytest.raises(ValidationError):
        RecordBugSchema(**VALID, severity="critical")


def test_unknown_source():
    with pytest.raises(ValidationError):
        RecordBugSchema(**VALID, source="webhook")


def test_empty_severity_is_allowed():
    data = RecordBugSchema(**VALID, severity="")
    assert data.severity is None


def test_feature_area_and_project_are_lowercased():
    data = VALID.copy()
    data["feature_area"] = "  Auth "
    data["project"] = "Shop-App"
    parsed = RecordBugSchema(**data)
    assert parsed.feature_area == "auth"
    assert parsed.project == "shop-app"


def test_stack_is_cleaned():
    data = RecordBugSchema(**VALID, stack=[" Python", "", "sqlite", "python"])
    assert data.stack == ["python", "sqlite"]


def test_empty_stack_becomes_none():
    data = RecordBugSchema(**VALID, stack=["", "  "])
    assert data.stack is None


def _git_fails(*args, **kwargs):
    raise OSError("git not found")


def test_diff_url_without_hunk_is_none():
    assert capture_diff("https://github.com/x/y/pull/1", None) == (None, "none")


def test_diff_uses_fallback_when_ref_is_not_a_hash():
    assert capture_diff("not-a-hash", "- old\n+ new") == ("- old\n+ new", "agent")


def test_diff_uses_fallback_when_git_show_fails(monkeypatch):
    monkeypatch.setattr(subprocess, "run", _git_fails)
    assert capture_diff("abc1234", "- old\n+ new") == ("- old\n+ new", "agent")


def test_diff_comes_from_git_when_show_succeeds(monkeypatch):
    class Done:
        returncode = 0
        stdout = "commit abc1234\n\n-old\n+new\n"

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: Done())
    assert capture_diff("abc1234", "ignored") == (Done.stdout, "git")


def test_blank_fallback_is_missing():
    assert capture_diff(None, "   ") == (None, "none")


def test_agent_hunk_is_capped():
    huge = "x" * (DIFF_CAP + 1000)
    text, source = capture_diff(None, huge)
    assert source == "agent"
    assert text.endswith(TRUNCATION_MARK)
    assert len(text.encode("utf-8")) <= DIFF_CAP + len(TRUNCATION_MARK.encode("utf-8"))


def test_small_diff_is_untouched():
    assert cap_diff("- a\n+ b") == "- a\n+ b"
