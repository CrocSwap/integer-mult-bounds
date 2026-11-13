"""Certify distances with normal forms, independently of the primary checker."""

import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
import sys


GATES = ("C01", "C10", "X0", "X1", "S0", "S1", "CZ", "omega")
IDENTITY = (1, 2, 0, 0, 0, 0, 0)
LITERAL_GATES = (
    ((0, 3, 2, 1), (0, 0, 0, 0)),
    ((0, 1, 3, 2), (0, 0, 0, 0)),
    ((1, 0, 3, 2), (0, 0, 0, 0)),
    ((2, 3, 0, 1), (0, 0, 0, 0)),
    ((0, 1, 2, 3), (0, 1, 0, 1)),
    ((0, 1, 2, 3), (0, 0, 1, 1)),
    ((0, 1, 2, 3), (0, 0, 0, 2)),
    ((0, 1, 2, 3), (1, 1, 1, 1)),
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def action(form):
    r0, r1, b, a, c0, c1, q = form
    permutation, phases = [], []
    for x in range(4):
        y0 = ((r0 & x).bit_count() & 1) ^ (b & 1)
        y1 = ((r1 & x).bit_count() & 1) ^ (b >> 1)
        permutation.append(y0 + 2 * y1)
        phases.append((a + c0 * (x & 1) + c1 * (x >> 1)
                       + 2 * q * (x & 1) * (x >> 1)) % 4)
    return tuple(permutation), tuple(phases)


def key(form):
    permutation, phases = action(form)
    return "".join(map(str, permutation + phases))


def polynomial_step(form, gate):
    r0, r1, b, a, c0, c1, q = form
    b0, b1 = b & 1, b >> 1
    u0, v0, u1, v1 = r0 & 1, r0 >> 1, r1 & 1, r1 >> 1
    if gate == "C01":
        r1 ^= r0
        b ^= b0 << 1
    elif gate == "C10":
        r0 ^= r1
        b ^= b1
    elif gate in ("X0", "X1"):
        b ^= 1 if gate == "X0" else 2
    elif gate in ("S0", "S1"):
        row, bit = (r0, b0) if gate == "S0" else (r1, b1)
        u, v = row & 1, row >> 1
        a += bit
        c0 += (1 - 2 * bit) * u
        c1 += (1 - 2 * bit) * v
        q ^= u * v
    elif gate == "CZ":
        a += 2 * b0 * b1
        c0 += 2 * (b0 * u1 + b1 * u0 + u0 * u1)
        c1 += 2 * (b0 * v1 + b1 * v0 + v0 * v1)
        q ^= (u0 * v1 + v0 * u1) & 1
    elif gate == "omega":
        a += 1
    else:
        raise ValueError("unknown polynomial gate")
    return r0, r1, b, a % 4, c0 % 4, c1 % 4, q


def forms():
    result = []
    for r0, r1 in product(range(1, 4), repeat=2):
        if r0 != r1:
            for b, a, c0, c1, q in product(range(4), range(4), range(4), range(4), range(2)):
                result.append((r0, r1, b, a, c0, c1, q))
    need(len(result) == 3072, "normal-form count")
    return result


def unique_object(pairs):
    need(len(pairs) <= 8, "too many object keys")
    result = dict(pairs)
    need(len(result) == len(pairs), "duplicate JSON key")
    return result


def load_labels(path):
    need(path.is_file() and not path.is_symlink(), "regular certificate required")
    need(path.stat().st_size <= 1_000_000, "certificate too large")
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    need(set(data) == {"schema", "gates", "distances"}, "certificate fields")
    need(data["schema"] == "two-axis-monomial-distances/1", "certificate schema")
    need(data["gates"] == list(GATES), "directed gate alphabet")
    rows = data["distances"]
    need(isinstance(rows, list) and len(rows) == 3072, "certificate row count")
    for row in rows:
        need(isinstance(row, list) and len(row) == 2, "certificate row shape")
        need(isinstance(row[0], str) and len(row[0]) == 8, "action code shape")
        need(type(row[1]) is int and 0 <= row[1] <= 8, "distance label range")
    result = dict(rows)
    need(len(result) == 3072 and rows == sorted(rows), "unique sorted action codes")
    return result


def generate_labels(universe):
    by_key = {key(form): form for form in universe}
    labels = {key(IDENTITY): 0}
    layer = {key(IDENTITY)}
    for depth in range(1, 9):
        following_layer = set()
        for old_key in layer:
            form = by_key[old_key]
            for gate in GATES:
                new_key = key(polynomial_step(form, gate))
                if new_key not in labels:
                    labels[new_key] = depth
                    following_layer.add(new_key)
        layer = following_layer
    need(len(labels) == 3072, "eight layers cover the group")
    return labels


def check_labels(labels, universe):
    keys = {key(form) for form in universe}
    need(len(keys) == 3072 and set(labels) == keys, "complete action inventory")
    need(labels[key(IDENTITY)] == 0, "identity label")
    need(sum(value == 0 for value in labels.values()) == 1, "unique zero label")
    predecessor = {key(IDENTITY)}
    comparisons = 0
    for form in universe:
        p, phase = action(form)
        before = labels[key(form)]
        for index, gate in enumerate(GATES):
            following = polynomial_step(form, gate)
            gp, gphase = LITERAL_GATES[index]
            literal = (tuple(gp[y] for y in p),
                       tuple((phase[x] + gphase[p[x]]) % 4 for x in range(4)))
            need(action(following) == literal, "polynomial/literal transition")
            after_key = key(following)
            after = labels[after_key]
            need(after <= before + 1, "edge distance inequality")
            if after == before + 1:
                predecessor.add(after_key)
            comparisons += 1
    need(predecessor == keys, "distance-decreasing predecessor")
    return comparisons


def word_endpoint(word):
    form = IDENTITY
    need(len(word) <= 8, "word length")
    for gate in word:
        form = polynomial_step(form, gate)
    return key(form)


def rejection_controls(labels, universe):
    altered = dict(labels)
    altered["31023223"] = 5
    tests = [(altered, "edge distance inequality"),
             ({**labels, key(IDENTITY): 1}, "identity label"),
             ({k: v for k, v in labels.items() if k != "31023223"}, "complete action inventory")]
    for candidate, reason in tests:
        try:
            check_labels(candidate, universe)
        except ValueError as error:
            need(str(error) == reason, "wrong certificate rejection")
        else:
            raise ValueError("invalid certificate accepted")
    try:
        polynomial_step(IDENTITY, "S0_inverse")
    except ValueError as error:
        need(str(error) == "unknown polynomial gate", "wrong gate rejection")
    else:
        raise ValueError("inverse record admitted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path)
    args = parser.parse_args()
    universe = forms()
    labels = generate_labels(universe) if args.certificate is None else load_labels(args.certificate)
    transitions = check_labels(labels, universe)
    need(labels["31023223"] == 6 and labels["02133322"] == 8, "sharp labels")
    need(word_endpoint(("C01", "X1", "C10", "S1", "omega", "omega")) == "31023223",
         "six-record witness")
    need(word_endpoint(("C01", "C10", "C01", "X0", "S0", "X0", "omega", "omega")) == "02133322",
         "eight-record witness")
    rejection_controls(labels, universe)
    root = Path(__file__).resolve().parent
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "verify.py", "independent_check.py")
    hashes = {}
    for name in files:
        path = root / name
        need(path.is_file() and not path.is_symlink(), "regular package file")
        need(path.stat().st_size <= 1_000_000, "package file too large")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    payload = {"schema": "two-axis-monomial-distances/1", "gates": list(GATES),
               "distances": sorted([[name, value] for name, value in labels.items()])}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(json.dumps({"result": "PASS_TWO_AXIS_MONOMIAL_POTENTIAL", "states": len(labels),
                      "transitions": transitions, "histogram": sorted(Counter(labels.values()).items()),
                      "diameter": max(labels.values()), "certificate_controls": 3,
                      "domain_controls": 1, "python": sys.version.split()[0],
                      "distance_certificate_sha256": digest,
                      "files_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
