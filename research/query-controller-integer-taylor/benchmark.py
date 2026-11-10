"""Alternate fresh complete processes and print a generated timing report."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
from statistics import median
import subprocess
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent


def sample(mode):
    command = [sys.executable, "-I", "-W", "error", "-B", str(HERE / "caller.py"), mode]
    start = perf_counter()
    process = subprocess.run(command, check=False, capture_output=True, timeout=120)
    elapsed = perf_counter() - start
    if process.returncode:
        raise RuntimeError(process.stderr.decode(errors="replace"))
    payload = json.loads(process.stdout)
    scientific = json.dumps(payload["result"], sort_keys=True, separators=(",", ":")).encode()
    if payload["mode"] != mode or payload["work"]["exponential_calls"] == 0:
        raise ValueError("measured arithmetic did not execute")
    return elapsed, sha256(scientific).hexdigest(), {**payload["work"], "trace_sha256": payload["trace_sha256"]}


def benchmark(pairs):
    if type(pairs) is not int or not 5 <= pairs <= 10:
        raise ValueError("five to ten alternating pairs required")
    samples = {"baseline": [], "candidate": []}
    expected = None
    for _ in range(pairs):
        for mode in ("baseline", "candidate"):
            elapsed, digest, work = sample(mode)
            if expected is None:
                expected = digest, work
            if expected != (digest, work):
                raise ValueError("complete scientific output or work changed")
            samples[mode].append(elapsed)
    summary = {mode: {"median_seconds": median(times), "range_seconds": [min(times), max(times)]}
               for mode, times in samples.items()}
    return {"python": platform.python_version(), "platform": platform.platform(), "pairs": pairs,
            "errors": 0, "samples_seconds": samples, "summary": summary,
            "fractional_time_reduction": 1 - summary["candidate"]["median_seconds"] / summary["baseline"]["median_seconds"],
            "scientific_sha256": expected[0], "work_per_process": expected[1]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(benchmark(args.pairs), indent=2, sort_keys=True))
