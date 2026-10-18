#!/usr/bin/env python3
"""Alternate complete cold processes and exact in-memory RUP checks."""
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

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import replay


def summary(samples):
    return {"seconds": samples,
            "median_baseline_seconds": statistics.median(p["baseline"] for p in samples),
            "median_epochs_seconds": statistics.median(p["epochs"] for p in samples),
            "median_paired_speedup": statistics.median(p["baseline"] / p["epochs"] for p in samples)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    replay.need(args.pairs > 0, "positive pair count required")
    module = replay.load()
    expected = module.read_json(module.ROOT / "EXPECTED.json")
    reference = module.lrat.check
    cases = {}

    def capture(proof, original, variables, initial_clauses):
        result = reference(proof, original, variables, initial_clauses)
        for name, certificate in expected["certificates"].items():
            if result == certificate["proof"]:
                cases.setdefault(name, (proof, original, variables, initial_clauses))
        return result

    with replay.checker(module, capture):
        receipt = module.compute()
    replay.need(replay.canonical(receipt) == replay.canonical(expected), "baseline receipt")
    replay.need(set(cases) == {"8", "9"}, "both complete proofs captured")
    kernels = {name: [] for name in cases}
    full = []
    with tempfile.TemporaryDirectory(prefix="p111-rup-benchmark-") as directory:
        for pair in range(args.pairs):
            order = ("baseline", "epochs") if pair % 2 == 0 else ("epochs", "baseline")
            times = {}
            for engine in order:
                path = Path(directory) / (engine + ".json")
                start = time.perf_counter()
                process = subprocess.run(
                    [sys.executable, "-I", "-O", "-B", str(ROOT / "replay.py"),
                     "--engine", engine, "--receipt", str(path)],
                    cwd=directory, capture_output=True, text=True, check=True)
                times[engine] = time.perf_counter() - start
                replay.need(path.read_bytes() == replay.canonical(expected) + b"\n",
                            "complete cold receipt equality")
                replay.need(json.loads(process.stdout)["status"] == "PASS", "cold status")
            full.append(times)
            for name, arguments in sorted(cases.items()):
                times = {}
                for engine in order:
                    function = reference if engine == "baseline" else replay.candidate.check
                    start = time.perf_counter()
                    result = function(*arguments)
                    times[engine] = time.perf_counter() - start
                    replay.need(result == expected["certificates"][name]["proof"], "RUP receipt equality")
                kernels[name].append(times)
    report = {
        "status": "PASS", "scope": "Verifier wall time only; no multiplication runtime or kappa claim",
        "pairs": args.pairs, "order": "baseline first on even-indexed pairs; epochs first on odd",
        "environment": {"python": sys.version, "executable": sys.executable,
                        "platform": platform.platform(), "machine": platform.machine(),
                        "cold_flags": ["-I", "-O", "-B"], "kernel_optimize": sys.flags.optimize},
        "source_manifest_sha256": hashlib.sha256((ROOT / "SOURCES.json").read_bytes()).hexdigest(),
        "implementation_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                                  for name in ("candidate.py", "replay.py", "benchmark.py")},
        "complete_receipt_sha256": hashlib.sha256(replay.canonical(expected)).hexdigest(),
        "proof_additions": 37044, "hints_checked": 1409475,
        "cold_process": summary(full),
        "rup_check_only": {name: summary(times) for name, times in kernels.items()},
        "coverage": "Full formula regeneration, original encoder comparison, geometry, positive calibration, parsing, every proof hint, original controls and exact EXPECTED.json equality remain enabled. Kernel inputs prepared once outside kernel timing; database copy and epoch allocation are included. No retained proof result is cached."
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "pairs": args.pairs,
                      "cold_speedup": report["cold_process"]["median_paired_speedup"],
                      "c9_rup_speedup": report["rup_check_only"]["9"]["median_paired_speedup"]}))


if __name__ == "__main__":
    main()
