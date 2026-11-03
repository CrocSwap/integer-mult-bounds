#!/usr/bin/env python3
"""Time complete source authentication; produced by Nick Petalas, Apache-2.0."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time


PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    args = parser.parse_args()
    require(5 <= args.rounds <= 20, "Use five through twenty rounds")
    root = PACKAGE.parents[1]
    require((root / "certificates/selected-result.json").read_bytes()
            == (PACKAGE / "selection.json").read_bytes(),
            "Official selection differs from this fixed benchmark")
    commands = {
        "reference": [sys.executable, "-I", "-W", "error", "-B",
                      str(root / "scripts/research_selected_baseline.py")],
        "prefix": [sys.executable, "-I", "-W", "error", "-B", str(PACKAGE / "fast.py")],
    }
    expected = None
    samples = {"reference": [], "prefix": []}
    for _ in range(args.rounds):
        for side in ("reference", "prefix"):
            start = time.perf_counter_ns()
            completed = subprocess.run(commands[side], capture_output=True, timeout=120, check=False)
            elapsed = (time.perf_counter_ns() - start) / 1_000_000_000
            require(completed.returncode == 0 and not completed.stderr,
                    "Complete command failed: " + completed.stderr.decode(errors="replace"))
            require(json.loads(completed.stdout)["status"] ==
                    "PASS_RESEARCH_BASELINE_BINDINGS_ONLY", "Authentication did not finish")
            digest = sha256(completed.stdout).hexdigest()
            expected = digest if expected is None else expected
            require(digest == expected, "Complete report bytes differ")
            samples[side].append(elapsed)
    medians = {side: statistics.median(values) for side, values in samples.items()}
    print(json.dumps({"status": "PASS_COMPLETE_BASELINE_BENCHMARK", "errors": 0,
                      "python": platform.python_version(), "platform": platform.platform(),
                      "rounds_per_side": args.rounds, "wall_seconds": samples,
                      "median_seconds": medians, "stdout_sha256": expected,
                      "median_reduction_fraction": 1 - medians["prefix"] / medians["reference"],
                      "scope": "Complete fresh-process frozen-selection source authentication; warm OS caches."
                      }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
