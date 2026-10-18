"""Sequential fresh-process comparison on both complete historical axes."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

from adapter import HERE, require, verify_sources


def implementation_hashes():
    names = ("priority.py", "adapter.py", "run.py", "benchmark.py", "reference-pr175.py", "SOURCE.json")
    return {name: sha256((HERE / name).read_bytes()).hexdigest() for name in names}


def benchmark(rounds, output):
    require(1 <= rounds <= 7, "Use one through seven rounds")
    require(not output.exists(), "Output must be a fresh directory")
    pins = verify_sources()
    implementations = implementation_hashes()
    output.mkdir(parents=True)
    records = []
    modes = ("reference", "buckets", "indexed")
    for h in (23, 25):
        for repetition in range(rounds):
            offset = repetition % len(modes)
            order = modes[offset:] + modes[:offset]
            for mode in order:
                name = f"h{h}-round{repetition + 1}-{mode}"
                command = [sys.executable, "-B", str(HERE / "run.py"),
                           "--mode", mode, "--h", str(h), "--out", str(output / name)]
                with (output / (name + ".log")).open("w") as log:
                    start = time.perf_counter()
                    subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)
                    process_seconds = time.perf_counter() - start
                record = json.loads((output / name / "RESULT.json").read_text())
                record.update(round=repetition + 1, process_wall_seconds=process_seconds)
                reference = next((r for r in records if r["h"] == h), record)
                for key in ("word_sha256", "word_bytes", "compiler_receipt", "independent_replay", "transitions"):
                    require(record[key] == reference[key], "Engines disagree: " + key)
                records.append(record)
                print(f"PASS {name} compile={record['compile_wall_seconds']:.3f}s process={process_seconds:.3f}s", flush=True)
    require(implementation_hashes() == implementations, "Implementation changed during benchmark")
    summary = {}
    for h in (23, 25):
        summary[h] = {}
        for mode in modes:
            rows = [r for r in records if r["h"] == h and r["engine"] == mode]
            summary[h][mode] = {key: statistics.median(r[key] for r in rows)
                               for key in ("compile_wall_seconds", "compile_cpu_seconds", "process_wall_seconds")}
    result = dict(status="PASS_RECLAMATION_BENCHMARK", utc=datetime.now(timezone.utc).isoformat(),
                  rounds=rounds, python=sys.version, platform=platform.platform(),
                  order="reference/buckets/indexed, then cyclic rotations; axes 23 then 25; sequential fresh processes; OS caches not flushed",
                  source_pins=pins, implementation_sha256=implementations, medians=summary, runs=records,
                  scope="Complete axis compilation and replay/transition process, not full joint-dual verification, frontier cold replay or multiplication runtime")
    (output / "BENCHMARK.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_RECLAMATION_BENCHMARK", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    benchmark(args.rounds, args.out.resolve())
