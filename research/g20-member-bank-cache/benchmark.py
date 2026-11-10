"""Alternate complete fresh-process census commands; emit a hash-bound receipt.

Produced by Nick Petalas. Apache-2.0. Timing is a local observation.
"""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
SUCCESS = b"PASS independent complete normalized G20 census receipt\n"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def benchmark(pairs):
    if type(pairs) is not int or not 5 <= pairs <= 10:
        raise ValueError("Use five through ten alternating pairs")
    commands = {
        "original": [sys.executable, "-I", "-W", "error", "-B",
                     str(ROOT / "frozen" / "verify_full_census.py")],
        "cached": [sys.executable, "-I", "-W", "error", "-B", str(ROOT / "replay.py")],
    }
    rows, errors = [], []
    for pair in range(pairs):
        for side in ("original", "cached"):
            start = time.perf_counter()
            completed = subprocess.run(commands[side], capture_output=True, timeout=120, check=False)
            seconds = time.perf_counter() - start
            ok = completed.returncode == 0 and completed.stdout == SUCCESS and not completed.stderr
            rows.append({"pair": pair, "side": side, "seconds": seconds,
                         "returncode": completed.returncode, "output_matches": ok})
            if not ok:
                errors.append({"pair": pair, "side": side,
                               "stderr": completed.stderr.decode(errors="replace")[:4096]})
    if errors:
        raise ValueError("Benchmark process/output failures: " + json.dumps(errors))
    summary = {}
    for side in commands:
        values = [row["seconds"] for row in rows if row["side"] == side]
        summary[side] = {"median_seconds": statistics.median(values),
                         "minimum_seconds": min(values), "maximum_seconds": max(values)}
    gain = 1 - summary["cached"]["median_seconds"] / summary["original"]["median_seconds"]
    bindings = {"replay.py": digest(ROOT / "replay.py"),
                "benchmark.py": digest(ROOT / "benchmark.py"),
                "FROZEN.json": digest(ROOT / "FROZEN.json")}
    return {"status": "PASS_COMPLETE_CENSUS_BENCHMARK", "pairs": pairs,
            "python": sys.version, "platform": platform.platform(), "commands": commands,
            "errors": 0, "rows": rows, "summary": summary, "median_fraction_saved": gain,
            "bindings_sha256": bindings,
            "timing_boundary": "Before subprocess creation through complete exit and captured output; validation after timer.",
            "coverage": "Both commands recompute the complete census and compare FULL-CENSUS.json; all successes have exactly the source CLI output. Cached command also authenticates its seventeen frozen inputs.",
            "limits": "One shared macOS host, warm filesystem cache; no host-wide isolation or cross-host speed guarantee."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(benchmark(args.pairs), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
