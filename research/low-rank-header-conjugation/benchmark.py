"""Alternating complete-command benchmark. Produced by Nick Petalas."""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import HERE, build, need, source_bytes


def timed(binary):
    start = time.perf_counter_ns()
    result = subprocess.run([str(binary), "3", "4"], capture_output=True,
                            timeout=120)
    elapsed = time.perf_counter_ns() - start
    need(result.returncode == 0 and not result.stderr, "census success")
    need(result.stdout.startswith(b"q=3 m=4 GL=24261120 "), "complete workload")
    return elapsed, result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    args = parser.parse_args()
    need(5 <= args.rounds <= 9, "benchmark rounds must be in 5..9")
    samples = [[], []]
    output = None
    with tempfile.TemporaryDirectory(prefix="header-benchmark-") as directory:
        binaries = build(Path(directory))
        for pair in range(args.rounds):
            for side in (0, 1):
                elapsed, stdout = timed(binaries[side])
                if output is None:
                    output = stdout
                need(stdout == output, "byte-identical complete census")
                samples[side].append(elapsed)
    compiler = subprocess.run(["cc", "--version"], check=True,
                              capture_output=True, text=True, timeout=10)
    medians = [statistics.median(s) for s in samples]
    hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
              for name in ("build.py", "conjugate.h", "benchmark.py")}
    result = {"schema": "complete-header-benchmark/1", "rounds": args.rounds,
              "order": "baseline,candidate for each pair", "errors": 0,
              "workload": [3, 4], "samples_ns": samples,
              "median_ns": medians,
              "range_ns": [[min(s), max(s)] for s in samples],
              "reduction_percent": 100 * (1 - medians[1] / medians[0]),
              "stdout": output.decode(),
              "stdout_sha256": hashlib.sha256(output).hexdigest(),
              "source_sha256": hashlib.sha256(source_bytes()).hexdigest(),
              "implementation_sha256": hashes, "platform": platform.platform(),
              "python": sys.version, "compiler": compiler.stdout,
              "flags": ["-O2", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-pedantic"],
              "timed_region": "fresh census process through complete output; compilation excluded"}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
