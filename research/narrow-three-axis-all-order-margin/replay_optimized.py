#!/usr/bin/env python3
"""Run all five science/review paths in explicit optimized child interpreters.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
SPDX-License-Identifier: Apache-2.0
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
if sys.flags.optimize < 1:
    raise RuntimeError("the optimized suite must itself run with -O")

for script, timeout in (
    ("classify_leading.py", 30),
    ("check_mixed_columns.py", 60),
    ("check_source_and_controls.py", 30),
    ("review/classification/verify_independent.py", 120),
    ("review/analytic/check_constants.py", 30),
):
    print("OPTIMIZED_REPLAY "+script, flush=True)
    subprocess.run(
        [sys.executable, "-I", "-O", "-W", "error", "-B", str(ROOT/script)],
        check=True, timeout=timeout,
    )
print("PASS_COMPLETE_OPTIMIZED_SCIENCE_AND_REVIEWS", flush=True)
