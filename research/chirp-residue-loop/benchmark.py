"""Five alternating fresh-process measurements of the complete command."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

PACKAGE = Path(__file__).resolve().parent


def measure():
    rows = []
    expected = b"PASS_CHIRP_RESIDUE_STEP rollouts=6141 no_new_kappa\n"
    for trial in range(5):
        for mode in ("baseline", "fast"):
            command = [sys.executable, "-I", "-W", "error", "-B",
                       str(PACKAGE / "replay.py"), "--mode", mode]
            start = time.perf_counter()
            result = subprocess.run(command, capture_output=True, timeout=120)
            elapsed = time.perf_counter() - start
            if result.returncode or result.stderr or result.stdout != expected:
                raise RuntimeError(repr((command, result.returncode,
                                         result.stdout, result.stderr)))
            rows.append({"trial": trial, "mode": mode, "seconds": elapsed,
                         "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
                         "errors": 0})
            print(mode, trial, round(elapsed, 6), flush=True)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("refusing an existing benchmark output")
    rows = measure()
    summary = {}
    for mode in ("baseline", "fast"):
        samples = [r["seconds"] for r in rows if r["mode"] == mode]
        summary[mode] = {"median": statistics.median(samples),
                         "minimum": min(samples), "maximum": max(samples)}
    report = {"python": sys.version, "platform": platform.platform(),
              "logical_cpus": os.cpu_count(), "load_average": os.getloadavg(),
              "samples": rows, "summary": summary,
              "reduction": 1 - summary["fast"]["median"] / summary["baseline"]["median"],
              "errors": 0}
    report["source_hashes"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (PACKAGE / "loop.py", PACKAGE / "replay.py", Path(__file__))}
    with args.output.open("x") as output:
        json.dump(report, output, indent=2)
        output.write("\n")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
