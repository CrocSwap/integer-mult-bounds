#!/usr/bin/env python3
"""Alternating fresh-process before/after timings for production frame-pair enumeration.

Timing is host-descriptive and is not a correctness gate.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BASELINE = PACKAGE / "baseline.py"
PRODUCTION = ROOT / "research/complex-frame-pair-decoders/verify.py"


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise SystemExit(f"duplicate JSON key: {key}")
        out[key] = value
    return out


WORKER = r"""
import contextlib, hashlib, io, json, sys, time, types
from pathlib import Path

root = Path(sys.argv[1])
engine = sys.argv[2]
path = root / (
    "research/frame-pair-enumeration-production/baseline.py"
    if engine == "baseline"
    else "research/complex-frame-pair-decoders/verify.py"
)

def load(path):
    module = types.ModuleType("frame_pair_bench")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), module.__dict__)
    return module

def digest(obj):
    return hashlib.sha256(
        json.dumps(json.loads(json.dumps(obj, allow_nan=False)), sort_keys=True,
                   separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()

m = load(path)
stream = []
rank_records = []
original = m.frame_pair_solutions
original_pair = m.pair_decoder

def enumerate_pairs(a, b):
    result = original(a, b)
    stream.append([a, b, result])
    return result

def pair_check(pairs, live):
    answer = original_pair(pairs, live)
    rank_records.append([pairs, live, answer])
    return answer

m.frame_pair_solutions = enumerate_pairs
m.pair_decoder = pair_check
capture = io.StringIO()
t0 = time.perf_counter()
with contextlib.redirect_stdout(capture):
    frames, example, hist, kinds = m.section_d()
    chain = m.section_e(frames, example)
    m.section_h(example, frames, hist)
elapsed = time.perf_counter() - t0
if m.FAILS:
    raise SystemExit("checks failed: " + str(m.FAILS))
receipt = {
    "frames": len(frames),
    "enumerations": len(stream),
    "decoder_rank_checks": len(rank_records),
    "term_rank_checks": sum(len(record[2][1]) for record in rank_records),
    "ordered_solution_stream_sha256": digest(stream),
    "rank_stream_sha256": digest(rank_records),
    "histogram": sorted(hist.items()),
    "types": sorted((str(k), v) for k, v in kinds.items()),
    "example": example,
    "chain": chain,
    "log": capture.getvalue().splitlines(),
}
print(json.dumps({"elapsed": elapsed, "receipt": receipt}, sort_keys=True))
"""


def run_engine(engine: str) -> dict:
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-I", "-B", "-c", WORKER, str(ROOT), engine],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(f"engine={engine} failed\n{proc.stderr}\n{proc.stdout}")
    return json.loads(proc.stdout.strip().splitlines()[-1], object_pairs_hook=unique_object)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--write-result", action="store_true")
    parser.add_argument("--output", type=Path, default=PACKAGE / "RESULT.json")
    args = parser.parse_args(argv)
    if args.rounds < 1:
        raise SystemExit("--rounds must be >= 1")

    samples = []
    baseline_times = []
    production_times = []
    reference = None
    for round_index in range(args.rounds):
        order = ("baseline", "production") if round_index % 2 == 0 else ("production", "baseline")
        pair = []
        for engine in order:
            payload = run_engine(engine)
            if reference is None:
                reference = payload["receipt"]
            elif payload["receipt"] != reference:
                raise SystemExit(f"receipt mismatch round={round_index} engine={engine}")
            pair.append({"engine": engine, "seconds": payload["elapsed"],
                         "receipt_sha256": hashlib.sha256(
                             json.dumps(payload["receipt"], sort_keys=True, separators=(",", ":")).encode()
                         ).hexdigest()})
            if engine == "baseline":
                baseline_times.append(payload["elapsed"])
            else:
                production_times.append(payload["elapsed"])
            print(
                f"round={round_index} engine={engine} seconds={payload['elapsed']:.6f}",
                flush=True,
            )
        samples.append(pair)

    base_med = statistics.median(baseline_times)
    prod_med = statistics.median(production_times)
    result = {
        "status": "PASS_IDENTICAL_FRAME_PAIR_ENUMERATION_PRODUCTION_RECEIPTS",
        "ai_assistance": (
            "Substantial AI assistance for orientation, overlap search, profiling, "
            "production wiring, packaging, benchmarking and writing. Not independent "
            "human peer review."
        ),
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "predecessor": "research/frame-pair-enumeration-fast-seed93/",
        "python": sys.version,
        "platform": platform.platform(),
        "rounds": args.rounds,
        "scope": "PR968 sections D/E/H (complete frame-pair census, attaining chain, controls)",
        "baseline_median_seconds": base_med,
        "production_median_seconds": prod_med,
        "median_ratio": base_med / prod_med if prod_med else None,
        "samples": samples,
        "implementation_sha256": {
            "baseline.py": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
            "production": hashlib.sha256(PRODUCTION.read_bytes()).hexdigest(),
            "benchmark.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "no_new_kappa": True,
    }
    print(result["status"])
    print(f"median {base_med:.6f} -> {prod_med:.6f} ({result['median_ratio']:.3f}x)")
    if args.write_result:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
