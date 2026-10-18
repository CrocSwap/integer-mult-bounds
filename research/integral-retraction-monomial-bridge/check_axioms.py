#!/usr/bin/env python3
"""Audit actual Lean #print axioms output. This is NOT a proof checker.

Usage: python3 check_axioms.py SOURCE LOG [SOURCE LOG ...]
Stdlib only. Accepts no missing/duplicate queries or non-whitelisted axioms.
Only successful fresh Lean compilations should be supplied by replay.sh.
The parser also rejects error diagnostics; parsing is not proof checking.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ALLOWED = frozenset({"Quot.sound", "propext", "Classical.choice"})
QUERY = re.compile(r"^#print axioms ([A-Za-z_][A-Za-z_0-9.]*)\s*$", re.M)
RECORD = re.compile(
    r"'([^']+)'\s+(?:does not depend on any axioms|"
    r"depends on axioms:\s*\[([^\]]*)\])", re.M
)


def parse_records(text: str) -> dict[str, list[str]]:
    # Even a complete-looking census cannot certify an error-bearing compilation.
    if re.search(r"(?mi)^.*\berror:", text):
        raise ValueError("Compiler error diagnostic in axiom log")
    if re.search(r"(?i)declaration uses [\"'`]sorry[\"'`]", text):
        raise ValueError("Incomplete-proof diagnostic in axiom log")
    records: dict[str, list[str]] = {}
    for match in RECORD.finditer(text):
        name = match.group(1)
        if name in records:
            raise ValueError(f"Duplicate axiom record: {name}")
        deps = sorted({a.strip().strip('`') for a in (match.group(2) or '').split(',')
                       if a.strip()})
        extra = set(deps) - ALLOWED
        if extra:
            raise ValueError(f"Disallowed axiom dependencies for {name}: {sorted(extra)}")
        records[name] = deps
    return records


def main(argv: list[str]) -> int:
    if not argv or len(argv) % 2:
        print(__doc__, file=sys.stderr)
        return 2
    report: dict[str, list[str]] = {}
    for src_arg, log_arg in zip(argv[0::2], argv[1::2]):
        source = Path(src_arg).read_text(encoding="utf-8")
        expected = QUERY.findall(source)
        if not expected or len(set(expected)) != len(expected):
            raise ValueError(f"Empty/duplicate axiom-query inventory: {src_arg}")
        actual = parse_records(Path(log_arg).read_text(encoding="utf-8"))
        missing = set(expected) - actual.keys()
        unexpected = actual.keys() - set(expected)
        if missing or unexpected:
            raise ValueError(f"Axiom inventory mismatch for {src_arg}; "
                             f"missing={sorted(missing)}, unexpected={sorted(unexpected)}")
        if report.keys() & actual.keys():
            raise ValueError("Duplicate declarations across supplied logs")
        report.update(actual)
    print(json.dumps({"allowed_axioms": sorted(ALLOWED),
                      "declaration_count": len(report),
                      "observed_dependencies": dict(sorted(report.items()))}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except (OSError, ValueError) as exc:
        print(f"AXIOM AUDIT FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
