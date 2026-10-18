#!/usr/bin/env python3
"""Alternating fresh-process before/after timing for shared-point frame contains.

Timing is descriptive and never a correctness gate. Receipts must match
fieldwise between baseline and optimized workers. Circuit construction and
ExclusionCircuit.compile are shared and excluded from the timed interval so the
measurement isolates verify_frames nesting (support_in / contained).
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

if mode == "baseline":
    spec = importlib.util.spec_from_file_location(
        "baseline_spc", root / "research/shared-point-frame-contains/baseline.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["baseline_spc"] = mod
    spec.loader.exec_module(mod)
    SharedPointCircuit = mod.SharedPointCircuit
else:
    from shared_point_circuit import SharedPointCircuit

# Build the fixed historical full-size circuit and compile outside the timer.
circuit = SharedPointCircuit(46)
code = circuit.compile()

t0 = time.perf_counter()
record = circuit.verify_frames(code)
elapsed = time.perf_counter() - t0
print(json.dumps(dict(mode=mode, seconds=elapsed, record=record), sort_keys=True))
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
            pair["baseline"]["record"] == pair["optimized"]["record"],
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
        status="PASS_IDENTICAL_SHARED_POINT_FRAME_CONTAINS_RECEIPTS",
        fixture=(
            "SharedPointCircuit(46).verify_frames(code) only "
            "(construction and compile excluded)"
        ),
        rounds=args.rounds,
        median_baseline_seconds=base_med,
        median_optimized_seconds=opt_med,
        median_ratio=base_med / opt_med,
        samples=samples,
        python=sys.version,
        platform=platform.platform(),
        machine=platform.machine(),
        source_pins={
            "research/shared-point-frame-contains/baseline.py": sha256(
                (PACKAGE / "baseline.py").read_bytes()
            ).hexdigest(),
            "scripts/shared_point_circuit.py": sha256(
                (ROOT / "scripts" / "shared_point_circuit.py").read_bytes()
            ).hexdigest(),
        },
        base_commit="0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
    )
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        result["status"],
        f"median_baseline={base_med:.3f}s",
        f"median_optimized={opt_med:.3f}s",
        f"median_ratio={result['median_ratio']:.3f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
