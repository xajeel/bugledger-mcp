import json
import re
from itertools import groupby
from pathlib import Path

from bugledger_mcp.database import repository


def render_json(records):
    return (
        json.dumps(
            {"format_version": 1, "records": records},
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )


def _one_line(value):
    return " ".join(value.splitlines())


def _diff_block(diff_hunk):
    longest_run = max((len(run) for run in re.findall(r"`+", diff_hunk)), default=0)
    fence = "`" * max(3, longest_run + 1)
    return f"{fence}diff\n{diff_hunk.rstrip()}\n{fence}"


def render_markdown(records):
    lines = ["# Bug Ledger export", ""]
    ordered = sorted(records, key=lambda record: (record["feature_area"], record["id"]))
    for feature_area, grouped in groupby(ordered, key=lambda record: record["feature_area"]):
        lines.extend((f"## {_one_line(feature_area)}", ""))
        for record in grouped:
            lines.extend(
                (
                    f"### {record['id']} — {_one_line(record['symptom'])}",
                    "",
                    f"**Project:** {record['project']}",
                    f"**Created:** {record['created_at']}",
                    f"**Root cause:** {_one_line(record['root_cause'])}",
                )
            )
            if record["stack"]:
                lines.append(f"**Stack:** {', '.join(record['stack'])}")
            if record["severity"]:
                lines.append(f"**Severity:** {record['severity']}")
            if record["fix_ref"]:
                lines.append(f"**Fix reference:** {_one_line(record['fix_ref'])}")
            if record["resolutions"]:
                resolved = ", ".join(
                    f"{item['project']} ({item['resolved_at']})" for item in record["resolutions"]
                )
                lines.append(f"**Resolved for:** {resolved}")
            if record["diff_hunk"]:
                lines.extend(("", _diff_block(record["diff_hunk"])))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def export_ledger(conn, output_format, output_path=None):
    records = repository.export_records(conn)
    content = render_json(records) if output_format == "json" else render_markdown(records)
    if output_path is None:
        print(content, end="")
        return

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
