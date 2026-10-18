#!/usr/bin/env python3
"""Alternating fresh-process before/after timing for mixed-point scalar digests.

Timing is descriptive and never a correctness gate. Receipts must match
fieldwise between baseline and optimized workers. Circuit construction is
shared and excluded from the timed interval so the measurement isolates the
scalar_check digest stream.
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

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from certify import require  # noqa: E402

WORKER = r'''
import importlib.util
import json
import sys
import time
from pathlib import Path

root = Path(sys.argv[1])
mode = sys.argv[2]
sys.path.insert(0, str(root / "scripts"))

from experiments.mixed_point_circuit import build, factored_transpose

if mode == "baseline":
    spec = importlib.util.spec_from_file_location(
        "baseline_amp", root / "research/mixed-point-scalar-digest/baseline.py"
    )
    amp = importlib.util.module_from_spec(spec)
    sys.modules["baseline_amp"] = amp
    spec.loader.exec_module(amp)
else:
    import audit_mixed_point as amp

# Build the fixed historical circuit set outside the timed window.
circuits = []
build.cache_clear()
for common, label in ((False, "block_only"), (True, "hybrid")):
    c = build(50, 3, 3, 1, common=common)
    circuits.append((label, c, None))
    build.cache_clear()
c = build(50, 3, 3, 1)
build.cache_clear()
for step in range(1, 5):
    c, stats = factored_transpose(c)
    circuits.append((f"factored_{step}", c, stats))

t0 = time.perf_counter()
rows = []
for label, circuit, stats in circuits:
    record = amp.scalar_check(circuit)
    row = dict(label=label, **record)
    if stats is not None:
        row["factoring"] = stats
    rows.append(row)
elapsed = time.perf_counter() - t0
print(json.dumps(dict(mode=mode, seconds=elapsed, rows=rows), sort_keys=True))
'''


def run_worker(mode: str) -> dict:
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-I", "-B", "-c", WORKER, str(ROOT), mode],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    require(proc.returncode == 0, f"worker {mode} failed: {proc.stderr[-2000:]}")
    line = proc.stdout.strip().splitlines()[-1]
    return json.loads(line)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--out", type=Path, default=PACKAGE / "RESULT.json")
    args = parser.parse_args()
    require(args.rounds >= 1, "rounds")

    samples = []
    for i in range(args.rounds):
        order = ("optimized", "baseline") if i % 2 == 0 else ("baseline", "optimized")
        pair = {}
        for mode in order:
            pair[mode] = run_worker(mode)
        require(
            pair["baseline"]["rows"] == pair["optimized"]["rows"],
            f"receipt mismatch on round {i}",
        )
        samples.append(
            dict(
                round=i,
                baseline_seconds=pair["baseline"]["seconds"],
                optimized_seconds=pair["optimized"]["seconds"],
                ratio=pair["baseline"]["seconds"] / pair["optimized"]["seconds"],
            )
        )
        print(
            f"round {i}: baseline={pair['baseline']['seconds']:.3f}s "
            f"optimized={pair['optimized']['seconds']:.3f}s "
            f"ratio={samples[-1]['ratio']:.3f}",
            flush=True,
        )

    base_med = statistics.median(s["baseline_seconds"] for s in samples)
    opt_med = statistics.median(s["optimized_seconds"] for s in samples)
    result = dict(
        status="PASS_IDENTICAL_MIXED_POINT_SCALAR_RECEIPTS",
        fixture=(
            "mixed-point scalar_check only (construction excluded): "
            "block_only+hybrid h=50 and four factored rounds"
        ),
        rounds=args.rounds,
        median_baseline_seconds=base_med,
        median_optimized_seconds=opt_med,
        median_ratio=base_med / opt_med,
        samples=samples,
        environment=dict(
            python=sys.version,
            platform=platform.platform(),
            executable=sys.executable,
        ),
        source_sha256=dict(
            baseline=sha256((PACKAGE / "baseline.py").read_bytes()).hexdigest(),
            production=sha256((ROOT / "scripts/audit_mixed_point.py").read_bytes()).hexdigest(),
        ),
        no_new_kappa=True,
    )
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        "PASS_IDENTICAL_MIXED_POINT_SCALAR_RECEIPTS",
        f"median {base_med:.3f} -> {opt_med:.3f} s ({base_med / opt_med:.2f}x)",
        flush=True,
    )


if __name__ == "__main__":
    main()
