#!/usr/bin/env python3
"""Source-bound finite propagation audit. Nick Petalas. Apache-2.0."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/connector-covering-code/cycle_search.cpp"
FLAGS = ["-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Werror"]
MUTANTS = [
    ("endpoint", "a.end == b.start", "a.end != b.start"),
    ("disjointness", "(a.mask & b.mask) == 0", "(a.mask & b.mask) != 0"),
    ("conditional", "if (i != a && i != b) excluding[i][difference] |= contribution;",
     "if (false) excluding[i][difference] |= contribution;"),
    ("totals", "sum_min[label] - minima[i][label] + value > target[label]",
     "sum_min[label] - minima[i][label] + value >= target[label]"),
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_bytes(path):
    require(path.is_file() and not path.is_symlink(), f"not a regular input: {path}")
    require(path.stat().st_size <= 256_000, f"oversized input: {path}")
    return path.read_bytes()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def authenticate():
    pins = json.loads(bounded_bytes(PACKAGE / "SOURCES.json"))
    require(len(pins["files"]) <= 16, "pin inventory limit")
    for row in pins["files"]:
        if row["usage"] == "input":
            data = bounded_bytes(ROOT / row["path"])
            require(sha256(data) == row["sha256"],
                    f"source hash mismatch: {row['path']}")
    source = bounded_bytes(ROOT / SOURCE)
    driver = bounded_bytes(PACKAGE / "audit.cpp")
    expected = json.loads(bounded_bytes(PACKAGE / "RESULT.json"))
    require(expected["source_sha256"] == sha256(source), "receipt source hash mismatch")
    require(expected["driver_sha256"] == sha256(driver), "receipt driver hash mismatch")
    return source, driver, expected["counts"]


def native_run(source, driver, directory, compiler, sanitize=False):
    (directory / "cycle_search.cpp").write_bytes(source)
    (directory / "audit.cpp").write_bytes(driver)
    flags = FLAGS.copy()
    if sanitize:
        flags[1:2] = ["-O1", "-g", "-fsanitize=address,undefined",
                      "-fno-omit-frame-pointer"]
    binary = directory / "audit"
    build = subprocess.run([compiler, *flags, "audit.cpp", "-o", str(binary)],
                           cwd=directory, text=True, capture_output=True,
                           timeout=90, check=False)
    require(build.returncode == 0, f"compile failed:\n{build.stdout}{build.stderr}")
    require(not build.stderr, f"compiler diagnostics:\n{build.stderr}")
    env = os.environ.copy()
    env.update(ASAN_OPTIONS="detect_leaks=1", UBSAN_OPTIONS="halt_on_error=1")
    return subprocess.run([str(binary)], cwd=directory, text=True, capture_output=True,
                          timeout=90, env=env, check=False)


def source_mutants(source, driver, directory, compiler):
    text = source.decode("utf-8")
    for name, before, after in MUTANTS:
        require(text.count(before) == 1, f"ambiguous mutation: {name}")
        mutant = directory / name
        mutant.mkdir()
        result = native_run(text.replace(before, after).encode(), driver,
                            mutant, compiler)
        require(result.returncode == 1 and "AUDIT_ERROR" in result.stderr,
                f"native unsound mutant survived or crashed: {name}")
    return len(MUTANTS)


def export_failure_controls(directory, work):
    # This is a small source export, not a Git checkout or another worktree.
    exported = directory / "export"
    target = exported / "research/connector-path-propagation-audit"
    target.mkdir(parents=True)
    names = ["verify.py", "audit.cpp", "SOURCES.json", "RESULT.json"]
    for name in names:
        (target / name).write_bytes(bounded_bytes(PACKAGE / name))
    pins = json.loads(bounded_bytes(PACKAGE / "SOURCES.json"))
    for row in pins["files"]:
        if row["usage"] == "input":
            destination = exported / row["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(bounded_bytes(ROOT / row["path"]))
    command = [sys.executable, "-I", "-B", str(target / "verify.py"),
               "--work", str(work)]
    source_path = exported / SOURCE
    original = source_path.read_bytes()
    source_path.write_bytes(original + b"\n")
    bad_pin = subprocess.run(command, text=True, capture_output=True,
                             timeout=120, check=False)
    require(bad_pin.returncode == 1 and "source hash mismatch" in bad_pin.stderr,
            "changed source accepted by direct verifier")
    source_path.write_bytes(original)
    receipt_path = target / "RESULT.json"
    receipt = json.loads(receipt_path.read_bytes())
    receipt["counts"]["lost_feasible_choices"] = 1
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    bad_receipt = subprocess.run(command, text=True, capture_output=True,
                                 timeout=120, check=False)
    require(bad_receipt.returncode == 1
            and "fresh native receipt differs" in bad_receipt.stderr,
            "corrupted expected receipt accepted")
    return 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path,
                        help="existing parent for disposable builds")
    parser.add_argument("--failure-controls", action="store_true")
    parser.add_argument("--sanitize", action="store_true")
    args = parser.parse_args()
    source, driver, expected = authenticate()
    compiler = shutil.which("g++")
    require(compiler is not None, "g++ with C++17 support is required")
    if args.work is not None:
        require(args.work.is_dir(), "--work must be an existing directory")
    with tempfile.TemporaryDirectory(
        prefix="connector-propagation-", dir=args.work
    ) as name:
        directory = Path(name)
        result = native_run(source, driver, directory, compiler, args.sanitize)
        require(result.returncode == 0,
                f"native audit failed:\n{result.stdout}{result.stderr}")
        require(not result.stderr, f"native diagnostics:\n{result.stderr}")
        actual = json.loads(result.stdout)
        require(actual == expected, "fresh native receipt differs from RESULT.json")
        require(actual["lost_feasible_choices"] == 0
                and actual["conditional_removed"] > 0,
                "preservation/conditional-coverage gate failed")
        failures = 0
        if args.failure_controls:
            failures += source_mutants(source, driver, directory, compiler)
            failures += export_failure_controls(directory, directory)
        print("PASS_CONNECTOR_PATH_PROPAGATION "
              f"relations={actual['relations']} tuples={actual['tuples']} "
              f"feasible_choices={actual['feasible_choices']} lost=0 "
              f"failure_controls={failures} no_full_census")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        raise SystemExit(f"AUDIT_ERROR {error}") from error
