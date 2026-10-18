#!/usr/bin/env python3
"""Exact finite evidence for rational prescribed-triangle recovery. Apache-2.0."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGETS = ((0, 2), (0, 4), (2, 4))
# Twice the three decoder coefficients at each target vertex.
ROOT_ROWS = ((1, 1, -1), (1, -1, 1), (-1, 1, 1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def edges(p):
    return [(u, v) for u, v in combinations(range(2 * p), 2) if u // 2 != v // 2]


def allowed(a, b):
    return a == b == 6 or (a < 6 and b < 6 and a ^ b == 1)


def retained(p, classes):
    return [e for e in edges(p) if e in TARGETS or allowed(*(classes[v] for v in e))]


def census(p):
    """Every seven-class assignment; counting does not use the endpoint formula."""
    free = [v for v in range(2 * p) if v not in (0, 2, 4)]
    histogram = Counter()
    maximum, witness = -1, None
    for assignment in product(range(7), repeat=len(free)):
        classes = [0] * (2 * p)
        classes[2], classes[4] = 2, 4
        for v, label in zip(free, assignment):
            classes[v] = label
        counts = [classes.count(label) for label in range(7)]
        count = 3 + counts[6] * (counts[6] - 1) // 2
        count += sum(counts[k] * counts[k + 1] for k in (0, 2, 4))
        count -= sum(allowed(classes[v], classes[v + 1]) for v in range(0, 2 * p, 2))
        histogram[count] += 1
        if count > maximum:
            maximum, witness = count, classes
    require(len(retained(p, witness)) == maximum, "census witness edge count")
    return {
        "p": p,
        "assignments": sum(histogram.values()),
        "maximum_retained_edges": maximum,
        "minimum_deletions": len(edges(p)) - maximum,
        "maximizing_assignments": histogram[maximum],
        "witness_classes": witness,
        "retained_edge_histogram": {str(k): histogram[k] for k in sorted(histogram)},
    }


def rational_rank(rows):
    a = [[Fraction(x) for x in row] for row in rows]
    rank = 0
    for col in range(len(a[0])):
        pivot = next((r for r in range(rank, len(a)) if a[r][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        value = a[rank][col]
        a[rank] = [x / value for x in a[rank]]
        for r in range(rank + 1, len(a)):
            value = a[r][col]
            if value:
                a[r] = [x - value * y for x, y in zip(a[r], a[rank])]
        rank += 1
    return rank


def binary_rank(rows):
    pivots = {}
    for row in rows:
        word = sum((int(value) & 1) << j for j, value in enumerate(row))
        while word:
            pivot = word.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = word
                break
            word ^= pivots[pivot]
    return len(pivots)


def recoverable(p, kept, rank=rational_rank):
    observations = [[int(v in e) for e in kept] for v in range(2 * p)]
    wanted = [[int(e == target) for e in kept] for target in TARGETS]
    return rank(observations) == rank(observations + wanted)


def independent_p3():
    """All retained graphs, using rational row spaces, without class reduction."""
    optional = [e for e in edges(3) if e not in TARGETS]
    counts = Counter()
    binary_successes = 0
    omitted_observation_controls = 0
    for mask in range(1 << len(optional)):
        kept = list(TARGETS) + [e for j, e in enumerate(optional) if mask >> j & 1]
        if recoverable(3, kept):
            counts[len(kept)] += 1
            if len(kept) == 7:
                observations = [[int(v in e) for e in kept] for v in range(6)]
                wanted = [[int(e == target) for e in kept] for target in TARGETS]
                require(rational_rank(observations) == 6, "optimum observation rank")
                for v in range(6):
                    partial = observations[:v] + observations[v + 1:]
                    require(rational_rank(partial + wanted) > rational_rank(partial),
                            "omitted raw vertex observation accepted")
                    omitted_observation_controls += 1
        binary_successes += recoverable(3, kept, binary_rank)
    require(max(counts) == 7, "independent p=3 optimum")
    require(binary_successes == 0, "characteristic-two triangle ambiguity")
    return {"retained_graphs": 512, "recoverable_by_edges": dict(sorted(counts.items())),
            "binary_recoverable_graphs": binary_successes,
            "omitted_observation_controls": omitted_observation_controls}


def word(p, classes):
    kept = retained(p, classes)
    active = [v for v, label in enumerate(classes) if label < 6]
    size = len(kept) + 3 + len(active)
    helper = {v: len(kept) + 3 + j for j, v in enumerate(active)}
    gather = [("ADD", helper[v], j, Fraction(1))
              for j, e in enumerate(kept) for v in e if v in helper]
    program = []
    for sign in (1, -1):
        program.extend((op, dst, src, sign * c) for op, dst, src, c in gather)
        program.extend(("SCALE", h, h, Fraction(1, 2)) for h in helper.values())
        for target in range(3):
            for v, h in helper.items():
                label = classes[v]
                coefficient = sign * (-1 if label % 2 else 1) * ROOT_ROWS[label // 2][target]
                program.append(("ADD", len(kept) + target, h, Fraction(coefficient)))
        program.extend(("SCALE", h, h, Fraction(2)) for h in helper.values())
    return kept, size, program


def check_word(p, classes, program=None):
    kept, size, original = word(p, classes)
    if program is None:
        program = original
    for column in range(size):
        state = [Fraction(int(j == column)) for j in range(size)]
        expected = state[:]
        if column < len(kept) and kept[column] in TARGETS:
            expected[len(kept) + TARGETS.index(kept[column])] += 1
        for op, dst, src, coefficient in program:
            if op == "ADD":
                state[dst] += coefficient * state[src]
            else:
                require(op == "SCALE", "unknown scalar instruction")
                state[dst] *= coefficient
        require(state == expected, f"dirty echo identity p={p} column={column}")
    active = [v for v, label in enumerate(classes) if label < 6]
    observation_rank = rational_rank([[int(v in e) for e in kept] for v in active])
    return {"p": p, "basis_columns": size, "dirty_helpers": len(active),
            "observation_rank": observation_rank,
            "source_adds": sum(op == "ADD" and src < len(kept) for op, _, src, _ in program),
            "output_adds": sum(op == "ADD" and src >= len(kept) for op, _, src, _ in program),
            "scales": sum(op == "SCALE" for op, _, _, _ in program), "total": len(program)}


def rejected(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError("negative control accepted")


def compute():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for item in pins["sources"]:
        data = (ROOT / item["path"]).read_bytes()
        require(sha256(data).hexdigest() == item["sha256"],
                "source pin: " + item["path"])
        require(sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == item["blob"],
                "source blob: " + item["path"])
    rows = [census(p) for p in (3, 4, 5)]
    require([row["minimum_deletions"] for row in rows] == [5, 12, 18], "finite minima")
    invoices, restored_edge_controls, instruction_controls = [], 0, 0
    for p in (3, 4, 5):
        classes = [0, 0, 2, 1, 4, 1] if p == 3 else [6] * (2 * p)
        for v, label in zip((0, 2, 4), (0, 2, 4)):
            classes[v] = label
        kept, _, program = word(p, classes)
        require(recoverable(p, kept), "rational positive fixture")
        for edge in edges(p):
            if edge not in kept:
                require(not recoverable(p, kept + [edge]), "restored deleted edge accepted")
                restored_edge_controls += 1
        invoices.append(check_word(p, classes))
        # Each omitted source read, output update or scale must be detected.
        for index in range(len(program)):
            rejected(lambda i=index: check_word(p, classes, program[:i] + program[i + 1:]))
            instruction_controls += 1
    require([item["total"] for item in invoices] == [88, 42, 42], "complete scalar invoice")
    require([item["observation_rank"] for item in invoices] == [6, 3, 3], "observation ranks")
    return {"assignment_seed": 48, "census": rows, "independent_p3": independent_p3(),
            "dirty_echo": invoices, "restored_edge_controls": restored_edge_controls,
            "instruction_omission_controls": instruction_controls,
            "source_pins": len(pins["sources"]), "claim": "scoped_information_theorem_no_new_kappa"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the recomputed exact receipt")
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    result = compute()
    # JSON round-trip normalizes integer histogram keys for exact receipt comparison.
    result = json.loads(json.dumps(result))
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads(args.certificate.read_text())
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                "certificate mismatch")
        print("PASS_RATIONAL_TRIANGLE_S48 assignments=840693 graphs=512 "
              "deletions=5,12,18 restored_edges=35 omissions=172 no_new_kappa")


if __name__ == "__main__":
    main()
