#!/usr/bin/env python3
"""Time five alternating pairs of complete authenticated Dic3 replays."""

from __future__ import annotations

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


def one_run(baseline: bool) -> tuple[dict, bytes]:
    command = [sys.executable, "-I", "-W", "error", "-B", str(PACKAGE / "replay.py")]
    if baseline:
        command.append("--baseline")
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    start = time.perf_counter_ns()
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                            timeout=120, check=False)
    elapsed = time.perf_counter_ns() - start
    row = {"baseline": baseline, "elapsed_ns": elapsed,
           "returncode": result.returncode, "stderr_bytes": len(result.stderr),
           "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
           "command": command}
    if result.returncode or result.stderr:
        raise RuntimeError("complete replay failed: " + repr(row)
                           + result.stderr.decode(errors="replace"))
    if not result.stdout.startswith(b"PASS_DIC3_BOUNDED_DIAGONAL_SEARCH "):
        raise RuntimeError("complete replay omitted its scientific result")
    return row, result.stdout


def measure() -> dict:
    samples = []
    reference = None
    for index in range(10):
        row, output = one_run(index % 2 == 0)
        if reference is None:
            reference = output
        if output != reference:
            raise RuntimeError("complete scientific output changed")
        samples.append(row)
        print(index + 1, row["baseline"], row["elapsed_ns"], flush=True)
    groups = [[r["elapsed_ns"] for r in samples if r["baseline"] == side]
              for side in (True, False)]
    summaries = [{"median_ns": statistics.median(g), "min_ns": min(g),
                  "max_ns": max(g)} for g in groups]
    return {"schema": "dic3-shift-benchmark/v1", "samples": samples,
            "baseline": summaries[0], "prepared": summaries[1],
            "reduction_fraction": 1 - summaries[1]["median_ns"] / summaries[0]["median_ns"],
            "errors": 0, "identical_complete_outputs": 10,
            "stdout": reference.decode(), "python": sys.version,
            "platform": platform.platform(), "machine": platform.machine(),
            "cpu_count": os.cpu_count(), "load_average_at_end": os.getloadavg(),
            "source_hashes": {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                              for name in ("replay.py", "benchmark.py", "SOURCES.json")}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(ROOT):
        parser.error("write measurements outside the checkout")
    if args.output.exists():
        parser.error("output must be a new file")
    result = measure()
    with args.output.open("x") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print("PASS_DIC3_SHIFT_BENCHMARK", result["reduction_fraction"])


if __name__ == "__main__":
    main()
