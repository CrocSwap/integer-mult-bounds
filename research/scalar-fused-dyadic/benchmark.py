"""Alternating fresh-process full audits; timings are evidence, not gates.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance; Apache-2.0.
"""

import argparse
import hashlib
import importlib.util
import json
import platform
import resource
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("differential", HERE / "verify.py")
verification = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verification)
require = verification.require


def measure(rounds):
    require(rounds >= 1, "at least one round required")
    raw = verification.word_bytes()
    expected = verification.expected_report()
    samples = []
    with tempfile.TemporaryDirectory(prefix="fused scalar benchmark ") as temporary:
        directory = Path(temporary)
        word = directory / "FULL-WORD.json.gz"
        word.write_bytes(raw)
        for round_id in range(rounds):
            engines = ("reference", "fused") if round_id % 2 == 0 else ("fused", "reference")
            for engine in engines:
                output = directory / (str(round_id) + "-" + engine + ".json")
                # -I and -B are fixed for both arms. Each timed process includes
                # imports, source checks, parent binding, every original audit
                # phase, receipt serialization and ordinary stdout production.
                command = [sys.executable, "-B", "-I", str(HERE / "adapter.py"),
                           "--engine", engine, "--word", str(word), "--output", str(output)]
                before = resource.getrusage(resource.RUSAGE_CHILDREN)
                started = time.perf_counter()
                child = subprocess.run(command, capture_output=True, text=True)
                wall = time.perf_counter() - started
                after = resource.getrusage(resource.RUSAGE_CHILDREN)
                require(child.returncode == 0, "timed child failed: " + child.stderr)
                report = json.loads(output.read_bytes())
                stable = verification.stable(report)
                require(verification.canonical(stable) == verification.canonical(expected), "timed receipt differs")
                require(word.read_bytes() == raw, "timed input changed")
                verification.adapter.source_pins()
                sample = {"round": round_id, "engine": engine, "wall_seconds": wall,
                          "child_cpu_seconds": after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
                          "auditor_seconds": report["elapsed_seconds"],
                          "receipt_sha256_without_timing": hashlib.sha256(verification.canonical(stable).encode()).hexdigest()}
                samples.append(sample)
                print(engine, round_id, format(wall, ".6f"), "s", flush=True)
    medians = {engine: {metric: statistics.median(s[metric] for s in samples if s["engine"] == engine)
                        for metric in ("wall_seconds", "child_cpu_seconds", "auditor_seconds")}
               for engine in ("reference", "fused")}
    return {"status": "PASS_IDENTICAL_COMPLETE_SCALAR_AUDITS", "rounds": rounds,
            "python": sys.version, "executable": sys.executable, "platform": platform.platform(),
            "cpu": platform.processor(), "clock": vars(time.get_clock_info("perf_counter")),
            "source_pins": verification.adapter.source_pins(),
            "implementation_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in [HERE / "adapter.py", HERE / "kernel.py"]},
            "method": "alternating fresh processes; same input; no cache flushing or host isolation; timing is not a pass threshold",
            "samples": samples, "medians": medians,
            "wall_speedup": medians["reference"]["wall_seconds"] / medians["fused"]["wall_seconds"],
            "complete_receipt": expected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), "output already exists")
    result = measure(args.rounds)
    with args.output.open("x") as output:
        json.dump(result, output, indent=2, sort_keys=True)
        output.write("\n")
    print("PASS_IDENTICAL_COMPLETE_SCALAR_AUDITS rounds=" + str(args.rounds) +
          " median_wall_speedup=" + format(result["wall_speedup"], ".3f"))


if __name__ == "__main__":
    main()
