"""Alternate complete fresh-process replays and check every outcome."""

import argparse
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from replay import PACKAGE, ROOT, SOURCE, check_sources
from verify import complete_conformance


def measure(script: str, cache: str) -> float:
    command = [sys.executable, "-X", f"pycache_prefix={cache}", "-W", "error", "-B", script]
    environment = dict(os.environ)
    environment.pop("PYTHONOPTIMIZE", None)
    start = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, timeout=30)
    elapsed = time.perf_counter() - start
    if result.returncode or result.stderr:
        raise ValueError(f"replay failed: {result.returncode}: {result.stderr!r}")
    if result.stdout != b"PASS_Q_TOEPLITZ_FACTORIZATION matrices=30 no_new_kappa\n":
        raise ValueError("complete replay output changed")
    return elapsed


def benchmark(rounds: int) -> dict:
    check_sources()  # Admit all sources before any timing starts.
    if not 5 <= rounds <= 31:
        raise ValueError("rounds must be in 5..31")
    samples = {"reference": [], "candidate": []}
    scripts = {"reference": SOURCE, "candidate": "research/q-toeplitz-zero-products/replay.py"}
    with tempfile.TemporaryDirectory(prefix="q-toeplitz-benchmark-") as cache:
        for _ in range(rounds):
            for name in ("reference", "candidate"):
                samples[name].append(measure(scripts[name], cache))
    summary = {
        name: {"median_seconds": statistics.median(values), "range_seconds": [min(values), max(values)]}
        for name, values in samples.items()
    }
    return {
        "python": sys.executable, "version": platform.python_version(),
        "platform": platform.platform(), "rounds_per_side": rounds, "errors": 0,
        "timed_region": "fresh interpreter, all imports, all 30 matrices, every retained check and stdout",
        "commands": {name: ["{python}", "-W", "error", "-B", script] for name, script in scripts.items()},
        "cache_policy": "-B and one fresh private bytecode namespace for both sides; no result cache",
        "samples_seconds": samples, "summary": summary,
        "work": complete_conformance(),
        "files_sha256": {name: hashlib.sha256((PACKAGE/name).read_bytes()).hexdigest()
                         for name in ("kernel.py", "replay.py", "verify.py", "benchmark.py", "SOURCES.json")},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=15)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("refusing to overwrite benchmark output")
    result = benchmark(args.rounds)
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], sort_keys=True))
    print("PASS_COMPLETE_Q_TOEPLITZ_BENCHMARK errors=0")


if __name__ == "__main__":
    main()
