#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Time alternating fresh-process complete primary replays; write only stdout."""

import argparse
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = b"PASS_A2_E6_NINE_NORMAL_FLOOR copy=69 active=9 variable=17 fixed=52 entries=12544 controls=4\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, choices=range(5, 10), default=5)
    args = parser.parse_args()
    rows = []
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    load_start = os.getloadavg()
    for pair in range(args.pairs):
        for mode in ("original", "cached"):
            command = [sys.executable, "-I", "-W", "error", "-B",
                       str(HERE / "replay.py"), "--mode", mode]
            started = time.perf_counter_ns()
            run = subprocess.run(command, capture_output=True, timeout=60, env=env, check=False)
            elapsed = time.perf_counter_ns() - started
            if run.returncode or run.stdout != EXPECTED or run.stderr:
                raise ValueError((mode, run.returncode, run.stdout, run.stderr))
            rows.append({"pair": pair, "mode": mode, "nanoseconds": elapsed,
                         "stdout_sha256": hashlib.sha256(run.stdout).hexdigest()})
    summary = {}
    for mode in ("original", "cached"):
        values = [row["nanoseconds"] for row in rows if row["mode"] == mode]
        summary[mode] = {"median_ns": statistics.median(values),
                         "min_ns": min(values), "max_ns": max(values)}
    fraction = 1 - summary["cached"]["median_ns"] / summary["original"]["median_ns"]
    report = {"status": "PASS_A2_E6_COMPLETE_BENCHMARK", "errors": 0,
              "python": sys.version, "executable": sys.executable,
              "platform": platform.platform(), "machine": platform.machine(),
              "cpu_count": os.cpu_count(), "load_start": load_start,
              "load_end": os.getloadavg(), "runs": rows, "summary": summary,
              "median_time_reduction": fraction,
              "scope": "complete primary CLI; every run compares the full predecessor certificate"}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
