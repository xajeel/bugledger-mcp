import json
import sys

import pytest

from bugledger_mcp import __version__
from bugledger_mcp.mcp_server import main


def seed_ledger(home):
    from bugledger_mcp.database import db

    conn = db.init_db()
    conn.execute(
        """
        INSERT INTO bug_records (
            id, project, symptom, root_cause, feature_area, stack,
            severity, fix_ref, diff_hunk, source, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "rec_00002",
            "shop-app",
            "Checkout returned 500",
            "The retry reused an expired payment token",
            "payments",
            '["python", "stripe"]',
            "high",
            "#42",
            "- old\n+ new",
            "confirm",
            "2026-09-20T02:00:00+00:00",
        ),
    )
    conn.execute(
        """
        INSERT INTO bug_records (
            id, project, symptom, root_cause, feature_area, stack,
            severity, fix_ref, diff_hunk, source, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "rec_00001",
            "admin-ui",
            "Login redirected in a loop",
            "The callback URL retained a stale session nonce",
            "auth",
            None,
            None,
            None,
            None,
            "slash",
            "2026-09-20T01:00:00+00:00",
        ),
    )
    conn.execute(
        "INSERT INTO bug_resolutions (record_id, project, resolved_at) VALUES (?, ?, ?)",
        ("rec_00001", "admin-ui", "2026-09-20T03:00:00+00:00"),
    )
    conn.commit()
    conn.close()
    return home / "ledger.db"


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


def test_export_json_to_stdout_is_complete_and_deterministic(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("BUGLEDGER_HOME", str(tmp_path))
    db_path = seed_ledger(tmp_path)
    before = db_path.read_bytes()
    monkeypatch.setattr(sys, "argv", ["bugledger-mcp", "export", "--format", "json"])

    main()

    exported = json.loads(capsys.readouterr().out)
    assert exported["format_version"] == 1
    assert [record["id"] for record in exported["records"]] == ["rec_00001", "rec_00002"]
    assert exported["records"][0]["stack"] is None
    assert exported["records"][1]["stack"] == ["python", "stripe"]
    assert exported["records"][0]["resolutions"] == [
        {"project": "admin-ui", "resolved_at": "2026-09-20T03:00:00+00:00"}
    ]
    assert exported["records"][1]["diff_hunk"] == "- old\n+ new"
    assert db_path.read_bytes() == before


def test_export_markdown_groups_records_and_writes_file(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("BUGLEDGER_HOME", str(tmp_path / "home"))
    seed_ledger(tmp_path / "home")
    output = tmp_path / "exports" / "ledger.md"
    monkeypatch.setattr(
        sys,
        "argv",
        ["bugledger-mcp", "export", "--format", "md", "--out", str(output)],
    )

    main()

    assert capsys.readouterr().out == ""
    text = output.read_text(encoding="utf-8")
    assert text.startswith("# Bug Ledger export\n")
    assert text.index("## auth") < text.index("## payments")
    assert "### rec_00001 — Login redirected in a loop" in text
    assert "**Resolved for:** admin-ui (2026-09-20T03:00:00+00:00)" in text
    assert "```diff\n- old\n+ new\n```" in text


def test_export_empty_ledger_as_json(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("BUGLEDGER_HOME", str(tmp_path))
    monkeypatch.setattr(sys, "argv", ["bugledger-mcp", "export", "--format", "json"])

    main()

    assert json.loads(capsys.readouterr().out) == {"format_version": 1, "records": []}


def test_export_requires_a_supported_format(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["bugledger-mcp", "export", "--format", "csv"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    assert "invalid choice" in capsys.readouterr().err
