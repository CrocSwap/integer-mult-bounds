#!/usr/bin/env python3
"""Paired wall-time samples for production HPE integer-row audit.

Descriptive only: timing is not a correctness gate.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import io
import contextlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / (
    "research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/"
    "code/hpe_audit_and_transport.py"
)
BASELINE = PACKAGE / "baseline.py"
ARCHIVE = ROOT / "research/community-frontier1042-audit/selected-replay.tar.gz"
ROUTING = ROOT / (
    "research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/"
    "complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz"
)
WORDS = ("p6n", "promo", "jx", "hyb", "frames")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_five(module, words, tmp: Path) -> tuple[float, list]:
    receipts = []
    start = time.perf_counter()
    for name, data in words:
        raw = tmp / f"{name}.json.gz"
        raw.write_bytes(data)
        out = tmp / f"out-{name}-{time.time_ns()}"
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            module.run(raw, ROUTING, out)
        receipt = json.loads((out / "SCALAR-FRAME-AUDIT.json").read_text())
        receipt.pop("seconds", None)
        receipts.append(receipt)
    return time.perf_counter() - start, receipts


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args(argv)

    with tarfile.open(ARCHIVE) as archive:
        words = [(name, archive.extractfile(f"chain/{name}/FULL-WORD.json.gz").read()) for name in WORDS]

    base_times = []
    prod_times = []
    with tempfile.TemporaryDirectory(prefix="hpe-audit-bench-") as tmp:
        tmp_path = Path(tmp)
        for i in range(args.rounds):
            # Alternate order each round.
            order = ("baseline", "production") if i % 2 == 0 else ("production", "baseline")
            for engine in order:
                path = BASELINE if engine == "baseline" else PRODUCTION
                module = load_module(f"{engine}_{i}", path)
                work = tmp_path / f"r{i}-{engine}"
                work.mkdir(exist_ok=True)
                dt, receipts = run_five(module, words, work)
                if engine == "baseline":
                    base_times.append(dt)
                    base_receipts = receipts
                else:
                    prod_times.append(dt)
                    prod_receipts = receipts
            if base_receipts != prod_receipts:
                raise SystemExit("PASS gate failed: receipts diverged during benchmark")

    base_med = statistics.median(base_times)
    prod_med = statistics.median(prod_times)
    ratio = base_med / prod_med if prod_med else float("inf")
    result = {
        "schema_version": 1,
        "package": "research/hpe-audit-integer-production",
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "workload": "five honest FULL-WORD audits (p6n,promo,jx,hyb,frames)",
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
    print(json.dumps({
        "median_baseline_seconds": base_med,
        "median_production_seconds": prod_med,
        "median_speedup": ratio,
    }, indent=2), flush=True)
    print(
        f"PASS_IDENTICAL_HPE_AUDIT_INTEGER_PRODUCTION_RECEIPTS "
        f"median {base_med:.3f}->{prod_med:.3f}s ({ratio:.3f}x)",
        flush=True,
    )
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
