"""Measure complete fresh-process replays; author evidence outside the checkout."""
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
ROOT = PACKAGE.parent.parent


def bindings():
    names = ("adapter.py", "run.py", "verify.py", "benchmark.py", "SOURCES.json", "VERIFY.json")
    return {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() for name in names}


def sample(mode):
    command = [sys.executable, "-I", "-W", "error", "-B", str(PACKAGE / "run.py"), "--mode", mode]
    started = time.perf_counter()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=290, check=False)
    seconds = time.perf_counter() - started
    if result.returncode != 0:
        raise ValueError("complete replay failed: " + result.stderr.decode())
    counts = json.loads(result.stderr)
    if not result.stdout.startswith(b"PASS_CERTIFIED_GAUSSIAN_RECOVERY "):
        raise ValueError("missing completed scientific replay")
    return {"mode": mode, "seconds": seconds, "returncode": result.returncode,
            "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(), "counts": counts["counts"]}


def measure():
    records = []
    for _ in range(5):
        for mode in ("baseline", "reflected"):
            records.append(sample(mode))
    if len({r["stdout_sha256"] for r in records}) != 1:
        raise ValueError("complete scientific output changed")
    summary = {}
    for mode in ("baseline", "reflected"):
        selected = [r for r in records if r["mode"] == mode]
        times = [r["seconds"] for r in selected]
        if any(r["counts"] != selected[0]["counts"] for r in selected):
            raise ValueError("work count changed between repetitions")
        summary[mode] = {"median_seconds": statistics.median(times),
                         "minimum_seconds": min(times), "maximum_seconds": max(times),
                         "counts": selected[0]["counts"]}
    summary["reduction_percent"] = 100 * (1 - summary["reflected"]["median_seconds"] /
                                        summary["baseline"]["median_seconds"])
    return records, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    target = args.output.resolve()
    if ROOT == target or ROOT in target.parents or target.exists():
        raise ValueError("new output must be outside the checkout")
    environment = {"python": sys.version, "platform": platform.platform(),
                   "logical_cpus": os.cpu_count(), "initial_load": os.getloadavg()}
    records, summary = measure()
    report = {"status": "PASS_GAUSSIAN_REFLECTION_BENCHMARK", "errors": 0,
              "bindings": bindings(), "environment": environment,
              "records": records, "summary": summary}
    with target.open("x") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
