"""Alternating fresh-process comparisons of the identical complete PR886 suite."""
import argparse
import datetime
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run.require(1 <= args.pairs <= 20, "pairs must be 1..20")
    destination = args.output.resolve()
    run.require(not destination.exists() and not destination.is_relative_to(run.ROOT),
                "use a fresh external benchmark path")
    run.check_sources()
    expected = json.loads((HERE / "EXPECTED.json").read_text())
    samples = []
    for pair in range(args.pairs):
        order = ("reference", "basis") if pair % 2 == 0 else ("basis", "reference")
        sample = {"pair": pair, "order": list(order), "engines": {}}
        for engine in order:
            cases = {}
            start_suite = time.perf_counter()
            for case in run.CASES:
                start = time.perf_counter()
                process = subprocess.run([sys.executable, "-I", "-B", str(HERE / "run.py"),
                    "--case", case, "--engine", engine], capture_output=True, text=True, timeout=150)
                seconds = time.perf_counter() - start
                run.require(process.returncode == 0, engine + " " + case + ": " + process.stderr)
                report = json.loads(process.stdout)
                run.require(report == expected[case], "timed full receipt: " + case)
                cases[case] = {"seconds": seconds, "report_sha256": run.sha(run.canonical(report).encode())}
            sample["engines"][engine] = {"seconds": time.perf_counter() - start_suite, "cases": cases}
        samples.append(sample)
        print("PAIR", pair, {k: round(v["seconds"], 4) for k, v in sample["engines"].items()}, flush=True)
    medians = {engine: statistics.median(s["engines"][engine]["seconds"] for s in samples)
               for engine in ("reference", "basis")}
    case_medians = {case: {engine: statistics.median(s["engines"][engine]["cases"][case]["seconds"]
                    for s in samples) for engine in medians} for case in run.CASES}
    result = {"status": "PASS_BIT_FRAME_CLOSURE_BENCHMARK", "samples": samples,
              "median_suite_seconds": medians, "suite_ratio": medians["reference"] / medians["basis"],
              "median_case_seconds": case_medians,
              "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "python": sys.version, "executable": sys.executable, "platform": platform.platform(),
              "implementation_sha256": {name: run.sha((HERE / name).read_bytes())
                  for name in ("closure.py", "run.py", "benchmark.py", "EXPECTED.json", "SOURCES.json")},
              "scope": "Three complete pinned checker cases in fresh interpreters per engine; same sources, closure inventories and receipts; warm OS caches; no timing acceptance threshold or selected-replay claim."}
    with destination.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(result["status"], "ratio=" + str(result["suite_ratio"]))


if __name__ == "__main__":
    main()
