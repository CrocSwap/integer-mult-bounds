#!/usr/bin/env python3
"""Time complete scanner commands; produced by Nick Petalas. Apache-2.0."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "de5ec2e7a6074068452f45b1a191b5c72832df4a"
HEAD = "7c49fe32c55de02c2c873655c804b16e4c3fef0a"


def measure(implementation):
    command = [sys.executable, "-I", "-W", "error", "-B", str(PACKAGE / "run.py"),
               implementation, "--root", str(ROOT), "--base", BASE, "--head", HEAD, "--json"]
    start = time.perf_counter()
    result = subprocess.run(command, capture_output=True, timeout=180, check=False)
    elapsed = time.perf_counter() - start
    if result.returncode != 0 or result.stderr:
        raise ValueError("complete scanner command failed: " + result.stderr.decode(errors="replace"))
    report = json.loads(result.stdout)
    if report["changed_files"] != 39 or len(report["pins"]) != 154:
        raise ValueError("incomplete benchmark domain")
    return elapsed, result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runs = {name: [] for name in ("predecessor", "optimized")}
    expected = None
    for _ in range(5):
        for name in runs:
            elapsed, output = measure(name)
            if expected is not None and expected != output:
                raise ValueError("complete stdout differs")
            expected = output
            runs[name].append(elapsed)
            print(json.dumps({"implementation": name, "seconds": elapsed}), flush=True)
    summary = {name: {"seconds": values, "median": statistics.median(values),
                      "minimum": min(values), "maximum": max(values)}
               for name, values in runs.items()}
    separated = summary["optimized"]["maximum"] < summary["predecessor"]["minimum"]
    receipt = {"schema_version": 1, "base": BASE, "head": HEAD, "runs": summary,
               "errors": 0, "complete_stdout_sha256": hashlib.sha256(expected).hexdigest(),
               "changed_files": 39, "pin_rows": 154, "ordering": "five alternating pairs",
               "verdict": "faster with separated ranges" if separated else "timing inconclusive",
               "platform": platform.platform(), "python": platform.python_version(),
               "cpu_count": os.cpu_count(), "load_average_at_finish": os.getloadavg(),
               "source_sha256": {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                                 for name in ("predecessor.py", "optimized.py", "run.py", "benchmark.py")}}
    with args.output.open("x") as handle:
        handle.write(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"verdict": receipt["verdict"], "output": str(args.output)}))


if __name__ == "__main__":
    main()
