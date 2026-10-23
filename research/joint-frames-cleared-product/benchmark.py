#!/usr/bin/env python3
"""Alternating fresh-process before/after timing for the positive-side audit.

Timing is descriptive and never a correctness gate. Receipts must match
fieldwise between baseline and optimized workers.
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
sys.path.insert(0, str(ROOT / "scripts"))
from certify import require  # noqa: E402

WORKER = r'''
import json, sys, time
from hashlib import sha256
from pathlib import Path

root = Path(sys.argv[1])
mode = sys.argv[2]
sys.path.insert(0, str(root / "scripts"))

import importlib.util

if mode == "baseline":
    spec = importlib.util.spec_from_file_location(
        "baseline_jf", root / "research/joint-frames-cleared-product/baseline.py"
    )
    jf = importlib.util.module_from_spec(spec)
    sys.modules["baseline_jf"] = jf
    spec.loader.exec_module(jf)
else:
    import audit_joint_frames as jf

import experiments.positive_side_core as positive_side_core
import experiments.rank_product_core as rank_product_core
from experiments.positive_side_core import PositiveSide
from experiments.signed_sparse_core import vectors

positive_side_core.product = jf.product
rank_product_core.product = jf.product
if hasattr(jf.rank, "cache_clear"):
    jf.rank.cache_clear()

t0 = time.perf_counter()
rows = []
for h, q in ((4, 2), (5, 2), (4, 4), (5, 4), (6, 4), (8, 8)):
    labels = list(vectors(h, q))
    bit_rows = [
        sum(
            1 << j
            for j, y in enumerate(labels)
            if i == j or sum(a * b for a, b in zip(x, y)) == 0
        )
        for i, x in enumerate(labels)
    ]
    for strategy in ("balanced", "frequent-pairs"):
        c = PositiveSide(bit_rows, labels, strategy)
        record = c.verify()
        invocation = c.verify_invocation()
        frames = c.verify_frames() if strategy == "frequent-pairs" else None
        dag = sha256(
            json.dumps(dict(args=c.args, outputs=c.outputs), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        rows.append(
            dict(
                h=h,
                q=q,
                strategy=strategy,
                side_roles=record["side_roles"],
                additions=record["additions"],
                dag_sha256=dag,
                independent_roles=invocation["independent_roles"],
                frames_transitions=(frames or {}).get("distinct_transitions"),
            )
        )
elapsed = time.perf_counter() - t0
print(json.dumps(dict(mode=mode, elapsed=elapsed, rows=rows), sort_keys=True))
'''


def run_worker(mode: str) -> dict:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("PYTHONOPTIMIZE", None)
    proc = subprocess.run(
        [sys.executable, "-I", "-B", "-c", WORKER, str(ROOT), mode],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout.strip().splitlines()[-1])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    require(args.rounds >= 1, "rounds must be positive")

    for _ in range(args.warmup):
        run_worker("baseline")
        run_worker("optimized")

    samples = []
    for i in range(args.rounds):
        order = ("baseline", "optimized") if i % 2 == 0 else ("optimized", "baseline")
        pair = {}
        for mode in order:
            pair[mode] = run_worker(mode)
        require(
            pair["baseline"]["rows"] == pair["optimized"]["rows"],
            f"receipt mismatch in pair {i}",
        )
        samples.append(
            dict(
                pair=i,
                order=list(order),
                baseline_seconds=pair["baseline"]["elapsed"],
                optimized_seconds=pair["optimized"]["elapsed"],
                rows=pair["optimized"]["rows"],
            )
        )

    base_med = statistics.median(s["baseline_seconds"] for s in samples)
    opt_med = statistics.median(s["optimized_seconds"] for s in samples)
    ratio = base_med / opt_med if opt_med else None
    payload = dict(
        status="PASS_IDENTICAL_POSITIVE_SIDE_RECEIPTS",
        fixture="scripts/audit_positive_side.py experiment stream (h,q) in {(4,2),(5,2),(4,4),(5,4),(6,4),(8,8)}",
        rounds=args.rounds,
        warmup=args.warmup,
        median_baseline_seconds=base_med,
        median_optimized_seconds=opt_med,
        median_speedup_ratio=ratio,
        samples=samples,
        environment=dict(
            python=sys.version,
            platform=platform.platform(),
            executable=sys.executable,
        ),
        note="Timing is host-descriptive and is not a correctness gate.",
        no_new_kappa=True,
    )
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        require(not args.output.exists(), f"output exists: {args.output}")
        args.output.write_text(text, encoding="utf-8")
    else:
        (PACKAGE / "RESULT.json").write_text(text, encoding="utf-8")
    print(
        "PASS_IDENTICAL_POSITIVE_SIDE_RECEIPTS "
        f"rounds={args.rounds} median_baseline={base_med:.3f}s "
        f"median_optimized={opt_med:.3f}s ratio={ratio:.3f}x"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
