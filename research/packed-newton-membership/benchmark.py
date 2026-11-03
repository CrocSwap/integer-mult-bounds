"""Five alternating fresh-process trials; timing is not an acceptance gate.

Produced by Nick Petalas. Apache-2.0.
"""
import argparse
import cProfile
from hashlib import sha256
import json
from pathlib import Path
import platform
import pstats
from statistics import median
import subprocess
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import packed
from support import need, replay_result, source_modules


def sample(side, workload, profile=False):
    reference, replay = source_modules()
    if workload == "replay":
        start = perf_counter()
        result = replay_result(replay, side == "packed")
        return {"seconds": perf_counter() - start, "errors": 0,
                "result_sha256": sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()}
    # Same positive encoding and coefficient width as the source benchmark.
    old = replay.load_source()
    coefficients = [((-1 if i & 1 else 1) * ((1 << 1024) + i * 17),
                     (-1 if i & 2 else 1) * ((1 << 1024) + i * 13)) for i in range(512)]
    values = old.encode(coefficients)
    function = packed.obstruction if side == "packed" else reference.obstruction
    need(reference.obstruction(values) is None and packed.obstruction(values) is None,
         "benchmark fixture must be accepted")
    profiler = cProfile.Profile() if profile else None
    if profiler is not None:
        profiler.enable()
    start = perf_counter()
    for _ in range(1000):
        need(function(values) is None, "timed validation failed")
    seconds = perf_counter() - start
    result = {"seconds": seconds, "calls": 1000, "errors": 0,
              "input_sha256": sha256(json.dumps(values).encode()).hexdigest(),
              "max_component_bits": max(x.bit_length() for z in values for x in z)}
    if profiler is not None:
        profiler.disable()
        stats = pstats.Stats(profiler)
        result["profile_total_seconds"] = stats.total_tt
        result["profile_hotspots"] = [
            {"function": f"{Path(key[0]).name}:{key[1]}:{key[2]}",
             "calls": row[1], "own_seconds": row[2],
             "cumulative_seconds": row[3]}
            for key, row in sorted(stats.stats.items(), key=lambda x: x[1][2], reverse=True)[:8]]
    return result


def trials():
    rows = {workload: {side: [] for side in ("reference", "packed")}
            for workload in ("api", "replay")}
    for workload in ("api", "replay"):
        for trial in range(5):
            order = ("reference", "packed") if trial % 2 == 0 else ("packed", "reference")
            for side in order:
                argv = [sys.executable, "-I", "-W", "error", "-B", str(__file__),
                        "--sample", side, "--workload", workload]
                start = perf_counter()
                run = subprocess.run(argv, capture_output=True, text=True, timeout=120, check=True)
                elapsed = perf_counter() - start
                need(not run.stderr and len(run.stdout) < 16384, "unexpected sample output")
                record = json.loads(run.stdout)
                need(record["errors"] == 0, "sample errors")
                record["process_seconds"] = elapsed
                rows[workload][side].append(record)
    return summarize(rows)


def summarize(rows):
    summaries = {}
    for workload, sides in rows.items():
        field = "result_sha256" if workload == "replay" else "input_sha256"
        need(len({r[field] for side in sides.values() for r in side}) == 1,
             "different fixtures or scientific outputs")
        summary = {}
        for side, records in sides.items():
            values = [r["seconds"] for r in records]
            summary[side] = {"median_seconds": median(values), "min_seconds": min(values),
                             "max_seconds": max(values)}
        before = summary["reference"]["median_seconds"]
        after = summary["packed"]["median_seconds"]
        summary["reduction_percent"] = 100 * (1 - after / before)
        summaries[workload] = summary
    return {"python": platform.python_version(), "platform": platform.platform(),
            "trials_per_side": 5, "samples": rows, "summary": summaries,
            "code_sha256": {name: sha256((HERE / name).read_bytes()).hexdigest()
                            for name in ("benchmark.py", "packed.py", "support.py", "SOURCES.json")},
            "scope": "Complete API calls and complete inherited scientific replay; no physical caller or kappa claim."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", choices=("reference", "packed"))
    parser.add_argument("--workload", choices=("api", "replay"), default="api")
    parser.add_argument("--profile", action="store_true")
    args = parser.parse_args()
    need(not args.profile or args.sample is not None, "profile requires one sample")
    result = sample(args.sample, args.workload, args.profile) if args.sample else trials()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
