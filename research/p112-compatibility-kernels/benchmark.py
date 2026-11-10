#!/usr/bin/env python3
"""Alternate five complete source and kernel CLI runs. Nick Petalas."""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPECTED = ("PASS_SPARSE_REDUNDANT_DECODER planes=32385 single_vectors=765 "
            "minimum=64 all_active=65 equality_shifts=4 controls=6 no_new_kappa\n")


def measure(program):
    argv = [sys.executable, "-I", "-O", "-W", "error", "-B", str(program)]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    result = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True, timeout=60)
    wall = time.perf_counter() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    if result.returncode or result.stdout != EXPECTED or result.stderr:
        raise ValueError("complete command failed: " + result.stdout + result.stderr)
    return {"wall_seconds": wall,
            "cpu_seconds": after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
            "exit_code": result.returncode, "stdout_sha256": hashlib.sha256(result.stdout.encode()).hexdigest()}


def summary(rows):
    values = [row["wall_seconds"] for row in rows]
    return {"median_seconds": statistics.median(values), "minimum_seconds": min(values),
            "maximum_seconds": max(values), "runs": rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, required=True)
    args = parser.parse_args()
    programs = [("source", ROOT / "research/sparse-redundant-decoder/verify.py"),
                ("kernel", HERE / "fast.py")]
    samples = {name: [] for name, _ in programs}
    for _ in range(5):
        for name, program in programs:
            samples[name].append(measure(program))
    result = {"python": sys.version, "platform": platform.platform(),
              "argv_flags": ["-I", "-O", "-W", "error", "-B"], "errors": 0,
              "order": ["source", "kernel"] * 5,
              "timing_scope": "whole subprocess including interpreter, source hashes, census, witnesses, controls and receipt comparison",
              **{name: summary(rows) for name, rows in samples.items()}}
    with args.write.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
