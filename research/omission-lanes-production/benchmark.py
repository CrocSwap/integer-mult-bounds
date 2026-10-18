#!/usr/bin/env python3
"""Paired wall-time samples for production packed R439 omission atlas.

Descriptive only: timing is not a correctness gate.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research/r439-omission-atlas-seed81/verify.py"
BASELINE = PACKAGE / "baseline.py"
CERTIFICATE = ROOT / "research/r439-omission-atlas-seed81/CERTIFICATE.json"
BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"


def load_checker(name: str, source: Path):
    module = types.ModuleType(name)
    module.__file__ = str(PRODUCTION)
    exec(compile(source.read_bytes(), str(PRODUCTION), "exec", optimize=0), module.__dict__)
    return module


def run_once(module) -> tuple[float, bytes]:
    start = time.perf_counter()
    result = module.run()
    elapsed = time.perf_counter() - start
    module.need(
        module.canonical(module.load(module.canonical(result)))
        == module.canonical(module.load(CERTIFICATE.read_bytes())),
        "certificate mismatch",
    )
    return elapsed, module.canonical(result)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args(argv)

    base_times = []
    prod_times = []
    for i in range(args.rounds):
        order = ("baseline", "production") if i % 2 == 0 else ("production", "baseline")
        receipts = {}
        for engine in order:
            path = BASELINE if engine == "baseline" else PRODUCTION
            module = load_checker(f"{engine}_{i}", path)
            dt, receipt = run_once(module)
            receipts[engine] = receipt
            if engine == "baseline":
                base_times.append(dt)
            else:
                prod_times.append(dt)
        if receipts["baseline"] != receipts["production"]:
            raise SystemExit("PASS gate failed: receipts diverged during benchmark")

    base_med = statistics.median(base_times)
    prod_med = statistics.median(prod_times)
    ratio = base_med / prod_med if prod_med else float("inf")
    result = {
        "schema_version": 1,
        "package": "research/omission-lanes-production",
        "base_commit": BASE_COMMIT,
        "workload": "complete R439 omission atlas (5563 literal single-ADD mutants)",
        "rounds": args.rounds,
        "baseline_seconds": base_times,
        "production_seconds": prod_times,
        "median_baseline_seconds": base_med,
        "median_production_seconds": prod_med,
        "median_speedup": ratio,
        "baseline_sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
        "production_sha256": hashlib.sha256(PRODUCTION.read_bytes()).hexdigest(),
        "python": sys.version,
        "platform": os.uname().sysname + " " + os.uname().release,
        "note": "Host-descriptive; not a correctness gate. Receipts identical each round.",
    }
    print(
        json.dumps(
            {
                "median_baseline_seconds": base_med,
                "median_production_seconds": prod_med,
                "median_speedup": ratio,
            },
            indent=2,
        ),
        flush=True,
    )
    print(
        "PASS_IDENTICAL_OMISSION_LANES_PRODUCTION_RECEIPTS "
        f"rounds={args.rounds} median_speedup={ratio:.6f}",
        flush=True,
    )
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
