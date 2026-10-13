#!/usr/bin/env python3
"""Alternating complete fresh-process T37 audits; timings are descriptive."""
import argparse
import platform
from pathlib import Path
import random
import resource
import runpy
import statistics
import subprocess
import sys
import tempfile
import time

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))


def run(pairs, output):
    C["need"](type(pairs) is int and 1 <= pairs <= 5, "one through five pairs")
    C["need"](not output.exists(), "new benchmark output required")
    manifest = C["pins"]()
    samples, receipts = [], []
    first = random.Random(94).randrange(2)
    with tempfile.TemporaryDirectory(prefix="t37-bitmap-benchmark-") as tmp:
        for pair in range(pairs):
            order = ["reference", "bitmap"]
            if (pair + first) % 2:
                order.reverse()
            for engine in order:
                out = Path(tmp) / (str(pair) + "-" + engine)
                before = resource.getrusage(resource.RUSAGE_CHILDREN)
                start = time.perf_counter()
                result = subprocess.run([sys.executable, "-I", "-B", C["HERE"] / "adapter.py",
                                         "--engine", engine, "--output", out], capture_output=True, text=True)
                seconds = time.perf_counter() - start
                after = resource.getrusage(resource.RUSAGE_CHILDREN)
                C["need"](result.returncode == 0, result.stdout + result.stderr)
                receipt = C["load"](out / "normalized-receipt.json")
                if receipts:
                    C["same"](receipt, receipts[0], "complete timed receipts")
                receipts.append(receipt)
                usage = C["load"](out / "usage.json")
                row = {"pair": pair, "engine": engine, "wall_seconds": seconds,
                       "child_cpu_seconds": after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
                       "peak_rss_native_units": usage["peak_rss_native_units"]}
                samples.append(row)
                print(engine, pair, round(seconds, 4), flush=True)
    medians = {e: {k: statistics.median(x[k] for x in samples if x["engine"] == e)
                   for k in ("wall_seconds", "child_cpu_seconds", "peak_rss_native_units")}
               for e in ("reference", "bitmap")}
    result = {"status": "PASS_IDENTICAL_T37_OWNER_AUDITS", "seed": 94, "pairs": pairs,
              "samples": samples, "medians": medians,
              "wall_speedup": medians["reference"]["wall_seconds"] / medians["bitmap"]["wall_seconds"],
              "environment": {"python": sys.version, "platform": platform.platform(),
                              "rss_units": "KiB" if sys.platform.startswith("linux") else "platform-native",
                              "host_isolated": False, "os_caches_flushed": False},
              "sources": manifest, "complete_receipt": receipts[0],
              "scope": "Whole independent T37 owner audit, including source/archive/input admission, all original checks and 14 controls; no complete frontier timing."}
    C["write"](output, result)
    print(result["status"], result["wall_speedup"], flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pairs", type=int, default=5)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    run(args.pairs, args.output)
