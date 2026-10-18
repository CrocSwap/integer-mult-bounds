#!/usr/bin/env python3
"""Alternating fresh-process before/after timings for the three pinned witnesses.

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


WORKER = r"""
import json, sys, time
from pathlib import Path
root = Path(sys.argv[1])
engine = sys.argv[2]
sys.path.insert(0, str(root / "scripts"))
if engine == "baseline":
    import importlib.util
    path = root / "research/inplace-side-performance/baseline.py"
    spec = importlib.util.spec_from_file_location("inplace_side_baseline", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
else:
    from experiments import inplace_side as mod
witnesses = json.loads((root / "scripts/experiments/inplace_side_witnesses.json").read_text())
t0 = time.perf_counter()
receipts = [mod.verify_prefix(w["h"], w["pivots"], w["swaps"]) for w in witnesses]
elapsed = time.perf_counter() - t0
print(json.dumps({"elapsed": elapsed, "receipts": receipts}))
"""


def run_engine(engine: str) -> dict:
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-B", "-c", WORKER, str(ROOT), engine],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(f"engine={engine} failed\n{proc.stderr}\n{proc.stdout}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--output", type=Path, default=PACKAGE / "RESULT.json")
    args = parser.parse_args(argv)
    require_rounds = args.rounds
    if require_rounds < 1:
        raise SystemExit("--rounds must be >= 1")

    baseline_samples = []
    optimized_samples = []
    reference = None
    for round_index in range(require_rounds):
        order = ("baseline", "optimized") if round_index % 2 == 0 else ("optimized", "baseline")
        pair = {}
        for engine in order:
            payload = run_engine(engine)
            if reference is None:
                reference = payload["receipts"]
            elif payload["receipts"] != reference:
                raise SystemExit(f"receipt mismatch on round {round_index} engine={engine}")
            pair[engine] = payload["elapsed"]
        baseline_samples.append(pair["baseline"])
        optimized_samples.append(pair["optimized"])
        print(
            f"round={round_index} order={order[0]}->{order[1]} "
            f"baseline={pair['baseline']:.6f}s optimized={pair['optimized']:.6f}s",
            flush=True,
        )

    base_med = statistics.median(baseline_samples)
    opt_med = statistics.median(optimized_samples)
    result = {
        "status": "PASS_IDENTICAL_INPLACE_PREFIX_RECEIPTS",
        "ai_assistance": (
            "Substantial AI assistance for profiling, implementation, packaging, "
            "benchmarking and writing. Not independent human peer review."
        ),
        "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "fixture": "scripts/experiments/inplace_side_witnesses.json",
        "engines": {
            "baseline": "research/inplace-side-performance/baseline.py",
            "optimized": "scripts/experiments/inplace_side.py",
        },
        "source_sha256": {
            "baseline.py": sha256((PACKAGE / "baseline.py").read_bytes()).hexdigest(),
            "scripts/experiments/inplace_side.py": sha256(
                (ROOT / "scripts/experiments/inplace_side.py").read_bytes()
            ).hexdigest(),
            "scripts/experiments/inplace_side_witnesses.json": sha256(
                (ROOT / "scripts/experiments/inplace_side_witnesses.json").read_bytes()
            ).hexdigest(),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "implementation": platform.python_implementation(),
            "os_caches_flushed": False,
            "isolated_host": False,
        },
        "rounds": require_rounds,
        "baseline_seconds": baseline_samples,
        "optimized_seconds": optimized_samples,
        "medians": {
            "baseline": base_med,
            "optimized": opt_med,
            "speedup": (base_med / opt_med) if opt_med else None,
        },
        "receipt_fields_compared": sorted(reference[0].keys()) if reference else [],
        "witness_h": [r["h"] for r in reference] if reference else [],
        "scope": (
            "Fixed historical inplace-side prefix check on the three pinned witnesses "
            "(h=42,46,50). Not a selected-supplier cold replay or multiplication runtime."
        ),
        "no_new_kappa": True,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"PASS_IDENTICAL_INPLACE_PREFIX_RECEIPTS "
        f"median_baseline={base_med:.6f}s median_optimized={opt_med:.6f}s "
        f"speedup={base_med / opt_med:.3f}x output={args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
