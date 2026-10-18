#!/usr/bin/env python3
"""Alternating fresh-process before/after timings for production orbit screens.

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
        "audit_sparse_fusion_baseline",
        root / "research/sparse-fusion-orbits-production/baseline.py",
    )
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
else:
    import audit_sparse_fusion as audit

from prepare_layers import serializable

if scope == "screen":
    t0 = time.perf_counter()
    receipt = audit.central_gate_screen(25)
    elapsed = time.perf_counter() - t0
    print(json.dumps({"elapsed": elapsed, "receipt": serializable(receipt)}, sort_keys=True))
else:
    t0 = time.perf_counter()
    cert = audit.certificate()
    elapsed = time.perf_counter() - t0
    print(json.dumps({"elapsed": elapsed, "payload": serializable(cert)}, sort_keys=True))
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
    )
    if proc.returncode != 0:
        raise SystemExit(f"engine={engine} scope={scope} failed\n{proc.stderr}\n{proc.stdout}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def measure(scope: str, rounds: int) -> dict:
    baseline_samples = []
    optimized_samples = []
    reference = None
    samples = []
    key = "receipt" if scope == "screen" else "payload"
    for round_index in range(rounds):
        order = ("baseline", "optimized") if round_index % 2 == 0 else ("optimized", "baseline")
        pair = {}
        for engine in order:
            payload = run_engine(engine, scope)
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

    screen = measure("screen", args.rounds)
    audit = measure("certificate", args.rounds)
    result = {
        "status": "PASS_IDENTICAL_SPARSE_FUSION_ORBITS_PRODUCTION_RECEIPTS",
        "ai_assistance": (
            "Substantial AI assistance for orientation, overlap search, profiling, "
            "production wiring, packaging, benchmarking and writing. Not independent "
            "human peer review."
        ),
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "predecessor": "research/sparse-fusion-orbits/",
        "engines": {
            "baseline": "research/sparse-fusion-orbits-production/baseline.py",
            "optimized": "scripts/audit_sparse_fusion.py",
        },
        "source_sha256": {
            "baseline.py": sha256((PACKAGE / "baseline.py").read_bytes()).hexdigest(),
            "scripts/audit_sparse_fusion.py": sha256(
                (ROOT / "scripts/audit_sparse_fusion.py").read_bytes()
            ).hexdigest(),
            "research/sparse-fusion-orbits/accelerator.py": sha256(
                (ROOT / "research/sparse-fusion-orbits/accelerator.py").read_bytes()
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
        "screen_only": screen,
        "complete_certificate": audit,
        "no_new_kappa": True,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    print(
        f"screen_median {screen['median_baseline_seconds']:.6f} -> "
        f"{screen['median_optimized_seconds']:.6f} ({screen['median_ratio']:.3f}x)"
    )
    print(
        f"certificate_median {audit['median_baseline_seconds']:.6f} -> "
        f"{audit['median_optimized_seconds']:.6f} ({audit['median_ratio']:.3f}x)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
