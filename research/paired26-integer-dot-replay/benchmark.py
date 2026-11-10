#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Alternate complete fresh-process commands; timings are local evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def timed(script: Path) -> tuple[float, bytes]:
    command = [sys.executable, "-I", "-W", "error", "-B", str(script)]
    started = time.perf_counter_ns()
    process = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
    elapsed = (time.perf_counter_ns() - started) / 1_000_000_000
    if process.returncode or process.stderr:
        raise RuntimeError("failed benchmark command: " + repr(process))
    if not process.stdout.startswith(b"PASS_FIXED_PAIRED26_MINIMUM_62\n"):
        raise RuntimeError("complete success output absent")
    return elapsed, process.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=9, choices=range(5, 16))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(ROOT):
        raise ValueError("benchmark output must be outside checkout")
    scripts = {"original": ROOT / "research/complex-paired26-completion/verify.py",
               "integer": PACKAGE / "replay.py"}
    rows, expected = [], None
    for pair in range(args.pairs):
        order = ("original", "integer") if pair % 2 == 0 else ("integer", "original")
        row = {}
        for engine in order:
            elapsed, output = timed(scripts[engine])
            if expected is None:
                expected = output
            if output != expected:
                raise RuntimeError("complete stdout disagreement")
            row[engine] = elapsed
        rows.append(row)
    medians = {name: statistics.median(row[name] for row in rows) for name in scripts}
    report = {"python": sys.version, "platform": platform.platform(),
              "executable": sys.executable, "pairs": rows, "medians": medians,
              "ranges": {name: [min(r[name] for r in rows), max(r[name] for r in rows)]
                         for name in scripts}, "failures": 0,
              "stdout_sha256": hashlib.sha256(expected).hexdigest(),
              "reduction_percent": 100 * (1 - medians["integer"] / medians["original"])}
    inputs = [*scripts.values(), ROOT / "research/complex-paired26-completion/certificate.json"]
    report["sha256"] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                        for path in inputs}
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
