import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT = Path(__file__).parents[2] / "scripts" / "measure_rules.py"
SPEC = importlib.util.spec_from_file_location("measure_rules", SCRIPT)
measure_rules = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(measure_rules)


def test_count_findings_groups_by_rule_and_severity():
    report = {
        "results": [
            {"check_id": "rule-b", "extra": {"severity": "WARNING"}},
            {"check_id": "rule-a", "extra": {"severity": "ERROR"}},
            {"check_id": "rule-a", "extra": {"severity": "ERROR"}},
        ]
    }

    assert measure_rules.count_findings(report) == {
        ("rule-a", "ERROR"): 2,
        ("rule-b", "WARNING"): 1,
    }


def test_site_packages_returns_existing_unique_paths(monkeypatch, tmp_path):
    packages = tmp_path / "site-packages"
    packages.mkdir()
    monkeypatch.setattr(
        measure_rules.sysconfig,
        "get_paths",
        lambda: {"purelib": str(packages), "platlib": str(packages)},
    )

    assert measure_rules.site_packages() == [packages]


def test_scan_runs_semgrep_and_parses_json(monkeypatch, tmp_path):
    output = {"results": [{"check_id": "rule-a", "extra": {"severity": "ERROR"}}]}
    observed = {}

    def fake_run(command, **kwargs):
        observed["command"] = command
        observed["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout=json.dumps(output), stderr="")

    monkeypatch.setattr(measure_rules.subprocess, "run", fake_run)

    assert measure_rules.scan([tmp_path]) == output
    assert observed["command"] == [
        "semgrep",
        "--json",
        "--experimental",
        "--project-root",
        ".",
        "--config",
        str(measure_rules.RULES_DIR),
        "--metrics=off",
        ".",
    ]
    assert observed["kwargs"] == {
        "capture_output": True,
        "check": False,
        "cwd": tmp_path,
        "text": True,
    }


def test_scan_reports_semgrep_failure(monkeypatch, tmp_path):
    monkeypatch.setattr(
        measure_rules.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=2, stdout="", stderr="invalid rule"),
    )

    with pytest.raises(RuntimeError, match="exit code 2: invalid rule"):
        measure_rules.scan([tmp_path])


def test_print_report_is_sorted_and_includes_totals(capsys, tmp_path):
    counts = measure_rules.Counter({("rule-b", "WARNING"): 1, ("rule-a", "ERROR"): 2})

    measure_rules.print_report(counts, [tmp_path])

    output = capsys.readouterr().out
    assert output.index("rule-a") < output.index("rule-b")
    assert "ERROR      2" in output
    assert "WARNING    1" in output
    assert "all        3" in output
