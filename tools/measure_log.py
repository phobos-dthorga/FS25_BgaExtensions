#!/usr/bin/env python3
"""Local FS25 log triage for Phobos testing."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


TIMESTAMP_RE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})")


def parse_timestamp(line: str) -> str | None:
    match = TIMESTAMP_RE.match(line)
    return match.group(1) if match else None


def is_phobos_line(line: str, mod_name: str) -> bool:
    lowered = line.lower().replace("\\", "/")
    return (
        mod_name.lower() in lowered
        or "/placeables/phobos/" in lowered
        or "phb_" in lowered
    )


def summarize_log(log_path: Path, mod_name: str) -> dict[str, object]:
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    summary: dict[str, object] = {
        "log_path": str(log_path),
        "line_count": len(lines),
        "first_timestamp": None,
        "last_timestamp": None,
        "mod_available_lines": [],
        "mod_load_lines": [],
        "phobos_errors": [],
        "phobos_warnings": [],
        "external_errors": [],
        "external_warnings": [],
    }

    timestamps = [stamp for line in lines if (stamp := parse_timestamp(line))]
    if timestamps:
        summary["first_timestamp"] = timestamps[0]
        summary["last_timestamp"] = timestamps[-1]
        start = datetime.strptime(timestamps[0], "%Y-%m-%d %H:%M:%S.%f")
        end = datetime.strptime(timestamps[-1], "%Y-%m-%d %H:%M:%S.%f")
        summary["log_span_seconds"] = round((end - start).total_seconds(), 3)

    for line in lines:
        if mod_name in line and ("Available mod:" in line or "Load mod:" in line):
            key = "mod_available_lines" if "Available mod:" in line else "mod_load_lines"
            summary[key].append(line)

        is_error = "Error:" in line
        is_warning = "Warning" in line
        if not (is_error or is_warning):
            continue

        target = None
        if is_phobos_line(line, mod_name):
            target = "phobos_errors" if is_error else "phobos_warnings"
        else:
            target = "external_errors" if is_error else "external_warnings"
        summary[target].append(line)

    return summary


def print_human_summary(summary: dict[str, object]) -> None:
    print(f"Log: {summary['log_path']}")
    print(f"Lines: {summary['line_count']}")
    if summary.get("log_span_seconds") is not None:
        print(f"Log span: {summary['log_span_seconds']} seconds")

    for label, key in [
        ("Phobos errors", "phobos_errors"),
        ("Phobos warnings", "phobos_warnings"),
        ("External errors", "external_errors"),
        ("External warnings", "external_warnings"),
    ]:
        values = summary[key]
        assert isinstance(values, list)
        print(f"{label}: {len(values)}")
        for line in values[:10]:
            print(f"  {line}")
        if len(values) > 10:
            print(f"  ... {len(values) - 10} more")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize FS25 log lines relevant to FS25_BgaExtensions")
    parser.add_argument("--log", required=True, help="Path to FS25 log.txt")
    parser.add_argument("--mod-name", default="FS25_BgaExtensions", help="Mod name to search for")
    parser.add_argument("--summary-json", help="Optional path to write JSON summary")
    parser.add_argument("--fail-on-phobos-warning", action="store_true", help="Exit non-zero for Phobos warnings/errors")
    args = parser.parse_args()

    log_path = Path(args.log).resolve()
    if not log_path.is_file():
        print(f"Log file not found: {log_path}", file=sys.stderr)
        return 2

    summary = summarize_log(log_path, args.mod_name)
    print_human_summary(summary)

    if args.summary_json:
        output = Path(args.summary_json).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"Wrote {output}")

    if args.fail_on_phobos_warning and (summary["phobos_errors"] or summary["phobos_warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
