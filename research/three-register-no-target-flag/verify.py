#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the no-target-flag extension; optionally cold-replay its full dependency."""

import argparse
from copy import deepcopy
from hashlib import sha256
from itertools import combinations, permutations
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from check_lemmas import build_certificate, multiply, require

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREDECESSOR = REPO / "research/bit-three-register-lower-bound"


def source_check():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for name, expected in pins["files"].items():
        require(sha256((REPO / name).read_bytes()).hexdigest() == expected,
                f"source pin mismatch: {name}")
    return pins


def matrix_product(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)]
            for i in range(3)]


def polynomial_product(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return result


def characteristic_polynomial(a):
    result = [0] * 4
    for order in permutations(range(3)):
        term = [1]
        for i, j in enumerate(order):
            term = polynomial_product(term, [-a[i][j], int(i == j)])
        sign = (-1) ** sum(order[i] > order[j] for i in range(3) for j in range(i + 1, 3))
        for i, value in enumerate(term):
            result[i] += sign * value
    return result


def nonzero_rank_one(frame):
    return any(frame) and all(
        frame[3 * i + k] * frame[3 * j + l] == frame[3 * i + l] * frame[3 * j + k]
        for i, j in combinations(range(3), 2) for k, l in combinations(range(3), 2))


def formal_product(word):
    """Multiply all formal coefficients; rational-address integers stay integers."""
    zero = (0,) * 9
    terms = {zero: 273}
    for frame, projector in word:
        updated = {}
        for exponent, coefficient in terms.items():
            for shift, scalar in ((zero, 273 ^ projector), (frame, projector)):
                target = tuple(x + y for x, y in zip(exponent, shift))
                updated[target] = updated.get(target, 0) ^ multiply(coefficient, scalar)
        terms = {target: coefficient for target, coefficient in updated.items() if coefficient}
    return terms


def target_example():
    identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    companion = [[0, 0, 2], [1, 0, 0], [0, 1, 0]]
    targets = [identity, companion, matrix_product(companion, companion)]
    flat = [tuple(x for row in a for x in row) for a in targets]
    polynomial = characteristic_polynomial(companion)
    require(polynomial == [-2, 0, 0, 1], "companion characteristic polynomial")
    require(polynomial[-1] % 2 != 0 and all(c % 2 == 0 for c in polynomial[:-1])
            and polynomial[0] % 4 != 0, "Eisenstein conditions at two")
    require(matrix_product(companion, targets[2]) == [[2 * x for x in row] for row in identity],
            "companion cube")
    require([characteristic_polynomial(a)[0] for a in targets] == [-1, -2, -4],
            "target invertibility")
    word = []
    for w, a in enumerate(targets):
        for column in range(3):
            frame = tuple(a[i][j] if j == column else 0 for i in range(3) for j in range(3))
            require(nonzero_rank_one(frame), "column frame rank one")
            word.append((frame, 1 << (4 * w)))
    expected = {frame: 1 << (4 * w) for w, frame in enumerate(flat)}
    require(formal_product(word) == expected, "nine-call unflagged endpoint")
    require(formal_product(word[:-1]) != expected, "omitted frame must change endpoint")
    changed = deepcopy(word)
    frame, scalar = changed[0]
    changed[0] = (tuple(3 * x for x in frame), scalar)
    require(nonzero_rank_one(changed[0][0]), "mutant frame remains rank one")
    require(formal_product(changed) != expected, "rational-address change must be detected")
    reduce_mod_two = lambda operations: [(tuple(x % 2 for x in frame), scalar)
                                         for frame, scalar in operations]
    require(formal_product(reduce_mod_two(changed)) == formal_product(reduce_mod_two(word)),
            "invalid address reduction would hide the mutation")
    return {"targets": targets, "characteristic_polynomial_ascending": polynomial,
            "irreducibility_certificate": {"criterion": "Eisenstein", "prime": 2},
            "nine_rank_one_calls": [{"frame": list(frame), "scalar_projector": scalar}
                                    for frame, scalar in word],
            "formal_endpoint_checked": True,
            "negative_controls": ["omitted column changes endpoint",
                                  "rank-one address mutation detected before invalid reduction mod two"]}


def check_replay_result(result, pins):
    for key, expected in {"families": 2276, "orders": 21317520,
                          "diagonal_terminals": 415398, "survivors": 0}.items():
        require(result[key] == expected, f"full replay count: {key}")
    require(result["all_per_case_counts_agree"] is True, "per-family engine agreement")
    require(result["core_positive_accepted"] is True and result["core_rank_two_mutation_rejected"] is True,
            "inherited core controls")
    require(result["formal_controls"] == {"nine_call_identity": True, "modular_alias_rejected": True,
                                         "noncommuting_eight_call_identity": True,
                                         "frame_span": 5, "target_rank": 2},
            "inherited formal controls")
    require(set(result["source_sha256"]) == {"catalogue.py", "rational.cpp", "f101.cpp"},
            "full replay source inventory")
    for name, actual in result["source_sha256"].items():
        require(actual == pins["files"][f"research/bit-three-register-lower-bound/{name}"],
                f"full replay source pin: {name}")
    expected = json.loads((PREDECESSOR / "expected.json").read_text())
    require(result["catalogue_sha256"] == expected["catalogue_sha256"], "catalogue digest")


def full_replay(work, pins):
    work.mkdir(parents=True, exist_ok=True)
    # The inherited replay uses assertions: always enable them in the child,
    # even when the quick checker is invoked under optimized Python.
    environment = {**os.environ, "PYTHONOPTIMIZE": "0"}
    command = [sys.executable, "-B", "-S", str(PREDECESSOR / "replay.py"),
               "--work-dir", str(work)]
    with (work / "driver.log").open("w") as log:
        outcome = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=environment)
    require(outcome.returncode == 0, f"Full replay failed; inspect {work / 'driver.log'}")
    result = json.loads((work / "driver.log").read_text())
    source_check()
    check_replay_result(result, pins)
    print(f"PASS_FULL_PR468_REPLAY: {result['orders']} orders, {result['survivors']} survivors")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="Run both complete inherited exact engines")
    parser.add_argument("--work-dir", type=Path, help="Keep full-replay logs and outputs here")
    parser.add_argument("--write-certificate", action="store_true", help="Regenerate this package's finite certificate")
    args = parser.parse_args()
    require(args.work_dir is None or args.full, "--work-dir requires --full")
    pins = source_check()
    certificate = {"lemmas": build_certificate(), "strictly_unflagged_example": target_example()}
    expected = HERE / "CERTIFICATE.json"
    if args.write_certificate:
        expected.write_text(json.dumps(certificate, sort_keys=True, separators=(",", ":")) + "\n")
    else:
        require(certificate == json.loads(expected.read_text()), "finite certificate mismatch")
    print("PASS_NINE_CALLS_WITHOUT_TARGET_FLAG", flush=True)
    print(json.dumps(certificate["lemmas"]["summary"], sort_keys=True), flush=True)
    if args.full:
        if args.work_dir is None:
            with TemporaryDirectory(prefix="three-register-no-flag-") as tmp:
                full_replay(Path(tmp), pins)
        else:
            full_replay(args.work_dir.resolve(), pins)


if __name__ == "__main__":
    main()
