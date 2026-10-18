#!/usr/bin/env python3
"""Offline serial C++17 replay of the finite cycle and multiplicity censuses.

By conorholds, with substantial OpenAI Codex assistance. Apache-2.0.
Builds only in a temporary directory. CXX and SDKROOT overrides are inherited;
no compiler, SDK, dependency or network download is performed.
"""

import argparse
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile


def need(condition, message):
    if not condition:
        raise ValueError(message)


def run_json(command, directory, timeout):
    result = subprocess.run(command, cwd=directory, text=True,
                            stdout=subprocess.PIPE, timeout=timeout, check=False)
    print(result.stdout, end="", flush=True)
    need(result.returncode == 0, f"finite verifier exited {result.returncode}; no successful exhaustion claimed")
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]


def check_controls(records):
    controls = {row["pattern"]: row for row in records if row.get("controls") == "PASS"}
    need(set(controls) == {"A", "B"}, "both path-decomposition controls must pass")
    for pattern, row in controls.items():
        need(row["normalized_paths"] == 106 and row["translated_candidates"] == 848,
             "complete Q3 path table")
        need(row["universal_low_dihedral_orbits"] == (5 if pattern == "A" else 77),
             "complete low-projection orbit census")
        need(row["positive_simple24_coverage"] == 128
             and row["negative_simple22_coverage"] == (116 if pattern == "A" else 126),
             "ordinary positive and noncover controls")
        need(all(row[key] is True for key in
                 ("repeated_origin_rejected", "wrong_count_rejected", "wrong_join_rejected")),
             "simplicity, multiplicity and joining failure controls")
        need(row["full_enumeration_rediscovered"] is True
             and row["full_enumeration_nodes"] > row["full_enumeration_capacity_survivors"] > 0
             and row["full_enumeration_compositions"] >= row["full_enumeration_capacity_survivors"],
             "the full gap/capacity/branching search path rediscovers the simple24 fixture")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=300,
                        help="native cycle-census budget, excluding compilation, premises and controls")
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    need(math.isfinite(args.seconds) and 0 < args.seconds <= 86400, "finite positive budget at most86400 seconds")
    source = Path(__file__).with_name("cycle_search.cpp").resolve()
    compiler = shlex.split(os.environ.get("CXX", "c++"))
    need(compiler and shutil.which(compiler[0]), "C++17 compiler missing; set CXX to an installed compiler")
    source_digest = sha256(source.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix="covering-cycle-replay-") as directory:
        binary = str(Path(directory) / "cycle_search")
        compiled = subprocess.run([*compiler, "-std=c++17", "-O3", str(source), "-o", binary],
                                  cwd=directory, timeout=60, check=False)
        need(compiled.returncode == 0, "C++17 compilation failed; CXX and SDKROOT may be overridden externally")
        if args.controls_only:
            check_controls(run_json([binary, "--controls-only"], directory, 90))
            print(json.dumps({"verification": "PASS_CONTROLS_ONLY", "scope": "controls-only",
                              "complete_orbits": 0,
                              "source_sha256": source_digest}, sort_keys=True))
            return
        premises = run_json([binary, "--premises-only"], directory, 120)
        actual = {(row["dimension"], row["length"], row["canonical_words"], row["maximum_coverage"])
                  for row in premises if row.get("premise") == "PASS"}
        need(len(premises) == 3 and actual == {(5, 10, 945, 31), (6, 12, 10395, 49),
                                             (6, 14, 945945, 59)}, "complete f5/f6 premise censuses")
        records = run_json([binary, "--seconds", str(args.seconds)], directory, args.seconds + 90)
        check_controls(records)
        cycles = [row for row in records if "exhausted" in row]
        expected = {("A", index) for index in range(1, 6)} | {("B", index) for index in range(1, 78)}
        need(len(cycles) == 82 and {(row["pattern"], row["template"]) for row in cycles} == expected,
             "every one of the82 low-projection orbits must be replayed exactly once")
        need(all(row["exhausted"] is True and row["found"] is False for row in cycles),
             "every finite branch must be exhausted without a universal simple22 word")
        need(records[-1].get("all_requested_exhausted") is True
             and records[-1].get("completed_orbits") == 82, "complete native census receipt")
    print(json.dumps({"verification": "PASS", "complete_orbits": 82, "multiplicity_cases": 3,
                      "source_sha256": source_digest}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        raise SystemExit(f"FAIL {error}") from error
