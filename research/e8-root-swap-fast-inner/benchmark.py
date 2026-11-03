"""Time complete fresh-process commands; write the generated evidence to stdout.

Produced by Nick Petalas. Apache-2.0. Timings are local observations only.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
from time import perf_counter_ns

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replay


def measure(argv, root):
    start = perf_counter_ns()
    process = subprocess.run(argv, cwd=root, capture_output=True, timeout=120,
                             check=False)
    elapsed = perf_counter_ns() - start
    correct = (process.returncode == 0 and process.stderr == b""
               and process.stdout == replay.EXPECTED.encode())
    return {"elapsed_ns": elapsed, "returncode": process.returncode,
            "correct": correct, "stdout_sha256": sha256(process.stdout).hexdigest(),
            "stderr": process.stderr.decode("utf-8", errors="replace")}


def benchmark(pairs):
    replay.require(5 <= pairs <= 15, "pairs must be between five and fifteen")
    root = replay.PACKAGE.parents[1]
    before = replay.authenticated_inputs(root)
    flags = [sys.executable, "-I", "-W", "error", "-B"]
    commands = {
        "baseline": flags + [str(root / replay.SOURCE / "verify.py")],
        "fast": flags + [str(replay.PACKAGE / "replay.py")],
    }
    rows = []
    for pair in range(pairs):
        for side in ("baseline", "fast"):
            rows.append({"pair": pair + 1, "side": side,
                         **measure(commands[side], root)})
    replay.require(replay.authenticated_inputs(root) == before,
                   "scientific inputs changed during measurement")
    failures = sum(not row["correct"] for row in rows)
    summary = {}
    for side in commands:
        values = [row["elapsed_ns"] for row in rows if row["side"] == side]
        summary[side] = {"median_ns": statistics.median(values),
                         "min_ns": min(values), "max_ns": max(values)}
    return {"schema_version": 1, "python": sys.version,
            "platform": platform.platform(), "cpu_count": os.cpu_count(),
            "load_average": list(os.getloadavg()), "commands": commands,
            "pairs": pairs, "complete_replays": len(rows), "failures": failures,
            "summary": summary, "runs": rows,
            "fraction_less_wall_time": 1 - summary["fast"]["median_ns"]
            / summary["baseline"]["median_ns"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=5)
    args = parser.parse_args()
    result = benchmark(args.pairs)
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(result["failures"] != 0)


if __name__ == "__main__":
    raise SystemExit(main())
