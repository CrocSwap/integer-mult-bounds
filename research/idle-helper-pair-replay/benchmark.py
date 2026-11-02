#!/usr/bin/env python3
"""Alternate complete baseline/fast commands and write a generated timing record."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time


def need(condition, message):
    if not condition:
        raise SystemExit(message)


def measure(repeats):
    script = Path(__file__).with_name("replay.py").resolve()
    rows = []
    expected = None
    for repetition in range(repeats):
        for mode in ("baseline", "fast"):
            command = [sys.executable, "-I", "-W", "error", "-B", str(script), "--mode", mode]
            started = time.perf_counter_ns()
            result = subprocess.run(command, capture_output=True, timeout=120, check=False)
            seconds = (time.perf_counter_ns() - started) / 1_000_000_000
            need(result.returncode == 0 and not result.stderr, "timed command failed")
            if expected is None:
                expected = result.stdout
            need(result.stdout == expected, "timed complete outputs differ")
            need(b"pair_products=14400" in result.stdout, "timed command did not finish the fixture")
            rows.append({"repetition": repetition + 1, "mode": mode, "seconds": seconds,
                         "command": command, "returncode": result.returncode,
                         "stdout_sha256": hashlib.sha256(result.stdout).hexdigest()})
    summaries = {}
    for mode in ("baseline", "fast"):
        seconds = [row["seconds"] for row in rows if row["mode"] == mode]
        summaries[mode] = {"median_seconds": statistics.median(seconds),
                           "min_seconds": min(seconds), "max_seconds": max(seconds)}
    gain = 1 - summaries["fast"]["median_seconds"] / summaries["baseline"]["median_seconds"]
    return {"schema": "idle-helper-complete-replay-timing/v1", "rows": rows,
            "summary": summaries, "wall_time_reduction_fraction": gain,
            "errors": 0, "stdout": expected.decode(), "repetitions_per_side": repeats,
            "python": sys.version, "platform": platform.platform(),
            "utc": datetime.now(timezone.utc).isoformat(), "load_average": os.getloadavg(),
            "cpu_count": os.cpu_count(),
            "adapter_sha256": hashlib.sha256(script.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    need(5 <= args.repeats <= 10, "repeats must be between 5 and 10")
    root = Path(__file__).resolve().parents[2]
    need(not args.output.resolve().is_relative_to(root), "write timing records outside checkout")
    record = measure(args.repeats)
    args.output.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({key: record[key] for key in ("summary", "wall_time_reduction_fraction",
                                                   "errors", "repetitions_per_side")}))


if __name__ == "__main__":
    main()
