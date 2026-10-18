#!/usr/bin/env python3
"""Recompute and compare the exact bounded UT4 search certificate."""

import json
import importlib.util
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("ut4_noncentral_search", HERE / "search.py")
if SPEC is None or SPEC.loader is None:
    raise SystemExit("cannot load search.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
expected = json.loads((HERE / "certificate.json").read_text(encoding="utf-8"))
actual = MODULE.search()
if actual != expected:
    raise SystemExit("certificate mismatch")

root = HERE.parents[1]
baseline_expected = json.loads((HERE / "BASELINE.json").read_text(encoding="utf-8"))
assert baseline_expected.pop("command") == "python3 -B scripts/research_baseline.py"
baseline_run = subprocess.run(
    [sys.executable, "-B", "scripts/research_baseline.py"],
    cwd=root,
    capture_output=True,
    check=True,
    text=True,
)
if json.loads(baseline_run.stdout) != baseline_expected:
    raise SystemExit("selected baseline positive-control receipt mismatch")

print(
    "PASS_UT4_NONCENTRAL_Q4 "
    f"factors={actual['factors']} pair_words={actual['ordered_pair_words']} "
    f"distinct_pairs={actual['distinct_pair_products']} "
    f"q3={actual['q3_candidates_checked']} q4={actual['q4_candidates_checked']} "
    f"outcome={actual['outcome']} baseline={baseline_expected['binding_primitive']}"
)
