#!/usr/bin/env python3
"""Alternating fresh-process timings of the complete source-bound consumer.

Produced by Nick Petalas. Apache-2.0. No performance threshold is used in CI.
"""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent
MARKER = b"PASS_CORE_SECTION_CAPACITY pairs=3780 sections=127 no_new_kappa\n"


def run(engine):
    command = [sys.executable, "-I", "-W", "error", "-B",
               str(PACKAGE / "replay.py"), "--engine", engine]
    started = time.perf_counter()
    result = subprocess.run(command, capture_output=True, timeout=60, check=True)
    elapsed = time.perf_counter() - started
    if result.stdout != MARKER or result.stderr:
        raise ValueError("complete replay output differs: " + engine)
    return elapsed


def benchmark(pairs):
    if type(pairs) is not int or not 5 <= pairs <= 15:
        raise ValueError("use 5..15 complete alternating pairs")
    before_load = os.getloadavg()
    timings = {"original": [], "gray": []}
    for _ in range(pairs):
        for engine in ("original", "gray"):
            timings[engine].append(run(engine))
    medians = {key: statistics.median(values) for key, values in timings.items()}
    return {"claim_type": "local complete-consumer timing evidence",
            "python": sys.version, "platform": platform.platform(),
            "logical_cpus": os.cpu_count(), "load_before": before_load,
            "load_after": os.getloadavg(), "pairs": pairs, "failures": 0,
            "seconds": timings, "median_seconds": medians,
            "range_seconds": {k: [min(v), max(v)] for k, v in timings.items()},
            "wall_time_reduction_percent":
                100 * (1 - medians["gray"] / medians["original"]),
            "pair_improvements": sum(b < a for a, b in zip(
                timings["original"], timings["gray"])),
            "complete_output_sha256": sha256(MARKER).hexdigest(),
            "measured_code_sha256": {
                name: sha256((PACKAGE / name).read_bytes()).hexdigest()
                for name in ("replay.py", "benchmark.py", "SOURCES.json")}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(benchmark(args.pairs), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
