#!/usr/bin/env python3
"""Measure complete original/cached replays in alternating fresh processes.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
from statistics import median
import subprocess
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cached import SOURCE, SOURCE_SHA256, require


def sample(script, root):
    argv = [sys.executable, "-I", "-W", "error", "-B", str(script)]
    start = perf_counter()
    result = subprocess.run(argv, cwd=root, capture_output=True, timeout=120, check=False)
    seconds = perf_counter() - start
    require(result.returncode == 0 and not result.stderr, "replay failure")
    require(len(result.stdout) < 65536, "output capacity")
    digest = sha256(result.stdout).hexdigest()
    require(digest == "ba358675b3031aef57895701547380f864223c83ef89a9f44f039714f1a97fa0",
            "scientific output differs")
    return {"seconds": seconds, "returncode": result.returncode, "stdout_sha256": digest}


def measure(rounds):
    require(5 <= rounds <= 15, "benchmark rounds must be 5 through 15")
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    baseline = root / SOURCE
    require(sha256(baseline.read_bytes()).hexdigest() == SOURCE_SHA256, "source digest")
    rows = []
    for index in range(rounds):
        rows.append({"round": index + 1, "baseline": sample(baseline, root),
                     "cached": sample(package / "cached.py", root)})
    summaries = {}
    for side in ("baseline", "cached"):
        times = [row[side]["seconds"] for row in rows]
        summaries[side] = {"median_seconds": median(times), "min_seconds": min(times),
                           "max_seconds": max(times)}
    return {"schema_version": 1, "python": sys.version, "executable": sys.executable,
            "platform": platform.platform(), "machine": platform.machine(),
            "errors": 0, "rounds": rows, "summary": summaries,
            "source_sha256": SOURCE_SHA256,
            "implementation_sha256": sha256((package / "cached.py").read_bytes()).hexdigest(),
            "harness_sha256": sha256(Path(__file__).read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output:
        target = args.output.resolve()
        root = Path(__file__).resolve().parents[2]
        require(not target.is_relative_to(root), "benchmark output must be outside checkout")
        require(not target.exists(), "refuse overwrite")
    result = measure(args.rounds)
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
