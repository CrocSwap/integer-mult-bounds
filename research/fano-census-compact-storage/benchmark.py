#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with substantial OpenAI Codex assistance.
"""Measure four complete census modes in fresh CPython processes on Linux.

Elapsed time includes process startup and the complete worker. GNU time reports
the worker's peak resident set in KiB. Timings are descriptive, not acceptance
thresholds; every sample must reproduce the same complete receipt and census.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import statistics
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODES = ("baseline", "compact", "rowtables", "rowtables-compact")
TIME = Path("/usr/bin/time")
RECEIPT_KEYS = {
    "receipt_sha256", "receipt_bytes", "census_sha256", "reduced_triples",
    "class_size_histogram", "relation_words",
}


def mode_order(repetition):
    """Reverse the complete order on odd, zero-based repetitions."""
    return MODES if repetition % 2 == 0 else tuple(reversed(MODES))


def parse_receipt(stdout, mode):
    value = json.loads(stdout)
    if not isinstance(value, dict) or value.get("mode") != mode:
        raise ValueError("worker mode does not match requested mode")
    receipt = {key: item for key, item in value.items() if key != "mode"}
    if set(receipt) != RECEIPT_KEYS:
        raise ValueError("unexpected complete worker receipt fields")
    for key in ("receipt_sha256", "census_sha256"):
        digest = receipt[key]
        if (not isinstance(digest, str) or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)):
            raise ValueError("invalid worker digest: " + key)
    return receipt


def source_hashes():
    """Bind the measured code, optional table engine and every fixture input."""
    manifest_path = HERE / "SOURCES.json"
    manifest = json.loads(manifest_path.read_bytes())
    paths = {HERE / name for name in (
        "benchmark.py", "worker.py", "kernel.py", "SOURCES.json",
        "PREDECESSOR.json", "inputs/pr3219-kernel.py",
    )}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("relative source path required")
        path = ROOT / relative
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("source hash: " + row["path"])
        paths.add(path)
    return {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths)}


def run_sample(mode, timeout_seconds):
    if mode not in MODES:
        raise ValueError("unknown benchmark mode")
    worker_argv = [sys.executable, "-I", "-B", str(HERE / "worker.py"), "--mode", mode]
    with tempfile.TemporaryDirectory(prefix="fano-census-benchmark-") as scratch:
        rss_path = Path(scratch) / "peak-rss-kib.txt"
        argv = [str(TIME), "-f", "%M", "-o", str(rss_path), "--", *worker_argv]
        started = time.perf_counter()
        process = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True,
                                   encoding="utf-8", start_new_session=True)
        try:
            stdout, stderr = process.communicate(timeout=timeout_seconds)
        except BaseException as error:
            # Killing only GNU time would leave its Python worker running.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
            if isinstance(error, subprocess.TimeoutExpired):
                raise TimeoutError("complete worker timed out: " + mode) from None
            raise
        elapsed = time.perf_counter() - started
        if process.returncode != 0:
            raise RuntimeError(f"worker {mode} failed ({process.returncode}): {stderr[-2000:]}")
        raw_rss = rss_path.read_text(encoding="ascii").strip()
        if not raw_rss.isdecimal() or int(raw_rss) <= 0:
            raise ValueError("GNU time did not report a positive peak RSS in KiB")
        return {"mode": mode, "argv": argv, "worker_argv": worker_argv,
                "cwd": str(ROOT), "elapsed_seconds": elapsed,
                "peak_rss_kib": int(raw_rss), "receipt": parse_receipt(stdout, mode),
                "stderr": stderr}


def environment():
    cpu = platform.processor()
    for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip() in ("model name", "Hardware"):
            cpu = value.strip()
            break
    return {"python_executable": sys.executable, "python_version": sys.version,
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(), "machine": platform.machine(),
            "cpu": cpu, "logical_cpu_count": os.cpu_count()}


def describe(values):
    return {"min": min(values), "max": max(values),
            "mean": statistics.mean(values), "median": statistics.median(values)}


def benchmark(repetitions=4, timeout_seconds=120):
    if platform.system() != "Linux" or platform.python_implementation() != "CPython":
        raise RuntimeError("this peak-RSS benchmark requires Linux and CPython")
    if not TIME.is_file():
        raise RuntimeError("GNU time is required at /usr/bin/time")
    if type(repetitions) is not int or repetitions < 1:
        raise ValueError("positive integer repetitions required")
    if type(timeout_seconds) is not int or timeout_seconds < 1:
        raise ValueError("positive integer timeout required")
    hashes = source_hashes()
    samples = []
    expected = None
    for repetition in range(repetitions):
        for mode in mode_order(repetition):
            sample = run_sample(mode, timeout_seconds)
            sample["repetition"] = repetition + 1
            sample["position"] = len(samples) + 1
            if expected is None:
                expected = sample["receipt"]
            elif sample["receipt"] != expected:
                raise ValueError("complete receipt or census differs across benchmark samples")
            samples.append(sample)
            print("SAMPLE", sample["position"], mode, sample["elapsed_seconds"],
                  sample["peak_rss_kib"], flush=True)
    if source_hashes() != hashes:
        raise ValueError("benchmark sources changed during measurement")
    summary = {}
    for mode in MODES:
        selected = [sample for sample in samples if sample["mode"] == mode]
        summary[mode] = {"samples": len(selected),
                         "elapsed_seconds": describe([s["elapsed_seconds"] for s in selected]),
                         "peak_rss_kib": describe([s["peak_rss_kib"] for s in selected])}
    return {"schema_version": 1, "environment": environment(),
            "repetitions": repetitions, "timeout_seconds_per_process": timeout_seconds,
            "measurement": {
                "elapsed_seconds": "parent perf_counter around the whole fresh GNU time / worker process",
                "peak_rss_kib": "GNU /usr/bin/time -f %M; Linux peak resident set in KiB",
                "order": "four modes in declared order, reversed on every other repetition",
                "acceptance": "successful workers and identical complete receipt/census; no performance threshold",
            },
            "source_sha256": hashes, "receipt": expected, "samples": samples,
            "summary": summary}


def positive_integer(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repetitions", type=positive_integer, default=4)
    parser.add_argument("--timeout-seconds", type=positive_integer, default=120)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error("output already exists")
    if not args.output.parent.is_dir():
        parser.error("output parent directory does not exist")
    result = benchmark(args.repetitions, args.timeout_seconds)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print("PASS_FANO_COMPACT_BENCHMARK", len(result["samples"]), "samples", args.output)
    for mode, values in result["summary"].items():
        print(mode, "mean seconds", values["elapsed_seconds"]["mean"],
              "mean peak RSS KiB", values["peak_rss_kib"]["mean"])


if __name__ == "__main__":
    main()
