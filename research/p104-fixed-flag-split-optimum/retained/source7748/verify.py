#!/usr/bin/env python3
"""Replay the fixed-flag single-gather minimum and the signed split witness."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from struct import pack


PORTS = range(104)
LINES = range(120)
CHAINS = range(8)
PORT_GRAM_SHA256 = "98339059a79361ca365325f872860f6ab5b3de87bf998c2957ecf240577f2c4a"
PORT_LABEL_SHA256 = "d7fc071c93a88a7746f545ba215da98c8be2de16ded9e3f884e48134a3d24fa6"
NPY_HEADER = b"{'descr': '<i8', 'fortran_order': False, 'shape': (104, 104), }"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return (a & b).bit_count() % 2


def inverse(matrix):
    rows = [
        list(map(Fraction, row)) + [Fraction(i == j) for j in CHAINS]
        for i, row in enumerate(matrix)
    ]
    for j in CHAINS:
        pivot = next((i for i in range(j, 8) if rows[i][j]), None)
        require(pivot is not None, "singular Gram basis")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        rows[j] = [entry / rows[j][j] for entry in rows[j]]
        for i in CHAINS:
            if i != j:
                factor = rows[i][j]
                rows[i] = [a - factor * b for a, b in zip(rows[i], rows[j], strict=True)]
    return [row[8:] for row in rows]


def reconstruct_gram(data):
    profiles = data["gram_profiles"]
    basis = data["basis_rows"]
    labels = data["labels"]
    require(len(profiles) == len(labels) == 120, "line count")
    require(len(basis) == len(set(basis)) == 8 and all(i in PORTS for i in basis),
            "basis must name eight distinct ports")
    require(all(len(row) == 8 and all(type(x) is int and abs(x) <= 2 for x in row)
                for row in profiles), "Gram profiles")
    require(len(set(labels)) == 120 and all(type(v) is int and 0 < v < 512 for v in labels),
            "line labels")
    dual = inverse([profiles[i] for i in basis])
    coordinates = [
        [sum(a * b for a, b in zip(row, column, strict=True)) for row in dual]
        for column in profiles
    ]
    gram = []
    for a in LINES:
        row = [sum(x * y for x, y in zip(coordinates[a], col, strict=True))
               for col in profiles]
        require(all(value.denominator == 1 for value in row), "nonintegral Gram entry")
        gram.append([int(value) for value in row])
    for a, b in product(LINES, repeat=2):
        entry = gram[a][b]
        require(entry == gram[b][a], "asymmetric Gram matrix")
        require(entry == 2 if a == b else abs(entry) <= 1, "invalid line inner product")
        require(dot(labels[a], labels[b]) == (entry + 1) % 2, "line label parity")
    payload = pack("<10816q", *(gram[a][b] for a, b in product(PORTS, repeat=2)))
    header = b"\x93NUMPY\x01\x00v\x00" + NPY_HEADER.ljust(117) + b"\n"
    require(sha256(header + payload).hexdigest() == PORT_GRAM_SHA256, "pinned port Gram")
    require(sha256(json.dumps(labels[:104]).encode()).hexdigest() == PORT_LABEL_SHA256,
            "pinned port labels")
    return gram


def flag_levels(labels, source, destination, basis):
    require(len(basis) == 8 and basis[0] == labels[destination], "flag entrance")
    span = {0}
    birth = {}
    for level, direction in enumerate(basis):
        require(type(direction) is int and 0 < direction < 512, "flag direction")
        require(direction not in span and not dot(direction, labels[source]), "flag step")
        new_vectors = {v ^ direction for v in span}
        birth.update(dict.fromkeys(new_vectors, level))
        span |= new_vectors
    arrivals = [birth.get(v, 8) for v in labels[:104]]
    deadlines = [
        next((i - 1 for i, direction in enumerate(basis) if dot(v, direction)), 7)
        for v in labels[:104]
    ]
    return arrivals, deadlines


def model(data, gram):
    pairs = data["chains"]
    flags = data["flag_bases"]
    labels = data["labels"]
    require(len(pairs) == len(flags) == 8, "eight chains")
    require(sorted(v for pair in pairs for v in pair) == list(range(104, 120)),
            "one use of each virtual line")
    arrivals, deadlines, weights = [], [], []
    for (z, zp), flag in zip(pairs, flags, strict=True):
        pairing = gram[z][zp]
        require(abs(pairing) == 1, "virtual pairing")
        tau, sigma = flag_levels(labels, z, zp, flag)
        arrivals.append(tau)
        deadlines.append(sigma)
        weights.append([[gram[t][z] * gram[s][zp] // pairing for t in PORTS] for s in PORTS])
    return arrivals, deadlines, weights


def run_column(source, schedule, arrivals, deadlines, weights):
    active = {k for k in CHAINS if any(weights[k][source])}
    require(set(schedule) == active, "gathers must cover exactly the active chains")
    coefficients = {}
    for k, pieces in schedule.items():
        require(1 <= len(pieces) <= 8, "gather piece count")
        require(sum(amount for _, amount in pieces) == 1, "gather coefficients must sum to one")
        require(all(0 <= level <= deadlines[k][source] for level, _ in pieces),
                "gather after cutoff")
        coefficients[k] = [
            sum(amount for level, amount in pieces if level < arrival)
            for arrival in range(9)
        ]
    return [
        sum(weights[k][source][t] * coefficients[k][arrivals[k][t]] for k in active)
        for t in PORTS
    ]


def check_required_entries(source, column, labels):
    require(column[source] == 2, "wrong diagonal")
    odd = [t for t in PORTS if t != source and dot(labels[t], labels[source])]
    require(all(column[t] == 0 for t in odd), "nonzero odd off-diagonal")
    return len(odd)


def junk(source, column, labels):
    return sum(bool(column[t]) for t in PORTS if t != source and not dot(labels[t], labels[source]))


def rejection_control(source, schedule, model_data, replacement, reason):
    modified = {**schedule, 3: replacement}
    try:
        run_column(source, modified, *model_data)
    except ValueError as error:
        require(str(error) == reason, "wrong rejection reason")
    else:
        raise ValueError("invalid gather passed")


def verify(data):
    labels = data["labels"]
    gram = reconstruct_gram(data)
    model_data = model(data, gram)
    _, deadlines, weights = model_data
    source = data["source_column"]
    require(source == 4, "source column")
    active = [k for k in CHAINS if any(weights[k][source])]
    limits = [deadlines[k][source] for k in active]
    require(active == [0, 2, 3, 5, 6] and limits == [0, 0, 4, 0, 1], "gather domain")

    counts = Counter()
    for levels in product(*(range(limit + 1) for limit in limits)):
        single = {k: [(level, 1)] for k, level in zip(active, levels, strict=True)}
        column = run_column(source, single, *model_data)
        check_required_entries(source, column, labels)
        counts[junk(source, column, labels)] += 1
    require(counts == {45: 2, 47: 2, 48: 6}, "single-gather histogram")

    split = dict(data["split_schedule"])
    require(split == {0: [[0, 1]], 2: [[0, 1]], 3: [[0, 2], [4, -1]],
                      5: [[0, 1]], 6: [[0, 1]]}, "signed split schedule")
    column = run_column(source, split, *model_data)
    require(junk(source, column, labels) == 44, "split junk count")
    comparison = {**split, 3: [(4, 1)]}
    baseline = run_column(source, comparison, *model_data)
    require(junk(source, baseline, labels) == 45, "comparison schedule minimum")
    removed = [t for t in PORTS if baseline[t] and not column[t]]
    added = [t for t in PORTS if column[t] and not baseline[t]]
    changed = [t for t in PORTS if column[t] != baseline[t]]
    require(removed == [0, 1, 50, 56] and added == [35, 86, 90]
            and changed == sorted(removed + added), "column delta")

    # Embed the split in a full schedule and check its required entries.
    odd_count = 0
    for s in PORTS:
        schedule = split if s == source else {k: [(0, 1)] for k in CHAINS if any(weights[k][s])}
        odd_count += check_required_entries(s, run_column(s, schedule, *model_data), labels)

    rejection_control(source, split, model_data, [(0, 2), (4, 1)],
                      "gather coefficients must sum to one")
    rejection_control(source, split, model_data, [(0, 2), (5, -1)], "gather after cutoff")
    print("PASS_P104_C56_SPLIT_GATHER_WITNESS")
    print(f"Single-gather junk counts: {sorted(counts.items())}. Signed split: 44.")
    print(f"Full schedule: 104 diagonals and {odd_count} odd off-diagonal zeros.")


if __name__ == "__main__":
    fixture = Path(__file__).with_name("WITNESS.json")
    verify(json.loads(fixture.read_text(encoding="utf-8")))
