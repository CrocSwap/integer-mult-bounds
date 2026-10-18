#!/usr/bin/env python3
"""Alternating fresh-process before/after timings for production data-corner.

Timing is descriptive evidence for RESULT.json. Equivalence is enforced by
verify.py; this script fails only on unequal receipts or subprocess errors.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import resource
import shlex
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research" / "copied-fixed" / "data_corners.cpp"
RECEIPT = ROOT / "research" / "copied-fixed" / "data-corners.json"

GUARD = '#ifdef NDEBUG\n#error "Data-corner replay requires assertions"\n#endif\n'


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def compile_program(source: str, output: Path, compiler: list[str]) -> None:
    path = output.with_suffix(".cpp")
    path.write_text(GUARD + source, encoding="utf-8")
    subprocess.run(
        [*compiler, "-O3", "-std=c++17", str(path), "-o", str(output)],
        check=True,
        capture_output=True,
    )


def timed_run(executable: Path, expected: dict) -> dict:
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    result = subprocess.run([str(executable)], capture_output=True, check=True)
    wall = time.perf_counter() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    require(json.loads(result.stdout) == expected, "receipt mismatch during benchmark")
    return dict(
        wall_seconds=wall,
        cpu_seconds=(after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime),
        stdout_sha256=sha256(result.stdout).hexdigest(),
        stderr_sha256=sha256(result.stderr).hexdigest(),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    require(args.rounds >= 1, "need at least one round")
    require(not args.out.exists(), "output already exists")

    baseline = (PACKAGE / "baseline.cpp").read_text(encoding="utf-8")
    production = PRODUCTION.read_text(encoding="utf-8")
    expected = json.loads(RECEIPT.read_text(encoding="utf-8"))
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    version = subprocess.check_output([*compiler, "--version"], text=True)

    samples = []
    with tempfile.TemporaryDirectory(prefix="data-corner-bench-") as tmp:
        work = Path(tmp)
        compile_program(baseline, work / "baseline", compiler)
        compile_program(production, work / "optimized", compiler)
        for round_index in range(args.rounds):
            order = (
                ("baseline", "optimized")
                if round_index % 2 == 0
                else ("optimized", "baseline")
            )
            for engine in order:
                sample = timed_run(work / engine, expected)
                samples.append(dict(pair=round_index, mode=engine, **sample))
                print(
                    f"PASS pair={round_index} {engine} wall={sample['wall_seconds']:.3f}s",
                    flush=True,
                )

    medians = {
        mode: statistics.median(s["wall_seconds"] for s in samples if s["mode"] == mode)
        for mode in ("baseline", "optimized")
    }
    report = dict(
        status="PASS_IDENTICAL_DATA_CORNER_PRODUCTION_RECEIPTS",
        base_commit="0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        rounds=args.rounds,
        platform=platform.platform(),
        python=platform.python_version(),
        compiler=compiler,
        compiler_version=version,
        flags=["-O3", "-std=c++17"],
        source_sha256={
            "research/data-corner-production/baseline.cpp": sha256(
                (PACKAGE / "baseline.cpp").read_bytes()
            ).hexdigest(),
            "research/copied-fixed/data_corners.cpp": sha256(PRODUCTION.read_bytes()).hexdigest(),
            "research/copied-fixed/data-corners.json": sha256(RECEIPT.read_bytes()).hexdigest(),
        },
        wall_medians=medians,
        speedup=medians["baseline"] / medians["optimized"],
        coverage={
            k: expected[k]
            for k in ("pairs", "good", "fallback", "nonzero_pivots", "ordered_zero_checks")
        },
        samples=samples,
    )
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS_IDENTICAL_DATA_CORNER_PRODUCTION_RECEIPTS")
    print(
        f"median baseline={medians['baseline']:.3f}s "
        f"optimized={medians['optimized']:.3f}s "
        f"speedup={report['speedup']:.3f}x"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
