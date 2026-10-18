#!/usr/bin/env python3
"""Alternating fresh-process before/after timings for packed production verify_factor.

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

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent

WORKER = r"""
import importlib.util
import json
import sys
import time
from pathlib import Path

root = Path(sys.argv[1])
engine = sys.argv[2]
scope = sys.argv[3]
sys.path.insert(0, str(root / "scripts"))

if engine == "baseline":
    spec = importlib.util.spec_from_file_location(
        "complex_centers_baseline",
        root / "research/central-factor-production/baseline.py",
    )
    centers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(centers)
else:
    from experiments import complex_centers as centers

if scope == "factor":
    factor = centers.factor(26)
    t0 = time.perf_counter()
    receipt = centers.verify_factor(factor)
    elapsed = time.perf_counter() - t0
    print(json.dumps({"elapsed": elapsed, "receipt": receipt}, sort_keys=True))
else:
    import audit_complex_centers as audit
    import experiments.complex_centers as live
    from prepare_layers import serializable
    # audit_complex_centers binds verify_factor at import time; patch both.
    live.verify_factor = centers.verify_factor
    audit.verify_factor = centers.verify_factor
    t0 = time.perf_counter()
    cert = audit.certificate()
    elapsed = time.perf_counter() - t0
    payload = serializable(cert)
    payload.pop("source_sha256", None)
    print(json.dumps({"elapsed": elapsed, "payload": payload}, sort_keys=True))
"""


def run_engine(engine: str, scope: str) -> dict:
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-I", "-B", "-c", WORKER, str(ROOT), engine, scope],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(f"engine={engine} scope={scope} failed\n{proc.stderr}\n{proc.stdout}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def measure(scope: str, rounds: int) -> dict:
    baseline_samples = []
    optimized_samples = []
    reference = None
    samples = []
    for round_index in range(rounds):
        order = ("baseline", "optimized") if round_index % 2 == 0 else ("optimized", "baseline")
        pair = {}
        for engine in order:
            payload = run_engine(engine, scope)
            key = "receipt" if scope == "factor" else "payload"
            if reference is None:
                reference = payload[key]
            elif payload[key] != reference:
                raise SystemExit(f"receipt mismatch scope={scope} round={round_index} engine={engine}")
            pair[engine] = payload["elapsed"]
        baseline_samples.append(pair["baseline"])
        optimized_samples.append(pair["optimized"])
        samples.append(
            {
                "round": round_index,
                "order": list(order),
                "baseline_seconds": pair["baseline"],
                "optimized_seconds": pair["optimized"],
                "ratio": pair["baseline"] / pair["optimized"] if pair["optimized"] else None,
            }
        )
        print(
            f"scope={scope} round={round_index} order={order[0]}->{order[1]} "
            f"baseline={pair['baseline']:.6f}s optimized={pair['optimized']:.6f}s",
            flush=True,
        )
    base_med = statistics.median(baseline_samples)
    opt_med = statistics.median(optimized_samples)
    return {
        "scope": scope,
        "rounds": rounds,
        "median_baseline_seconds": base_med,
        "median_optimized_seconds": opt_med,
        "median_ratio": base_med / opt_med if opt_med else None,
        "samples": samples,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--output", type=Path, default=PACKAGE / "RESULT.json")
    args = parser.parse_args(argv)
    if args.rounds < 1:
        raise SystemExit("--rounds must be >= 1")

    factor = measure("factor", args.rounds)
    audit = measure("audit", args.rounds)
    result = {
        "status": "PASS_IDENTICAL_CENTRAL_FACTOR_PRODUCTION_RECEIPTS",
        "ai_assistance": (
            "Substantial AI assistance for orientation, overlap search, profiling, "
            "implementation, packaging, benchmarking and writing. Not independent "
            "human peer review."
        ),
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "predecessor": "research/central-factor-packed/",
        "engines": {
            "baseline": "research/central-factor-production/baseline.py",
            "optimized": "scripts/experiments/complex_centers.py",
        },
        "source_sha256": {
            "baseline.py": sha256((PACKAGE / "baseline.py").read_bytes()).hexdigest(),
            "scripts/experiments/complex_centers.py": sha256(
                (ROOT / "scripts/experiments/complex_centers.py").read_bytes()
            ).hexdigest(),
            "research/central-factor-packed/packed.py": sha256(
                (ROOT / "research/central-factor-packed/packed.py").read_bytes()
            ).hexdigest(),
        },
        "environment": {
            "python": sys.version,
            "executable": sys.executable,
            "platform": platform.platform(),
            "implementation": platform.python_implementation(),
            "os_caches_flushed": False,
            "cpu_affinity_set": False,
        },
        "factor_only": factor,
        "complete_audit": audit,
        "no_new_kappa": True,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    print(
        f"factor_median {factor['median_baseline_seconds']:.6f} -> "
        f"{factor['median_optimized_seconds']:.6f} ({factor['median_ratio']:.3f}x)"
    )
    print(
        f"audit_median {audit['median_baseline_seconds']:.6f} -> "
        f"{audit['median_optimized_seconds']:.6f} ({audit['median_ratio']:.3f}x)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
