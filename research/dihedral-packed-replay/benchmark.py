"""Measure fresh complete predecessor and packed-adapter processes. Apache-2.0."""
import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "research/bit-dihedral-commutator/verify.py"
PACKED = "research/dihedral-packed-replay/run.py"
EXPECTED = (b"PASS_DIHEDRAL_COMMUTATOR minimum=8 layers=[1, 12, 80, 472, 2459] "
            b"meetings={'8': 398}\n")


def measure(path):
    command = [sys.executable, "-I", "-O", "-W", "error", "-B", path]
    started = time.perf_counter_ns()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30, check=True)
    elapsed = time.perf_counter_ns() - started
    if result.stdout != EXPECTED or result.stderr:
        raise ValueError("unexpected complete scientific output: " + path)
    return elapsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=15)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not 5 <= args.pairs <= 50:
        parser.error("pairs must be in [5, 50]")
    if args.out.exists():
        parser.error("output must not exist")
    rows = []
    for pair in range(args.pairs):
        order = (BASELINE, PACKED) if pair % 2 == 0 else (PACKED, BASELINE)
        values = {path: measure(path) for path in order}
        rows.append({"pair": pair, "order": list(order), "baseline_ns": values[BASELINE],
                     "packed_ns": values[PACKED]})
    before = [row["baseline_ns"] for row in rows]
    after = [row["packed_ns"] for row in rows]
    mb, ma = statistics.median(before), statistics.median(after)
    result = {"schema_version": 1, "python": sys.version, "platform": platform.platform(),
              "scope": "complete fresh-process replay including startup, pin reads and certificate comparison",
              "flags": ["-I", "-O", "-W", "error", "-B"], "pairs": args.pairs, "rows": rows,
              "baseline_median_ns": mb, "packed_median_ns": ma,
              "baseline_range_ns": [min(before), max(before)],
              "packed_range_ns": [min(after), max(after)], "median_reduction_percent": 100 * (1 - ma / mb),
              "faster_pairs": sum(a < b for a, b in zip(after, before)), "failed_processes": 0,
              "stdout_sha256": hashlib.sha256(EXPECTED).hexdigest(),
              "source_sha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                                for path in (BASELINE, PACKED)}}
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps({key: result[key] for key in ("pairs", "baseline_median_ns", "packed_median_ns",
                     "median_reduction_percent", "faster_pairs", "failed_processes")}, sort_keys=True))


if __name__ == "__main__":
    main()
