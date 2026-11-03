"""Time alternating fresh processes; emit observations, never a timing gate.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

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


def run(baseline):
    command = [sys.executable, "-I", "-W", "error", "-B", str(HERE / "replay.py")]
    if baseline:
        command.append("--baseline")
    start = time.perf_counter_ns()
    result = subprocess.run(command, capture_output=True, check=False, timeout=120)
    elapsed = time.perf_counter_ns() - start
    if result.returncode or result.stderr:
        raise ValueError(f"replay failed: {result.returncode}, {result.stderr!r}")
    if b"PASS_FULL_FAMILY_G_WITHOUT_D fixtures=2:" not in result.stdout:
        raise ValueError("replay did not complete")
    return elapsed, result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=7)
    args = parser.parse_args()
    if not 5 <= args.pairs <= 20:
        raise ValueError("pairs must lie in 5..20")
    results = {"baseline_ns": [], "candidate_ns": []}
    expected = None
    for _ in range(args.pairs):
        for baseline, key in ((True, "baseline_ns"), (False, "candidate_ns")):
            elapsed, output = run(baseline)
            if expected is None:
                expected = output
            if output != expected:
                raise ValueError("complete scientific stdout differs")
            results[key].append(elapsed)
    before = statistics.median(results["baseline_ns"])
    after = statistics.median(results["candidate_ns"])
    results.update(python=sys.version, platform=platform.platform(),
                   cpu_count=os.cpu_count(), load_average=os.getloadavg(),
                   order="baseline,candidate repeated", failures=0,
                   median_reduction_percent=100 * (before - after) / before,
                   scientific_stdout_sha256=hashlib.sha256(expected).hexdigest(),
                   source_sha256=hashlib.sha256(
                       (HERE.parent / "full-family-g-without-d" / "verify.py")
                       .read_bytes()).hexdigest(),
                   adapter_sha256=hashlib.sha256((HERE / "replay.py").read_bytes()).hexdigest())
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
