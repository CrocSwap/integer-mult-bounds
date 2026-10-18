#!/usr/bin/env python3
"""Verify exact coverage, then benchmark alternating fresh-process A/B pairs."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import tempfile
import time

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from replay import check_sources, require


def run(args, timeout=120):
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    result = subprocess.run([sys.executable, "-I", "-B", *map(str, args)],
                            capture_output=True, timeout=timeout)
    wall = time.perf_counter() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    require(result.returncode == 0,
            "Child failed: " + " ".join(map(str, args)) + "\n" + result.stderr.decode())
    return result, {"wall_seconds": wall,
                    "child_cpu_seconds": (after.ru_utime + after.ru_stime
                                          - before.ru_utime - before.ru_stime),
                    "stdout_sha256": sha256(result.stdout).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=7)
    parser.add_argument("--output", type=Path, required=True, help="Fresh result JSON path")
    args = parser.parse_args()
    require(args.pairs >= 3, "Use at least three alternating-order benchmark pairs")
    require(not args.output.exists(), "Output already exists; choose a fresh path")
    source = check_sources()
    expected = (PACKAGE / "EXPECTED.json").read_bytes()
    test_result, tests = run([PACKAGE / "test_kernel.py"])
    print(test_result.stderr.decode(), end="", flush=True)
    receipts = []
    with tempfile.TemporaryDirectory(prefix="joint-frame-rank-") as tmp:
        work = Path(tmp)
        for engine in ("reference", "screened"):
            outcome, receipt = run([PACKAGE / "replay.py", "--engine", engine, "--tests"])
            receipts.append({"engine": engine, "kind": "unchanged historical tests", **receipt})
        rank_stats = work / "per-rank.json"
        outcome, per_rank = run([PACKAGE / "replay.py", "--check-every-rank", "--stats", rank_stats])
        require(outcome.stdout == expected, "Per-matrix replay differs from full certificate")
        compared = json.loads(rank_stats.read_text())
        require(compared["calls"] == compared["individually_compared"] == 2644,
                "Unexpected rank coverage")
        # Inherited assertions may not be disabled, even if this new kernel
        # happens to use explicit checks itself.
        rejected = subprocess.run([sys.executable, "-I", "-O", "-B", str(PACKAGE / "replay.py")],
                                  capture_output=True, timeout=10)
        require(rejected.returncode != 0 and b"assertions must remain enabled" in rejected.stderr,
                "Optimized interpreter was not rejected")
        samples = []
        for pair in range(args.pairs):
            order = ("reference", "screened") if pair % 2 == 0 else ("screened", "reference")
            for engine in order:
                stats_path = work / f"{pair}-{engine}.json"
                result, timing = run([PACKAGE / "replay.py", "--engine", engine, "--stats", stats_path])
                require(result.stdout == expected, "Timed full certificate differs")
                stats = json.loads(stats_path.read_text())
                require(stats["calls"] == 2644, "Timed rank-call coverage differs")
                samples.append({"pair": pair, "engine": engine, "stats": stats, **timing})
            print(f"PASS exact full-certificate pair {pair + 1}/{args.pairs}", flush=True)
    medians = {engine: {metric: statistics.median(s[metric] for s in samples if s["engine"] == engine)
                        for metric in ("wall_seconds", "child_cpu_seconds")}
               for engine in ("reference", "screened")}
    speedups = {metric: medians["reference"][metric] / medians["screened"][metric]
                for metric in ("wall_seconds", "child_cpu_seconds")}
    record = {"status": "PASS_JOINT_FRAME_MODULAR_SCREEN", "base_commit": source["base_commit"],
              "assignment_seed": 85, "prime": 101,
              "python": sys.version, "platform": platform.platform(),
              "processor": platform.processor(),
              "expected_certificate_sha256": sha256(expected).hexdigest(),
              "source_manifest_sha256": sha256((PACKAGE / "SOURCE.json").read_bytes()).hexdigest(),
              "implementation_sha256": {name: sha256((PACKAGE / name).read_bytes()).hexdigest()
                                         for name in ("kernel.py", "replay.py", "test_kernel.py", "verify.py")},
              "focused_tests": tests, "historical_tests": receipts,
              "per_rank_comparison": {**per_rank, "stats": compared},
              "optimized_interpreter_rejected": True, "samples": samples,
              "medians": medians, "speedups": speedups,
              "scope": "Historical joint-frame certificate and 8 unchanged tests; not the selected supplier replay or the general multiplication theorem"}
    with args.output.open("x") as stream:
        stream.write(json.dumps(record, sort_keys=True, indent=2) + "\n")
    print("PASS_JOINT_FRAME_MODULAR_SCREEN", json.dumps({"medians": medians, "speedups": speedups}))


if __name__ == "__main__":
    main()
