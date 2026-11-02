"""Alternate complete fresh-process replays and emit a source-bound receipt."""

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


HERE = Path(__file__).resolve().parent
EXPECTED = b"PASS exact relative tariff threshold and retained receipt\n"


def inputs() -> dict[str, str]:
    origin = json.loads((HERE / "ORIGINS.json").read_bytes())
    names = ["benchmark.py", "exp_series.py", "replay.py", "ORIGINS.json"]
    names.extend("source/" + row["path"] for row in origin["files"])
    return {name: sha256((HERE / name).read_bytes()).hexdigest() for name in names}


def sample(arm: str) -> dict:
    command = [sys.executable, "-I", "-W", "error", "-B",
               str(HERE / "replay.py"), "--arm", arm]
    start = time.perf_counter_ns()
    result = subprocess.run(command, capture_output=True, timeout=30, check=False)
    elapsed = time.perf_counter_ns() - start
    if result.returncode != 0 or result.stderr or result.stdout != EXPECTED:
        raise RuntimeError("complete replay failed: " + repr(result))
    return {"arm": arm, "nanoseconds": elapsed, "exit_code": result.returncode,
            "stdout_sha256": sha256(result.stdout).hexdigest(), "stderr_bytes": 0}


def benchmark(pairs: int) -> dict:
    if type(pairs) is not int or not 5 <= pairs <= 15:
        raise ValueError("benchmark requires 5..15 alternating pairs")
    before = inputs()
    warmups = [sample(arm) for arm in ("original", "integer")]
    observations = [sample(arm) for _ in range(pairs)
                    for arm in ("original", "integer")]
    if inputs() != before:
        raise RuntimeError("benchmark inputs changed during measurement")
    summaries = {}
    for arm in ("original", "integer"):
        times = [row["nanoseconds"] for row in observations if row["arm"] == arm]
        summaries[arm] = {"median_ns": statistics.median(times),
                          "min_ns": min(times), "max_ns": max(times)}
    return {"schema_version": 1, "python": sys.version, "executable": sys.executable,
            "platform": platform.platform(), "cpu_count": os.cpu_count(),
            "load_average": list(os.getloadavg()), "pairs": pairs,
            "command": "{python} -I -W error -B {package}/replay.py --arm {arm}",
            "inputs": before, "warmups": warmups, "samples": observations,
            "summary": summaries, "failures": 0,
            "reduction_fraction": 1 - summaries["integer"]["median_ns"] /
            summaries["original"]["median_ns"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=9)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("benchmark receipt path already exists")
    report = benchmark(args.pairs)
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"summary": report["summary"],
                      "reduction_fraction": report["reduction_fraction"]}))
