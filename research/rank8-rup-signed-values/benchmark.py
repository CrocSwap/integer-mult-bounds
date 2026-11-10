#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Measure five alternating complete fresh-process runs per side and unit."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import statistics
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("signed_verify", HERE / "verify.py")
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load verification driver")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def measure(unit: str, output: Path) -> dict:
    elapsed = {"baseline": [], "candidate": []}
    reference = None
    checked = 0
    for index in range(5):
        for engine in ("baseline", "candidate"):
            path = output / f"{unit}-{index}-{engine}.json"
            start = time.perf_counter_ns()
            stdout, certificate = verify.run(engine, unit, path)
            seconds = (time.perf_counter_ns() - start) / 1e9
            result = stdout, certificate
            if reference is None:
                reference = result
            verify.require(result == reference, "benchmark output/certificate mismatch")
            elapsed[engine].append(seconds)
            checked += len(certificate["log"])
    verify.require(reference is not None, "empty workload")
    medians = {engine: statistics.median(values) for engine, values in elapsed.items()}
    return {"unit": unit, "seconds": elapsed, "medians": medians,
            "ranges": {engine: [min(values), max(values)] for engine, values in elapsed.items()},
            "wall_time_reduction_percent": 100 * (1 - medians["candidate"] / medians["baseline"]),
            "errors": 0, "scientific_checks_executed": checked,
            "stdout_sha256": hashlib.sha256(reference[0]).hexdigest(),
            "certificate_sha256": hashlib.sha256(json.dumps(reference[1], sort_keys=True).encode()).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    verify.adapter.authenticated_source()
    result = {"python": sys.version, "platform": platform.platform(),
              "timer": "perf_counter_ns around completed subprocess and output validation",
              "runs_per_side_per_unit": 5, "order": "baseline,candidate repeated five times",
              "units": [measure(unit, args.output_dir) for unit in ("P112", "P120")]}
    result["files"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sorted(HERE.glob("*.py"))}
    (args.output_dir / "BENCHMARK.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
