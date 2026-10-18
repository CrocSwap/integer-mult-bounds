#!/usr/bin/env python3
"""Alternating fresh-process before/after timings for production joint-dual replay.

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
WORDS = ("certificates/joint-dual-word-23.json.gz",
         "certificates/joint-dual-word-25.json.gz")

WORKER = r"""
import importlib.util
import json
import sys
import time
from pathlib import Path

root = Path(sys.argv[1])
engine = sys.argv[2]
words = sys.argv[3:]

if engine == "baseline":
    spec = importlib.util.spec_from_file_location(
        "binary_frame_replay_baseline",
        root / "research/joint-dual-replay-production/baseline.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
else:
    spec = importlib.util.spec_from_file_location(
        "binary_frame_replay_production",
        root / "scripts/experiments/binary_frame_replay.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

receipts = []
t0 = time.perf_counter()
for rel in words:
    receipts.append(mod.replay(root / rel))
elapsed = time.perf_counter() - t0
print(json.dumps({"elapsed": elapsed, "receipts": receipts}, sort_keys=True))
"""


def run_engine(engine: str) -> dict:
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-I", "-B", "-c", WORKER, str(ROOT), engine, *WORDS],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(f"engine={engine} failed\n{proc.stderr}\n{proc.stdout}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def measure(rounds: int) -> dict:
    baseline_samples = []
    optimized_samples = []
    reference = None
    samples = []
    for round_index in range(rounds):
        order = ("baseline", "optimized") if round_index % 2 == 0 else ("optimized", "baseline")
        pair = {}
        for engine in order:
            payload = run_engine(engine)
            if reference is None:
                reference = payload["receipts"]
            elif payload["receipts"] != reference:
                raise SystemExit(f"receipt mismatch round={round_index} engine={engine}")
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
            f"round={round_index} order={order[0]}->{order[1]} "
            f"baseline={pair['baseline']:.6f}s optimized={pair['optimized']:.6f}s",
            flush=True,
        )
    base_med = statistics.median(baseline_samples)
    opt_med = statistics.median(optimized_samples)
    return {
        "rounds": rounds,
        "words": list(WORDS),
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

    replay = measure(args.rounds)
    result = {
        "status": "PASS_IDENTICAL_JOINT_DUAL_REPLAY_PRODUCTION_RECEIPTS",
        "ai_assistance": (
            "Substantial AI assistance for orientation, overlap search, profiling, "
            "production wiring, packaging, benchmarking and writing. Not independent "
            "human peer review."
        ),
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "predecessor": "research/joint-dual-replay-fast/",
        "engines": {
            "baseline": "research/joint-dual-replay-production/baseline.py",
            "optimized": "scripts/experiments/binary_frame_replay.py",
        },
        "source_sha256": {
            "baseline.py": sha256((PACKAGE / "baseline.py").read_bytes()).hexdigest(),
            "scripts/experiments/binary_frame_replay.py": sha256(
                (ROOT / "scripts/experiments/binary_frame_replay.py").read_bytes()
            ).hexdigest(),
            "research/joint-dual-replay-fast/fast_replay.py": sha256(
                (ROOT / "research/joint-dual-replay-fast/fast_replay.py").read_bytes()
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
        "both_words_replay": replay,
        "no_new_kappa": True,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"])
    print(
        f"replay_median {replay['median_baseline_seconds']:.6f} -> "
        f"{replay['median_optimized_seconds']:.6f} ({replay['median_ratio']:.3f}x)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
