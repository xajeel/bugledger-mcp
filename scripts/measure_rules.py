"""Measure Bug Ledger rule findings across installed Python packages."""

from __future__ import annotations

import json
import subprocess
import sysconfig
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = REPO_ROOT / "shared" / "rules"


def site_packages() -> list[Path]:
    """Return the unique package directories for the active Python environment."""
    paths = sysconfig.get_paths()
    return sorted(
        {path.resolve() for name in ("purelib", "platlib") if (path := Path(paths[name])).is_dir()}
    )


def count_findings(report: dict[str, Any]) -> Counter[tuple[str, str]]:
    """Count Semgrep findings by rule identifier and severity."""
    return Counter(
        (
            result["check_id"],
            result.get("extra", {}).get("severity", "UNKNOWN").upper(),
        )
        for result in report.get("results", [])
    )


def scan(paths: list[Path]) -> dict[str, Any]:
    """Run the repository rule pack against package directories."""
    command = [
        "semgrep",
        "--json",
        "--experimental",
        "--project-root",
        ".",
        "--config",
        str(RULES_DIR),
        "--metrics=off",
        ".",
    ]
    combined: dict[str, Any] = {"results": []}
    for path in paths:
        completed = subprocess.run(command, capture_output=True, check=False, cwd=path, text=True)
        if completed.returncode:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"Semgrep failed with exit code {completed.returncode}: {detail}")

        try:
            report = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError("Semgrep did not return valid JSON") from error
        combined["results"].extend(report.get("results", []))
    return combined


def print_report(counts: Counter[tuple[str, str]], scanned: list[Path]) -> None:
    """Print deterministic per-rule counts and severity totals."""
    print("Scanned package directories:")
    for path in scanned:
        print(f"  {path}")

    print("\nFindings by rule:")
    if not counts:
        print("  none")
    else:
        for (rule_id, severity), count in sorted(counts.items()):
            print(f"  {severity:<7} {count:>4}  {rule_id}")

    severity_totals = Counter()
    for (_, severity), count in counts.items():
        severity_totals[severity] += count

    print("\nTotals by severity:")
    if not severity_totals:
        print("  all         0")
    else:
        for severity, count in sorted(severity_totals.items()):
            print(f"  {severity:<7} {count:>4}")
        print(f"  {'all':<7} {sum(severity_totals.values()):>4}")


def main() -> None:
    """Measure rule findings in the active environment."""
    paths = site_packages()
    if not paths:
        raise SystemExit("No site-packages directories found for the active Python")
    print_report(count_findings(scan(paths)), paths)


if __name__ == "__main__":
    main()
