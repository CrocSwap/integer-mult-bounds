#!/usr/bin/env python3
"""Exact six-transfer exclusion and credited eight-transfer construction.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable is imported. Guards remain active under python -O.
"""
import argparse
import copy
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import random
import shlex
import subprocess
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT_ROWS = 38


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    return json.loads((PACKAGE / name).read_text())


def rejected(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError("failure control accepted: " + label)


def check_predecessors():
    records = load("PREDECESSORS.json")
    for record in records["retained"]:
        raw = (PACKAGE / record["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == record["sha256"],
                "retained predecessor drift: " + record["path"])
    return len(records["retained"])


def structural_check(receipt, n, transfers):
    require(receipt["sources"] == n and receipt["transfers"] == transfers,
            "wrong census domain")
    expected = math.prod(range(1, 2 * n, 2)) * math.comb(2 * n + transfers, transfers) * 2**n
    require(receipt["candidates"] == expected, "incomplete skeleton census")
    histograms = receipt["histograms"]
    require(len(histograms) == n + 1, "missing source-port partition")
    for row in histograms:
        require(len(row) == 2**n + 1, "wrong coverage dimension")
        require(all(type(count) is int and count >= 0 for count in row), "invalid census multiplicity")
        require(row[0] == 0, "zero mask must be covered")
    require(sum(map(sum, histograms)) == receipt["restored"], "wrong restored count")
    require(0 < receipt["restored"] <= expected, "invalid restored count")


def run_census(binary, n, transfers):
    result = subprocess.run([str(binary), str(n), str(transfers)],
                            check=True, capture_output=True, text=True, timeout=240)
    receipt = json.loads(result.stdout)
    structural_check(receipt, n, transfers)
    return receipt


def python_small_census(n, transfers):
    """Third algorithm: labeled multiset permutations and set-valued expressions.

    Only used for n <= 2. Every canonical record has exactly n! relabelings.
    """
    require(n <= 2, "small oracle is deliberately bounded")
    hist = [[0] * (2**n + 1) for _ in range(n + 1)]
    candidates = restored = 0
    words = set(itertools.permutations(list(range(n)) * 2 + [n] * transfers))
    for word in words:
        for ports in itertools.product((0, 1), repeat=n):
            candidates += 1
            rows = [frozenset(("d0",)), frozenset(("d1",))]
            seen = set(rows)
            for op in word:
                if op == n:
                    rows[0] ^= rows[1]
                else:
                    rows[ports[op]] ^= frozenset((op,))
                seen.update(rows)
            if rows != [frozenset(("d0",)), frozenset(("d1",))]:
                continue
            restored += 1
            masks = {x ^ y for x in seen for y in seen if not ((x ^ y) & {"d0", "d1"})}
            hist[sum(ports)][len(masks)] += 1
    factor = math.factorial(n)
    require(candidates % factor == restored % factor == 0, "relabeling count")
    require(all(x % factor == 0 for row in hist for x in row), "orbit histogram")
    return dict(sources=n, transfers=transfers, candidates=candidates // factor,
                restored=restored // factor,
                histograms=[[x // factor for x in row] for row in hist])


def skeleton_states(skeleton):
    rows = [32, 64]
    states = [tuple(rows)]
    for op in skeleton:
        if op == ["C"]:
            rows[0] ^= rows[1]
        else:
            require(len(op) == 3 and op[0] == "B" and 0 <= op[1] < 5
                    and op[2] in (0, 1), "invalid skeleton instruction")
            rows[op[2]] ^= 1 << op[1]
        states.append(tuple(rows))
    return states


def expand_certificate(certificate):
    skeleton = certificate["skeleton"]
    states = skeleton_states(skeleton)
    require(states[-1] == (32, 64), "connector not restored")
    require(sum(op == ["C"] for op in skeleton) == 8, "not the eight-transfer fixture")
    require(all(sum(op[:2] == ["B", j] for op in skeleton) == 2 for j in range(5)),
            "each source must be called twice")
    at = [[] for _ in states]
    readouts = certificate["readouts"]
    require(sorted(int(m) for m in readouts) == list(range(1, 32)), "missing output mask")
    for name, pair in readouts.items():
        mask = int(name)
        require(len(pair) == 2, "need exactly two readouts")
        observed = 0
        for cut, port in pair:
            require(type(cut) is int and 0 <= cut < len(states) and port in (0, 1),
                    "readout outside skeleton")
            observed ^= states[cut][port]
            at[cut].append(["A", mask, port])
        require(observed == mask, "wrong mask or uncancelled incoming dirt")
    word = []
    for cut in range(len(states)):
        word.extend(sorted(at[cut]))
        if cut < len(skeleton):
            word.append(skeleton[cut])
    require(len(word) == 80, "wrong complete-word length")
    return word


def initial_polynomials():
    return [{(j, ())} for j in range(ROOT_ROWS)]


def apply_formal(operator, polynomial):
    return {(variable, (operator,) + word) for variable, word in polynomial}


def symbolic(word):
    rows = initial_polynomials()
    for op in word:
        if op == ["C"]:
            rows[36] ^= rows[37]
        else:
            kind, index, port = op
            require(port in (0, 1), "invalid port")
            if kind == "B":
                require(0 <= index < 5, "invalid source")
                rows[36 + port] ^= apply_formal(("B", index), rows[index])
            elif kind == "A":
                require(1 <= index <= 31, "invalid output")
                rows[4 + index] ^= apply_formal(("A", index), rows[36 + port])
            else:
                raise ValueError("operation outside interface")
    return rows


def symbolic_target():
    expected = initial_polynomials()
    for mask in range(1, 32):
        for source in range(5):
            if mask & (1 << source):
                expected[4 + mask].add((source, (("A", mask), ("B", source))))
    return expected


def certify_word(word):
    require(symbolic(word) == symbolic_target(), "free noncommutative dirty identity failed")


def matvec(matrix, vector):
    return sum(((row & vector).bit_count() & 1) << i for i, row in enumerate(matrix))


def dense_replay(word):
    columns = noncommuting = 0
    for width in range(1, 5):
        rng = random.Random(20261014 + width)
        matrices = {("B", j): [rng.randrange(2**width) for _ in range(width)] for j in range(5)}
        matrices.update({("A", m): [rng.randrange(2**width) for _ in range(width)] for m in range(1, 32)})
        noncommuting += sum(
            matvec(matrices["A", 1], matvec(matrices["B", j], 1 << bit)) !=
            matvec(matrices["B", j], matvec(matrices["A", 1], 1 << bit))
            for j in range(5) for bit in range(width))
        for column in range(ROOT_ROWS * width):
            initial = [0] * ROOT_ROWS
            initial[column // width] = 1 << (column % width)
            expected = initial.copy()
            for mask in range(1, 32):
                inner = 0
                for j in range(5):
                    if mask & (1 << j):
                        inner ^= matvec(matrices["B", j], initial[j])
                expected[4 + mask] ^= matvec(matrices["A", mask], inner)
            for program in (word, word[::-1]):
                rows = initial.copy()
                for op in program:
                    if op == ["C"]:
                        rows[36] ^= rows[37]
                    elif op[0] == "B":
                        rows[36 + op[2]] ^= matvec(matrices["B", op[1]], rows[op[1]])
                    else:
                        rows[4 + op[1]] ^= matvec(matrices["A", op[1]], rows[36 + op[2]])
                require(rows == expected, "dense noncommuting basis replay failed")
            columns += 1
    require(noncommuting > 0, "dense control accidentally commutative")
    return columns


def transfer_backend():
    """Literal one-head tape realization with one admitted clean scalar bit."""
    columns = 0
    for width in range(1, 6):
        for column in range(ROOT_ROWS * width):
            tape = [0] * (ROOT_ROWS * width)
            tape[column] = 1
            original = tape.copy()
            expected = original.copy()
            for k in range(width):
                expected[36 * width + k] ^= original[37 * width + k]
            for wanted in (expected, original):
                head = temporary = travel = xors = 0
                for k in range(width):
                    source, target = 37 * width + k, 36 * width + k
                    travel += abs(head - source)
                    head = source
                    temporary ^= tape[head]
                    xors += 1
                    travel += abs(head - target)
                    head = target
                    tape[head] ^= temporary
                    xors += 1
                    travel += abs(head - source)
                    head = source
                    temporary ^= tape[head]
                    xors += 1
                    travel += head
                    head = 0
                require(tape == wanted and temporary == head == 0, "transfer backend restoration")
                require(xors == 3 * width and travel == 77 * width**2 - width,
                        "transfer backend unpaid instruction")
            columns += 1
    return columns


def controls(certificate, word, receipt):
    names = []
    # These omissions test the literal word, not optimality of arbitrary words.
    for index in range(len(word)):
        names.append(rejected(lambda i=index: certify_word(word[:i] + word[i+1:]),
                              "omit-instruction-" + str(index)))
    for kind in ("A", "B"):
        altered = copy.deepcopy(word)
        index = next(i for i, op in enumerate(altered) if op[0] == kind)
        altered[index][2] ^= 1
        names.append(rejected(lambda: certify_word(altered), "wrong-" + kind + "-port"))
    altered = copy.deepcopy(word)
    index = next(i for i, op in enumerate(altered) if op[0] == "A")
    altered[index][1] = altered[index][1] % 31 + 1
    names.append(rejected(lambda: certify_word(altered), "wrong-output-destination"))
    damaged = copy.deepcopy(certificate)
    damaged["readouts"].pop("21")
    names.append(rejected(lambda: expand_certificate(damaged), "missing-mask-21"))
    damaged = copy.deepcopy(certificate)
    damaged["readouts"]["21"][0][1] ^= 1
    names.append(rejected(lambda: expand_certificate(damaged), "wrong-dirty-readout-port"))
    damaged_receipt = copy.deepcopy(receipt)
    damaged_receipt["candidates"] //= 2
    names.append(rejected(lambda: structural_check(damaged_receipt, 5, 6), "missing-port-half-census"))
    damaged_receipt = copy.deepcopy(receipt)
    damaged_receipt["histograms"] = damaged_receipt["histograms"][:-1]
    names.append(rejected(lambda: structural_check(damaged_receipt, 5, 6), "missing-port-partition"))
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional deterministic receipt; no files written by default")
    parser.add_argument("--witness-only", action="store_true",
                        help="Python-only upper-bound replay; does NOT check the six-transfer exclusion")
    args = parser.parse_args()
    pins = check_predecessors()
    certificate = load("CERTIFICATE.json")
    word = expand_certificate(certificate)
    certify_word(word)
    certify_word(word[::-1])
    if args.witness_only:
        receipt = dict(
            status="PASS_EIGHT_TRANSFER_WITNESS_ONLY",
            scope="Credited eight-transfer upper bound only; no lower-bound census executed.",
            symbolic_forward_and_inverse=True,
            dense_basis_columns_each_direction=dense_replay(word),
            transfer_tape_columns_each_direction=transfer_backend(),
            failure_controls=controls(certificate, word, load("EXPECTED.json")),
            retained_predecessor_files=pins)
        if args.output:
            args.output.write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt, indent=2))
        return
    with tempfile.TemporaryDirectory(prefix="six-transfer-") as directory:
        binaries = []
        for source in ("census.cpp", "independent.cpp"):
            binary = Path(directory) / source.removesuffix(".cpp")
            compiler = shlex.split(os.environ.get("CXX", "c++"))
            subprocess.run([*compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-pedantic",
                            str(PACKAGE / source), "-o", str(binary)], check=True, timeout=60)
            binaries.append(binary)
        full = [run_census(binary, 5, 6) for binary in binaries]
        require(full[0] == full[1], "separate full censuses disagree")
        require(full[0] == load("EXPECTED.json"), "frozen census receipt mismatch")
        require(all(row[32] == 0 for row in full[0]["histograms"]), "six-transfer witness exists")
        small_cases = []
        for n in range(1, 4):
            for transfers in (0, 2, 4, 6):
                receipts = [run_census(binary, n, transfers) for binary in binaries]
                require(receipts[0] == receipts[1], "small censuses disagree")
                if n <= 2:
                    require(receipts[0] == python_small_census(n, transfers), "set-valued Python oracle disagrees")
                small_cases.append([n, transfers])
        positive = run_census(binaries[0], 2, 4)
        require(sum(row[4] for row in positive["histograms"]) > 0, "small positive control absent")
        old = [run_census(binary, 5, 0) for binary in binaries]
        require(old[0] == old[1], "old-boundary census disagreement")
        known = {16: 42, 19: 120, 21: 180, 22: 56, 23: 45, 24: 220, 26: 110, 28: 150, 31: 22}
        require({i: x for i, x in enumerate(old[0]["histograms"][0]) if x} == known,
                "Ross Richardson's 945-pairing positive control failed")
    dense_columns = dense_replay(word)
    tape_columns = transfer_backend()
    failure_controls = controls(certificate, word, full[0])
    receipt = dict(
        status="PASS_TWO_CONNECTOR_SHARP_EIGHT_TRANSFERS",
        scope="Five sources, all 31 nonzero output masks, exactly two calls per A/B operator, one-way C only.",
        candidates=full[0]["candidates"], restored=full[0]["restored"],
        maximum_coverage_by_source_port_count=[max(i for i, x in enumerate(row) if x) for row in full[0]["histograms"]],
        full_census_implementations=2, small_census_cases=small_cases,
        independent_python_small_cases=8, historical_pairings=945,
        witness=dict(source_calls=10, output_calls=62, transfers=8,
                     total=80, output_masks=31, root_rows=38, borrowed_dirty_connectors=2),
        symbolic_forward_and_inverse=True, dense_basis_columns_each_direction=dense_columns,
        transfer_tape_columns_each_direction=tape_columns,
        failure_controls=failure_controls, retained_predecessor_files=pins,
        file_sha256={name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                     for name in ("census.cpp", "independent.cpp", "verify.py",
                                  "CERTIFICATE.json", "EXPECTED.json", "PREDECESSORS.json")},
        no_new_kappa=True)
    if args.output:
        args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
