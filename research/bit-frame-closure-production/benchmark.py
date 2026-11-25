#!/usr/bin/env python3
"""Alternating fresh-process before/after timings for production one-basis close.

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

CASES = (
    (
        "pr589",
        "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz",
        "1733427039589844234749/1000000000000000000000000",
        False,
    ),
    (
        "pr555",
        "research/e8-bit-p111-tuned/data/bitE8mut-p111.json.gz",
        "1733052823330162099157/1000000000000000000000000",
        False,
    ),
    (
        "degraded",
        "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz",
        "1733427039589844234749/1000000000000000000000000",
        True,
    ),
)

WORKER = r"""
import json
import sys
import time
from pathlib import Path

root = Path(sys.argv[1])
engine = sys.argv[2]
scope = sys.argv[3]
cases = [
    ("pr589", "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz",
     "1733427039589844234749/1000000000000000000000000", False),
    ("pr555", "research/e8-bit-p111-tuned/data/bitE8mut-p111.json.gz",
     "1733052823330162099157/1000000000000000000000000", False),
    ("degraded", "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz",
     "1733427039589844234749/1000000000000000000000000", True),
]
if engine == "baseline":
    script = root / "research/bit-frame-closure-production/baseline.py"
else:
    script = root / "research/bit589-frame-optimum/frameopt.py"
selected = [row for row in cases if scope == "suite" or row[0] == scope]
assert selected, scope
import subprocess, os
env = os.environ.copy()
env.pop("PYTHONOPTIMIZE", None)
env["PYTHONDONTWRITEBYTECODE"] = "1"
receipts = {}
t0 = time.perf_counter()
for name, word, endpoint, degraded in selected:
    cmd = [sys.executable, "-I", "-B", str(script), str(root / word), endpoint]
    if degraded:
        cmd.append("--degrade")
    proc = subprocess.run(cmd, cwd=root, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr + proc.stdout)
    receipts[name] = json.loads(proc.stdout)
elapsed = time.perf_counter() - t0
print(json.dumps({"elapsed": elapsed, "receipts": receipts}, sort_keys=True))
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
    for round_index in range(rounds):
        order = ("baseline", "optimized") if round_index % 2 == 0 else ("optimized", "baseline")
        pair = {}
        for engine in order:
            payload = run_engine(engine, scope)
            if reference is None:
                reference = payload["receipts"]
            elif payload["receipts"] != reference:
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

    single = measure("pr589", args.rounds)
    suite = measure("suite", args.rounds)
    result = {
        "status": "PASS_IDENTICAL_BIT_FRAME_CLOSURE_PRODUCTION_RECEIPTS",
        "ai_assistance": (
            "Substantial AI assistance for orientation, overlap search, profiling, "
            "production wiring, packaging, benchmarking and writing. Not independent "
            "human peer review."
        ),
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "predecessor": "research/bit-frame-closure-basis/",
        "engines": {
            "baseline": "research/bit-frame-closure-production/baseline.py",
            "optimized": "research/bit589-frame-optimum/frameopt.py",
        },
        "source_sha256": {
            "baseline.py": sha256((PACKAGE / "baseline.py").read_bytes()).hexdigest(),
            "research/bit589-frame-optimum/frameopt.py": sha256(
                (ROOT / "research/bit589-frame-optimum/frameopt.py").read_bytes()
            ).hexdigest(),
            "research/bit-frame-closure-basis/closure.py": sha256(
                (ROOT / "research/bit-frame-closure-basis/closure.py").read_bytes()
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
        "pr589_only": single,
        "complete_three_case_suite": suite,
        "no_new_kappa": True,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    print(
        f"pr589_median {single['median_baseline_seconds']:.6f} -> "
        f"{single['median_optimized_seconds']:.6f} ({single['median_ratio']:.3f}x)"
    )
    print(
        f"suite_median {suite['median_baseline_seconds']:.6f} -> "
        f"{suite['median_optimized_seconds']:.6f} ({suite['median_ratio']:.3f}x)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
