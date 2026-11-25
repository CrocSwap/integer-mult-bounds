#!/usr/bin/env python3
"""Alternating fresh-process before/after timings for production integer RREF.

Timing is descriptive evidence for RESULT.json. Equivalence is enforced by
verify.py; this script fails only on unequal receipts or subprocess errors.
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
import time

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WORD = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
MUTANTS = ROOT / "research/e8-bit-r420/code/mutants.py"
BASELINE = PACKAGE / "baseline.py"
PRODUCTION = ROOT / "research/e8-bit-r420/code/xcheck.py"

CHECK_STDOUT_SHA256 = "e4637c1fe38b10fb82e0e4f710a28821e980f629ad3e22b51c1e75b3cdf40acd"
MUTANTS_STDOUT_SHA256 = "8c2738b3258e207370597b60c2ebd318e740fc0feaca04cb8b0e3a26089258d8"


def clean_env():
    env = {k: v for k, v in os.environ.items() if k != "PYTHONOPTIMIZE"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_workload(engine: str, suite: str) -> dict:
    script = BASELINE if engine == "baseline" else PRODUCTION
    if suite == "check":
        cmd = [sys.executable, "-I", "-B", str(script), str(WORD)]
        expected = CHECK_STDOUT_SHA256
    elif suite == "controls":
        cmd = [sys.executable, "-I", "-B", str(MUTANTS), str(script), str(WORD)]
        expected = MUTANTS_STDOUT_SHA256
    else:
        raise SystemExit(f"unknown suite {suite}")
    start = time.perf_counter()
    proc = subprocess.run(cmd, cwd=ROOT, env=clean_env(), capture_output=True)
    elapsed = time.perf_counter() - start
    if proc.returncode != 0:
        raise SystemExit(f"{engine}/{suite} failed\n{proc.stderr.decode()}\n{proc.stdout.decode()}")
    digest = sha256(proc.stdout).hexdigest()
    if digest != expected:
        raise SystemExit(f"{engine}/{suite} stdout digest {digest} != {expected}")
    return {"elapsed": elapsed, "stdout_sha256": digest, "stdout_bytes": len(proc.stdout)}


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise SystemExit(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument(
        "--write-result",
        action="store_true",
        help="write RESULT.json (default prints only; use explicitly to refresh the artifact)",
    )
    args = parser.parse_args(argv)
    if args.rounds < 3:
        raise SystemExit("Use at least three alternating rounds")

    workloads = {}
    for suite in ("check", "controls"):
        records = []
        for pair in range(args.rounds):
            order = ("baseline", "production") if pair % 2 == 0 else ("production", "baseline")
            outputs = {}
            for engine in order:
                row = run_workload(engine, suite)
                records.append(
                    {
                        "pair": pair,
                        "engine": engine,
                        "seconds": row["elapsed"],
                        "stdout_sha256": row["stdout_sha256"],
                    }
                )
                outputs[engine] = row["stdout_sha256"]
            if outputs["baseline"] != outputs["production"]:
                raise SystemExit(f"pair {pair} suite {suite} receipts differ")
        medians = {
            engine: statistics.median(r["seconds"] for r in records if r["engine"] == engine)
            for engine in ("baseline", "production")
        }
        workloads[suite] = {
            "records": records,
            "median_seconds": medians,
            "speedup": medians["baseline"] / medians["production"],
        }

    result = {
        "status": "PASS_IDENTICAL_R420_RREF_PRODUCTION_RECEIPTS",
        "no_new_kappa": True,
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "interpreter": f"CPython {platform.python_version()}",
        "rounds": args.rounds,
        "timing_scope": (
            "fresh subprocess wall time including imports; warm OS caches, not flushed; "
            "host-descriptive only; not a correctness gate"
        ),
        "workloads": workloads,
        "suite_median_seconds": {
            "baseline": statistics.median(
                [
                    workloads["check"]["median_seconds"]["baseline"],
                    workloads["controls"]["median_seconds"]["baseline"],
                ]
            ),
            # Not a combined suite wall; retained for readability alongside per-workload medians.
        },
        "check_speedup": workloads["check"]["speedup"],
        "controls_speedup": workloads["controls"]["speedup"],
        "production_xcheck_sha256": sha256(PRODUCTION.read_bytes()).hexdigest(),
        "baseline_xcheck_sha256": sha256(BASELINE.read_bytes()).hexdigest(),
    }

    # Combined alternating wall for check+controls in one process pair is not claimed;
    # report the product of the two medians only as a descriptive sum of stage medians.
    result["stage_median_sum_seconds"] = {
        "baseline": (
            workloads["check"]["median_seconds"]["baseline"]
            + workloads["controls"]["median_seconds"]["baseline"]
        ),
        "production": (
            workloads["check"]["median_seconds"]["production"]
            + workloads["controls"]["median_seconds"]["production"]
        ),
    }
    result["stage_median_sum_speedup"] = (
        result["stage_median_sum_seconds"]["baseline"]
        / result["stage_median_sum_seconds"]["production"]
    )

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    # Reject duplicate keys if re-parsed.
    json.loads(text, object_pairs_hook=unique_object)
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(text, encoding="utf-8")
    print(result["status"])
    print(
        "check",
        workloads["check"]["median_seconds"],
        "speedup",
        round(workloads["check"]["speedup"], 3),
    )
    print(
        "controls",
        workloads["controls"]["median_seconds"],
        "speedup",
        round(workloads["controls"]["speedup"], 3),
    )
    print(
        "stage_median_sum",
        result["stage_median_sum_seconds"],
        "speedup",
        round(result["stage_median_sum_speedup"], 3),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
