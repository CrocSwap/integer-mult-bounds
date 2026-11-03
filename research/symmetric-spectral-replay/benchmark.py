#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Time five alternating fresh-process complete scientific replays."""
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
SOURCE = ROOT / "research/alternating-plane-spectral-copy"
EXPECTED = b"PASS_ALTERNATING_PLANE_SPECTRAL_COPY\n"


def run(path):
    command = [sys.executable, "-I", "-W", "error", "-B", str(path)]
    started = time.perf_counter_ns()
    process = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30, check=False)
    elapsed = time.perf_counter_ns() - started
    if process.returncode != 0 or process.stdout != EXPECTED or process.stderr:
        raise RuntimeError(f"complete replay failed: {path.name}: {process!r}")
    return {"elapsed_ns": elapsed, "returncode": process.returncode,
            "stdout_sha256": hashlib.sha256(process.stdout).hexdigest(),
            "stderr_bytes": len(process.stderr)}


def measure():
    paths = {"baseline": SOURCE / "verify.py", "candidate": PACKAGE / "replay.py"}
    hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
    pairs = []
    for _ in range(5):
        pairs.append({name: run(path) for name, path in paths.items()})
    summary = {}
    for name in paths:
        values = [pair[name]["elapsed_ns"] for pair in pairs]
        summary[name] = {"median_ns": statistics.median(values),
                         "min_ns": min(values), "max_ns": max(values)}
    base = summary["baseline"]["median_ns"]
    fast = summary["candidate"]["median_ns"]
    return {"schema": "symmetric-spectral-benchmark/1", "pairs": pairs,
            "summary": summary, "median_time_reduction_percent": 100 * (base - fast) / base,
            "all_pairs_improve": all(p["candidate"]["elapsed_ns"] < p["baseline"]["elapsed_ns"] for p in pairs),
            "failures": 0, "scope": "complete primary command, fresh process, five alternating pairs",
            "python": sys.version, "executable": sys.executable,
            "platform": platform.platform(), "logical_cpus": os.cpu_count(),
            "load_average_after": os.getloadavg(), "source_sha256": hashes,
            "result_sha256": hashlib.sha256((SOURCE / "RESULT.json").read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output is not None and args.output.exists():
        parser.error("output already exists")
    result = measure()
    text = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output is not None:
        with args.output.open("x") as stream:
            if stream.write(text) != len(text):
                raise OSError("partial benchmark write")
    print(text, end="")


if __name__ == "__main__":
    main()
