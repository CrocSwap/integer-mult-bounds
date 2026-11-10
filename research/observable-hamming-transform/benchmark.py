"""Measure five alternating fresh-process complete preparation pairs."""
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import planner
import source
import workload


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def worker(side):
    model = source.load_model()
    solve = model.solve if side == "baseline" else planner.solve
    result = workload.prepare(model, solve, workload.specification(), True)
    return {"sha256": digest(result), "stages": len(result["spec"]["steps"]),
            "table_entries": sum(map(len, result["plan"]["tables"])),
            "gates": len(result["word"]["gates"]), "cost": result["plan"]["cost"],
            "errors": 0}


def measure():
    records = []
    for trial in range(5):
        for side in ("baseline", "transform"):
            command = [sys.executable, "-I", "-B", str(Path(__file__).resolve()), "--worker", side]
            started = time.perf_counter()
            run = subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
            elapsed = time.perf_counter() - started
            value = json.loads(run.stdout)
            if value["errors"] != 0 or run.stderr:
                raise ValueError("worker reported an error")
            records.append({"trial": trial, "side": side, "wall_seconds": elapsed, "output": value})
    if len({digest(r["output"]) for r in records}) != 1:
        raise ValueError("preparation results disagree")
    summaries = {}
    for side in ("baseline", "transform"):
        values = [r["wall_seconds"] for r in records if r["side"] == side]
        summaries[side] = {"median_seconds": statistics.median(values),
                           "range_seconds": [min(values), max(values)]}
    before, after = (summaries[s]["median_seconds"] for s in ("baseline", "transform"))
    return {"schema_version": 1, "python": platform.python_version(),
            "platform": platform.platform(), "logical_cpus": os.cpu_count(),
            "load_average_at_end": os.getloadavg(), "runs_per_side": 5,
            "timed_region": "fresh process, imports and source authentication, demands, solve, "
                            "complete word emission, every observation, full inverse, invoice and output digest",
            "summaries": summaries, "fractional_wall_reduction": 1 - after / before,
            "records": records, "files_sha256": file_hashes()}


def file_hashes():
    names = ("planner.py", "source.py", "workload.py", "benchmark.py", "SOURCES.json")
    return {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=("baseline", "transform"))
    args = parser.parse_args()
    print(json.dumps(worker(args.worker) if args.worker else measure(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
