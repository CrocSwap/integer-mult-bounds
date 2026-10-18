#!/usr/bin/env python3
"""Paired wall-time samples for production P112 signed modular determinants.

Descriptive only: timing is not a correctness gate.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research/p112-free-sink-audit97/independent.py"
BASELINE = PACKAGE / "baseline.py"
CERTIFICATE = ROOT / "research/p112-free-sink-audit97/CERTIFICATE.json"
BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise SystemExit(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_checker(name: str, source: Path):
    module = types.ModuleType(name)
    module.__file__ = str(PRODUCTION)
    exec(compile(source.read_bytes(), str(PRODUCTION), "exec", optimize=0), module.__dict__)
    return module


def run_once(module, certificate) -> tuple[float, dict]:
    start = time.perf_counter()
    result = module.audit(certificate)
    elapsed = time.perf_counter() - start
    return elapsed, result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args(argv)

    certificate = json.loads(CERTIFICATE.read_bytes(), object_pairs_hook=unique_object)
    base_times = []
    prod_times = []
    expected = None
    for i in range(args.rounds):
        order = ("baseline", "production") if i % 2 == 0 else ("production", "baseline")
        receipts = {}
        for engine in order:
            path = BASELINE if engine == "baseline" else PRODUCTION
            module = load_checker(f"{engine}_{i}", path)
            dt, receipt = run_once(module, certificate)
            receipts[engine] = receipt
            if engine == "baseline":
                base_times.append(dt)
            else:
                prod_times.append(dt)
        if receipts["baseline"] != receipts["production"]:
            raise SystemExit("PASS gate failed: receipts diverged during benchmark")
        if expected is None:
            expected = receipts["baseline"]
        elif receipts["baseline"] != expected:
            raise SystemExit("PASS gate failed: audit receipt changed across rounds")

    base_med = statistics.median(base_times)
    prod_med = statistics.median(prod_times)
    ratio = base_med / prod_med if prod_med else float("inf")
    per_round = [b / p for b, p in zip(base_times, prod_times)]
    result = {
        "schema_version": 1,
        "status": "PASS_IDENTICAL_P112_SIGNED_MODULAR_PRODUCTION_RECEIPTS",
        "package": "research/p112-signed-modular-production",
        "base_commit": BASE_COMMIT,
        "workload": "complete P112 free-sink independent audit (28560 cases, 4030 signed minors)",
        "rounds": args.rounds,
        "baseline_seconds": base_times,
        "production_seconds": prod_times,
        "per_round_ratio": per_round,
        "median_baseline_seconds": base_med,
        "median_production_seconds": prod_med,
        "median_speedup": ratio,
        "min_per_round_ratio": min(per_round),
        "max_per_round_ratio": max(per_round),
        "audit_receipt": expected,
        "baseline_sha256": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
        "production_sha256": hashlib.sha256(PRODUCTION.read_bytes()).hexdigest(),
        "python": sys.version,
        "platform": platform.platform(),
        "note": (
            "Host-descriptive; not a correctness gate. Times cover audit() after module load "
            "(geometry, code coverage, all exact minors/cases); exclude interpreter startup "
            "and package pin hashing. Receipts identical each round."
        ),
    }
    text = json.dumps(result, indent=2) + "\n"
    print(text, end="")
    print(
        "PASS_IDENTICAL_P112_SIGNED_MODULAR_PRODUCTION_RECEIPTS "
        f"rounds={args.rounds} "
        f"median {base_med:.3f}->{prod_med:.3f}s "
        f"({ratio:.3f}×; per-round {min(per_round):.3f}–{max(per_round):.3f}×)",
        flush=True,
    )
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
