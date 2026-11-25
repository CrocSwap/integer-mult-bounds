#!/usr/bin/env python3
"""Alternating fresh-process before/after timings for production geometry-cache mutants.

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
XCHECK = ROOT / "research/e8-bit-r420/code/xcheck.py"
BASELINE = PACKAGE / "baseline.py"
PRODUCTION = ROOT / "research/e8-bit-r420/code/mutants.py"

MUTANTS_STDOUT_SHA256 = "8c2738b3258e207370597b60c2ebd318e740fc0feaca04cb8b0e3a26089258d8"


def clean_env():
    env = {k: v for k, v in os.environ.items() if k != "PYTHONOPTIMIZE"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_workload(engine: str) -> dict:
    harness = BASELINE if engine == "baseline" else PRODUCTION
    cmd = [sys.executable, "-I", "-B", str(harness), str(XCHECK), str(WORD)]
    start = time.perf_counter()
    proc = subprocess.run(cmd, cwd=ROOT, env=clean_env(), capture_output=True)
    elapsed = time.perf_counter() - start
    if proc.returncode != 0:
        raise SystemExit(f"{engine} failed\n{proc.stderr.decode()}\n{proc.stdout.decode()}")
    digest = sha256(proc.stdout).hexdigest()
    if digest != MUTANTS_STDOUT_SHA256:
        raise SystemExit(f"{engine} stdout digest {digest} != {MUTANTS_STDOUT_SHA256}")
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

    records = []
    for pair in range(args.rounds):
        order = ("baseline", "production") if pair % 2 == 0 else ("production", "baseline")
        outputs = {}
        for engine in order:
            row = run_workload(engine)
            records.append(
                {
                    "pair": pair,
                    "engine": engine,
                    "seconds": row["elapsed"],
                    "stdout_sha256": row["stdout_sha256"],
                }
            )
            outputs[engine] = row["stdout_sha256"]
            print(
                f"pair={pair} engine={engine} seconds={row['elapsed']:.6f}",
                flush=True,
            )
        if outputs["baseline"] != outputs["production"]:
            raise SystemExit(f"pair {pair} receipts differ")

    medians = {
        engine: statistics.median(r["seconds"] for r in records if r["engine"] == engine)
        for engine in ("baseline", "production")
    }
    result = {
        "status": "PASS_IDENTICAL_R420_GEOMETRY_CACHE_PRODUCTION_RECEIPTS",
        "no_new_kappa": True,
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "interpreter": f"CPython {platform.python_version()}",
        "rounds": args.rounds,
        "timing_scope": (
            "fresh subprocess wall time for the complete mutants.py harness "
            "(1 honest + 9 negative + 1 positive) including imports; warm OS caches, "
            "not flushed; host-descriptive only; not a correctness gate"
        ),
        "records": records,
        "median_seconds": medians,
        "speedup": medians["baseline"] / medians["production"],
        "mutants_stdout_sha256": MUTANTS_STDOUT_SHA256,
        "production_mutants_sha256": sha256(PRODUCTION.read_bytes()).hexdigest(),
        "baseline_mutants_sha256": sha256(BASELINE.read_bytes()).hexdigest(),
        "xcheck_sha256": sha256(XCHECK.read_bytes()).hexdigest(),
    }

    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    json.loads(text, object_pairs_hook=unique_object)
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(text, encoding="utf-8")
    print(result["status"])
    print(
        "controls",
        medians,
        "speedup",
        round(result["speedup"], 3),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
