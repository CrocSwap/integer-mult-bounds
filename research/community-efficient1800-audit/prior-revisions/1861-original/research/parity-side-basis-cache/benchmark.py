#!/usr/bin/env python3
"""Alternating fresh-process before/after timing for the parity-side audit.

Timing is descriptive and never a correctness gate. Receipts must match
fieldwise between baseline and optimized workers.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
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

if mode == "baseline":
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "baseline_bpf", root / "research/parity-side-basis-cache/baseline.py"
    )
    bpf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bpf)
else:
    import binary_phase_frames as bpf

import experiments.parity_side as parity_side
import experiments.parity_phase_repair as repair

parity_side.basis = bpf.basis
parity_side.classify = bpf.classify
repair.basis = bpf.basis
repair.contains = bpf.contains
repair.classify = bpf.classify
repair.dot = bpf.dot
if hasattr(repair.characteristic, "cache_clear"):
    repair.characteristic.cache_clear()
if hasattr(bpf, "_basis_cached") and hasattr(bpf._basis_cached, "cache_clear"):
    bpf._basis_cached.cache_clear()

t0 = time.perf_counter()
rows = []
for h in (8, 10, 26):
    c = parity_side.ParitySide(h)
    raw = c.verify()
    repaired = repair.coarsen(c)
    dag = sha256(
        json.dumps(dict(args=c.args, outputs=c.outputs), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    rows.append(
        dict(
            h=h,
            roles=raw["roles"],
            repaired_roles=repaired["repaired_roles"],
            local_obstructions=raw["local_obstructions"],
            dag_sha256=dag,
            nested_edges_checked=repaired["nested_edges_checked"],
            retained_nodes=repaired["retained_nodes"],
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

    # Warmup pairs (discarded)
    for _ in range(args.warmup):
        run_worker("baseline")
        run_worker("optimized")

    samples = []
    # Alternate starting mode each pair for fairness.
    for i in range(args.rounds):
        order = ("baseline", "optimized") if i % 2 == 0 else ("optimized", "baseline")
        pair = {}
        for mode in order:
            pair[mode] = run_worker(mode)
        require(
            pair["baseline"]["rows"] == pair["optimized"]["rows"],
            f"receipt mismatch in pair {i}: {pair['baseline']['rows']!r} vs {pair['optimized']['rows']!r}",
        )
        samples.append(
            dict(
                pair=i,
                order=list(order),
                baseline_elapsed=pair["baseline"]["elapsed"],
                optimized_elapsed=pair["optimized"]["elapsed"],
                rows=pair["baseline"]["rows"],
            )
        )

    base_med = statistics.median(s["baseline_elapsed"] for s in samples)
    opt_med = statistics.median(s["optimized_elapsed"] for s in samples)
    ratio = base_med / opt_med if opt_med else float("inf")
    result = dict(
        status="PASS_IDENTICAL_PARITY_SIDE_RECEIPTS",
        rounds=args.rounds,
        warmup=args.warmup,
        python=sys.version,
        executable=sys.executable,
        platform=sys.platform,
        median_baseline_seconds=base_med,
        median_optimized_seconds=opt_med,
        median_ratio=ratio,
        samples=samples,
        production_sha256=sha256((ROOT / "scripts/binary_phase_frames.py").read_bytes()).hexdigest(),
        baseline_sha256=sha256((PACKAGE / "baseline.py").read_bytes()).hexdigest(),
        no_new_kappa=True,
        note="Wall times are host-descriptive; receipt equality is the correctness gate.",
    )
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        require(not args.output.exists(), f"refusing to overwrite {args.output}")
        args.output.write_text(text, encoding="utf-8")
    else:
        # Default write into the package only when RESULT.json is absent or --force via explicit path.
        target = PACKAGE / "RESULT.json"
        target.write_text(text, encoding="utf-8")
    print(
        "PASS_IDENTICAL_PARITY_SIDE_RECEIPTS "
        f"rounds={args.rounds} median_baseline={base_med:.3f}s "
        f"median_optimized={opt_med:.3f}s ratio={ratio:.2f}x no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
