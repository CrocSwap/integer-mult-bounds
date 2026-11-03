"""Alternate complete original/adapted commands in fresh CPython processes."""

import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time

from adapter import PACKAGE, ROOT, require


def sample(mode, temporary):
    env = dict(os.environ)
    env["PYTHONPYCACHEPREFIX"] = str(temporary / mode)
    command = [sys.executable, "-W", "error", "-B", str(PACKAGE / "adapter.py"),
               "--mode", mode]
    start = time.perf_counter_ns()
    result = subprocess.run(command, capture_output=True, env=env, timeout=30, check=False)
    elapsed = time.perf_counter_ns() - start
    require(result.returncode == 0, "replay failed: " + result.stderr.decode())
    require(not result.stderr, "unexpected replay stderr")
    expected = (b"PASS_QUINARY_RESONANT_DISJOINTNESS_REPAIR\n"
                b"PASS_INDEPENDENT_QUINARY_TENSOR_AND_KERNEL\n")
    require(result.stdout == expected, "incomplete scientific output")
    return {"mode": mode, "seconds": elapsed / 10**9,
            "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(), "errors": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(5 <= args.rounds <= 15, "round count must be 5..15")
    output = args.output.resolve()
    require(not output.is_relative_to(ROOT), "measurements must stay outside checkout")
    require(output.parent.is_dir() and not output.exists(), "exclusive output required")
    samples = []
    with tempfile.TemporaryDirectory(prefix="rank-benchmark-", dir=output.parent) as name:
        for _ in range(args.rounds):
            for mode in ("original", "adapted"):
                samples.append(sample(mode, Path(name)))
    summary = {}
    for mode in ("original", "adapted"):
        values = [row["seconds"] for row in samples if row["mode"] == mode]
        summary[mode] = {"median_seconds": statistics.median(values),
                         "range_seconds": [min(values), max(values)]}
    report = {"python": sys.version, "platform": platform.platform(),
              "cpu_count": os.cpu_count(), "load_average": os.getloadavg(),
              "rounds": args.rounds, "samples": samples, "summary": summary,
              "errors": sum(row["errors"] for row in samples)}
    with output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
