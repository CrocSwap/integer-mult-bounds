#!/usr/bin/env python3
"""Paired complete-stream timings, separated from mathematical evidence.

Sricharan Vagvala, substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from contextlib import nullcontext
import json
from pathlib import Path
import platform
from statistics import median
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fast_rows import accelerated
from support import digest, fixture, predecessor, require


def benchmark(repeats=5):
    experiment, independent, _ = predecessor()
    programs = fixture(experiment)
    timings = {"baseline": [], "accelerated": []}
    reference = None
    for trial in range(-1, repeats):
        order = ("baseline", "accelerated") if (89 + trial) % 2 else ("accelerated", "baseline")
        for mode in order:
            context = accelerated(independent) if mode == "accelerated" else nullcontext()
            with context:
                started = perf_counter()
                results = {name: independent.replay(program) for name, program in programs.items()}
                elapsed = perf_counter() - started
            # Equality includes every endpoint, denominator maximum, envelope,
            # first peak instruction and price; hashing is outside the timing.
            receipts = {name: digest(result) for name, result in results.items()}
            if reference is None:
                reference = receipts
            require(receipts == reference, "benchmark changed a proof-relevant result")
            if trial >= 0:
                timings[mode].append(elapsed)
    baseline, fast = (median(timings[name]) for name in ("baseline", "accelerated"))
    return {"scope": "four complete integer-dyadic scalar streams; excludes construction, Fraction replay and native audit",
            "python": sys.version, "platform": platform.platform(),
            "assignment_seed": 89, "warmup_pairs": 1, "measured_pairs": repeats,
            "alternating_order": True, "streams": {name: {"primitives": len(program),
                "word_sha256": digest(program), "result_sha256": reference[name]}
                for name, program in programs.items()},
            "total_primitives_per_run": sum(map(len, programs.values())),
            "seconds": timings, "median_seconds": {"baseline": baseline, "accelerated": fast},
            "median_speedup": baseline / fast, "mathematical_receipts_identical": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--output", type=Path, help="optional timing JSON, not a mathematical certificate")
    args = parser.parse_args()
    if not 1 <= args.repeats <= 20:
        parser.error("use 1..20 paired repeats")
    result = benchmark(args.repeats)
    raw = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(raw)
    print(raw, end="")
