import pytest
from pydantic import ValidationError

from bugledger_mcp.schema.record_bug import RecordBugSchema
from bugledger_mcp.tools.record_bug import capture_diff

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


def test_unknown_severity():
    with pytest.raises(ValidationError):
        RecordBugSchema(**VALID, severity="critical")


def test_unknown_source():
    with pytest.raises(ValidationError):
        RecordBugSchema(**VALID, source="webhook")


def test_empty_severity_is_allowed():
    data = RecordBugSchema(**VALID, severity="")
    assert data.severity is None


def test_diff_url_without_hunk_is_none():
    assert capture_diff("https://github.com/x/y/pull/1", None) is None


def test_diff_uses_fallback_when_ref_is_not_a_hash():
    assert capture_diff("not-a-hash", "- old\n+ new") == "- old\n+ new"


def test_diff_uses_fallback_when_git_show_fails():
    assert capture_diff("abc1234", "- old\n+ new") == "- old\n+ new"


def test_blank_fallback_is_missing():
    assert capture_diff(None, "   ") is None
