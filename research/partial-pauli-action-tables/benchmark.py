"""Measure alternating complete fresh-process replays; write only outside the checkout.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

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


def sample(original):
    argv = [sys.executable, "-I", "-W", "error", "-B", str(PACKAGE / "replay.py")]
    if original:
        argv.append("--original")
    start = time.perf_counter_ns()
    result = subprocess.run(argv, capture_output=True, timeout=30, check=True)
    elapsed = (time.perf_counter_ns() - start) / 1e9
    if result.stderr or not result.stdout.startswith(b"PASS_PARTIAL_PAULI_GAUSSIAN_MINIMUM "):
        raise ValueError("complete replay did not return its successful output")
    return elapsed, result.stdout


def measure(rounds):
    if type(rounds) is not int or not 5 <= rounds <= 12:
        raise ValueError("benchmark rounds must be in 5..12")
    initial_load = os.getloadavg() if hasattr(os, "getloadavg") else None
    _, expected = sample(True)
    _, candidate = sample(False)
    if candidate != expected:
        raise ValueError("warmup complete outputs differ")
    samples = {"original": [], "tables": []}
    order = []
    for _ in range(rounds):
        for name, original in (("original", True), ("tables", False)):
            elapsed, output = sample(original)
            if output != expected:
                raise ValueError("timed complete outputs differ")
            samples[name].append(elapsed)
            order.append(name)
    medians = {name: statistics.median(values) for name, values in samples.items()}
    files = ("replay.py", "benchmark.py", "SOURCES.json")
    return {
        "status": "PASS_PARTIAL_PAULI_ACTION_TABLE_BENCHMARK",
        "errors": 0, "rounds": rounds, "order": order, "seconds": samples,
        "median_seconds": medians,
        "range_seconds": {name: [min(v), max(v)] for name, v in samples.items()},
        "fraction_less_wall_time": 1 - medians["tables"] / medians["original"],
        "complete_stdout": expected.decode(),
        "complete_stdout_sha256": hashlib.sha256(expected).hexdigest(),
        "python": sys.version, "executable": sys.executable,
        "platform": platform.platform(), "logical_cpus": os.cpu_count(),
        "load_before": initial_load,
        "load_after": os.getloadavg() if hasattr(os, "getloadavg") else None,
        "files_sha256": {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                         for name in files},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=6)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.output.is_absolute() or args.output.is_relative_to(PACKAGE.parents[1]):
        raise ValueError("benchmark output must be an absolute path outside the checkout")
    report = measure(args.rounds)
    with args.output.open("x") as stream:
        stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
