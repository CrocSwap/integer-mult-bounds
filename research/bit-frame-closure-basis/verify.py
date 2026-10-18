"""Replay both engines, compare every closure, and run independent controls."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import statistics

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run


def check_benchmark(expected, evidence=None):
    if evidence is None:
        evidence = json.loads((HERE / "BENCHMARK.json").read_text())
    names = {"closure.py", "run.py", "benchmark.py", "EXPECTED.json", "SOURCES.json"}
    run.require(set(evidence["implementation_sha256"]) == names, "benchmark input inventory")
    for name, digest in evidence["implementation_sha256"].items():
        run.require(run.sha((HERE / name).read_bytes()) == digest, "benchmark source binding: " + name)
    samples = evidence["samples"]
    run.require(bool(samples), "benchmark samples")
    for index, sample in enumerate(samples):
        order = ["reference", "basis"] if index % 2 == 0 else ["basis", "reference"]
        run.require(sample["pair"] == index and sample["order"] == order, "alternating benchmark pairs")
        for engine in order:
            cases = sample["engines"][engine]["cases"]
            run.require(set(cases) == set(expected), "benchmark case coverage")
            for case in cases:
                digest = run.sha(run.canonical(expected[case]).encode())
                run.require(cases[case]["report_sha256"] == digest, "benchmark complete receipt: " + case)
    medians = {engine: statistics.median(s["engines"][engine]["seconds"] for s in samples)
               for engine in ("reference", "basis")}
    run.require(medians == evidence["median_suite_seconds"], "benchmark median arithmetic")
    run.require(evidence["suite_ratio"] == medians["reference"] / medians["basis"],
                "benchmark ratio arithmetic")
    # There is deliberately no speed threshold: timings are descriptive.


def main():
    run.check_sources()
    expected = json.loads((HERE / "EXPECTED.json").read_text())
    check_benchmark(expected)
    comparisons = []
    with tempfile.TemporaryDirectory(prefix="bit-frame-closure-") as temp:
        for case in run.CASES:
            reports, inventories = {}, {}
            for engine in ("reference", "basis"):
                destination = Path(temp) / (case + "-" + engine + ".json")
                command = [sys.executable, "-I", "-B", str(HERE / "run.py"),
                           "--case", case, "--engine", engine,
                           "--closure-output", str(destination)]
                process = subprocess.run(command, capture_output=True, text=True, timeout=150)
                run.require(process.returncode == 0, engine + " " + case + ": " + process.stderr)
                reports[engine] = json.loads(process.stdout)
                inventories[engine] = json.loads(destination.read_text())
                run.require(reports[engine] == expected[case], "complete receipt: " + engine + " " + case)
            run.require(inventories["reference"] == inventories["basis"],
                        "every closure mask and rank: " + case)
            comparisons.append({"case": case, "closures": len(inventories["basis"]),
                                "assignments": reports["basis"]["receipt"]["assignments_enumerated"]})
    process = subprocess.run([sys.executable, "-I", "-B", str(HERE / "test_closure.py")],
                             timeout=150)
    run.require(process.returncode == 0, "rational oracle and negative controls")
    print(run.canonical({"status": "PASS_BIT_FRAME_CLOSURE_BASIS", "cases": comparisons,
                         "no_new_kappa": True}))


if __name__ == "__main__":
    main()
