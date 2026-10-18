#!/usr/bin/env python3
"""Alternating fresh-process benchmark with exact receipts on each sample."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=3)
    parser.add_argument("--case", choices=("historical", "t6"), default="t6")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.pairs < 3:
        parser.error("At least three alternating pairs required")
    if args.output.exists():
        parser.error("Output already exists")
    samples = []
    expected = None
    with tempfile.TemporaryDirectory(prefix="cube-xor-benchmark-") as tmp:
        for pair in range(args.pairs):
            order = ("original", "cached") if pair % 2 == 0 else ("cached", "original")
            for name in order:
                output = Path(tmp) / f"{pair}-{name}.json"
                command = [sys.executable, "-I", "-B", str(HERE / "replay.py"),
                           "--case", args.case, "--backend", name,
                           "--output", str(output)]
                start = time.perf_counter()
                result = subprocess.run(command, capture_output=True, text=True)
                seconds = time.perf_counter() - start
                if result.returncode:
                    raise RuntimeError(result.stderr)
                payload = output.read_bytes()
                if expected is None:
                    expected = payload
                if payload != expected:
                    raise ValueError("Benchmark complete receipts differ")
                samples.append({"pair": pair, "backend": name, "seconds": seconds,
                                "receipt_sha256": sha256(payload).hexdigest()})
                print(json.dumps(samples[-1], sort_keys=True), flush=True)
    medians = {name: statistics.median(s["seconds"] for s in samples if s["backend"] == name)
               for name in ("original", "cached")}
    result = {"measured_utc": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "platform": platform.platform(),
              "case": args.case, "fresh_process_each_sample": True,
              "scope": "Wall time includes imports, all source checks, base generation, every scheduled row, ordered elimination, complete receipt check and write; mask cache starts empty each sample. No concurrent replay launched by this harness.",
              "samples": samples, "median_seconds": medians,
              "speedup": medians["original"] / medians["cached"]}
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print("PASS_CUBE_XOR_BENCHMARK " + json.dumps(medians, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
