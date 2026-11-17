#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite premises of the two-coordinate A7+A1 code reduction."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_bounded(path, limit):
    with path.open("rb") as handle:
        data = handle.read(limit + 1)
    need(len(data) <= limit, "bounded package file")
    return data


def canonical(row):
    first = next(value for value in row if value)
    return tuple(row) if first > 0 else tuple(-value for value in row)


def root_lines():
    values = set()
    for i, j in itertools.combinations(range(8), 2):
        for a, b in itertools.product((-2, 2), repeat=2):
            row = [0] * 8
            row[i], row[j] = a, b
            values.add(canonical(row))
    for row in itertools.product((-1, 1), repeat=8):
        if sum(value < 0 for value in row) % 2 == 0:
            values.add(canonical(row))
    result = tuple(sorted(values, reverse=True))
    need(len(result) == 120, "120 unoriented root lines")
    return result


def dot(left, right):
    return sum(a * b for a, b in zip(left, right, strict=True))


def adjacent(left, right):
    return left != right and dot(left, right) == 0


def reader(row, term):
    return sum(row) != 0 if term == 8 else 8 * row[term] != sum(row)


def common_set(roots):
    return {i for i, row in enumerate(roots)
            if row[0] != row[1] and reader(row, 0) and reader(row, 1)}


def fixed_set(roots, term):
    if term == 8:
        return {i for i, row in enumerate(roots) if reader(row, term)}
    return {i for i, row in enumerate(roots)
            if reader(row, term) and row[term] not in (row[0], row[1])}


def check_petersen(roots, allowed, witness):
    need(set(witness) == {"petersen", "isolated"}, "certificate keys")
    petersen, isolated = witness["petersen"], witness["isolated"]
    vertices = petersen + isolated
    need(len(petersen) == 10 and len(isolated) == 4, "Petersen plus four")
    need(all(type(i) is int and 0 <= i < 120 for i in vertices), "indices")
    need(len(set(vertices)) == 14 and set(vertices) <= allowed, "support")
    pairs = tuple(itertools.combinations(range(5), 2))
    for i, j in itertools.combinations(range(10), 2):
        disjoint = not set(pairs[i]).intersection(pairs[j])
        need(adjacent(roots[petersen[i]], roots[petersen[j]]) == disjoint,
             "induced Petersen edge")
    for i in isolated:
        for j in vertices:
            need(i == j or not adjacent(roots[i], roots[j]), "isolated line")
    return 9


def check_independent(roots, allowed, vertices):
    need(len(set(vertices)) == len(vertices) and set(vertices) <= allowed,
         "independent support")
    need(all(not adjacent(roots[i], roots[j])
             for i, j in itertools.combinations(vertices, 2)), "independent edges")


def graph44(roots, common):
    """Construct H44 without using the root graph's adjacency computation."""
    index = {row: i for i, row in enumerate(roots)}
    labels = [(kind, j) for kind in ("A", "B") for j in range(6)]
    labels += [("S", bits) for bits in range(64) if bits.bit_count() % 2]
    vertices = []
    for kind, value in labels:
        if kind == "S":
            row = (1, -1) + tuple(-1 if value >> j & 1 else 1 for j in range(6))
        else:
            entries = [0] * 8
            entries[0 if kind == "A" else 1] = 2
            entries[value + 2] = 2
            row = tuple(entries)
        vertices.append(index[row])
    isolated = index[(2, -2, 0, 0, 0, 0, 0, 0)]
    need(len(vertices) == len(set(vertices)) == 44, "44 graph vertices")
    need(set(vertices) | {isolated} == common, "common graph decomposition")
    need(all(not adjacent(roots[isolated], roots[i]) for i in vertices), "isolate")
    edges = 0
    for i, j in itertools.combinations(range(44), 2):
        kind, value = labels[i]
        other, target = labels[j]
        if kind == other == "S":
            edge = (value ^ target).bit_count() == 4
        elif other == "S":
            edge = bool(target >> value & 1) == (kind == "A")
        else:
            edge = kind != other and value != target
        need(adjacent(roots[vertices[i]], roots[vertices[j]]) == edge,
             "combinatorial H44 edge")
        edges += edge
    return tuple(vertices), isolated, edges


def binary_basis(rows, width):
    need(0 <= width <= 120, "binary width")
    pivots = {}
    for original in rows:
        need(type(original) is int and 0 <= original < 1 << width, "binary row")
        value = original
        for column in range(width - 1, -1, -1):
            if value >> column & 1:
                if column in pivots:
                    value ^= pivots[column]
                else:
                    pivots[column] = value
                    break
    return tuple(pivots[column] for column in sorted(pivots, reverse=True))


def coefficients(row, basis, width):
    remaining, result = row, 0
    for i, value in enumerate(basis):
        column = value.bit_length() - 1
        if remaining >> column & 1:
            remaining ^= value
            result |= 1 << i
    need(remaining == 0 and result < 1 << width, "row in encoder span")
    return result


def xor_selected(mask, values):
    need(len(values) <= 120 and 0 <= mask < 1 << len(values), "XOR domain")
    result = 0
    for i, value in enumerate(values):
        if mask >> i & 1:
            result ^= value
    return result


def fitting_code(roots, vertices, expected_rank):
    """Check the actual encoder and every source basis column of its decoder."""
    rows = tuple(sum((i == j or adjacent(roots[i], roots[j])) << k
                     for k, j in enumerate(vertices)) for i in vertices)
    basis = binary_basis(rows, len(vertices))
    need(len(basis) == expected_rank, "new fitting-code rank")
    decode = tuple(coefficients(row, basis, len(vertices)) for row in rows)
    fixtures = [tuple(int(i == j) for i in range(len(vertices)))
                for j in range(len(vertices))]
    fixtures += [tuple((i * 29 + seed) & 127 for i in range(len(vertices)))
                 for seed in range(3)]
    checked = 0
    for payload in fixtures:
        message = tuple(xor_selected(row, payload) for row in basis)
        for i, row in enumerate(rows):
            known = xor_selected(row ^ (1 << i), payload)
            need(xor_selected(decode[i], message) ^ known == payload[i],
                 "literal side-information recovery")
            checked += 1
    return checked


def shifts_for_reduction(roots):
    shifts = []
    for row in roots:
        if row[0] == row[1] or not reader(row, 1):
            shifts.append(-row[0])
        else:
            shifts.append(-row[1])
    return tuple(shifts)


def validate_shifts(roots, shifts):
    need(len(shifts) == 120, "shift length")
    need(all(value in (-row[0], -row[1])
             for row, value in zip(roots, shifts, strict=True)), "two-coordinate family")


def demands(roots, shifts, term):
    if term == 8:
        return fixed_set(roots, 8)
    return {i for i, row in enumerate(roots)
            if reader(row, term) and row[term] + shifts[i] != 0}


def local_contracts(roots, common):
    checked = 0
    for i, row in enumerate(roots):
        for shift in (-row[0], -row[1]):
            hits = [reader(row, k) and row[k] + shift != 0 for k in (0, 1)]
            need(i not in common or sum(hits) == 1, "partition of common demands")
            for k in range(2, 8):
                if i in fixed_set(roots, k):
                    need(row[k] + shift != 0, "protected core for both choices")
                checked += 1
    shifts = shifts_for_reduction(roots)
    validate_shifts(roots, shifts)
    need(demands(roots, shifts, 0) == common, "attaining common graph")
    need(not demands(roots, shifts, 1), "empty other demand graph")
    return shifts, checked


def pair_transport(roots, certificate):
    index = {row: i for i, row in enumerate(roots)}
    checked = 0
    for a, b in itertools.combinations(range(8), 2):
        destinations = [a, b] + [k for k in range(8) if k not in (a, b)]
        mapping = []
        for row in roots:
            moved = [0] * 8
            for source, target in enumerate(destinations):
                moved[target] = row[source]
            mapping.append(index[canonical(moved)])
        need(len(set(mapping)) == 120, "coordinate permutation bijection")
        for k in list(range(2, 8)) + [8]:
            term = destinations[k] if k < 8 else 8
            allowed = {i for i, row in enumerate(roots) if reader(row, term)
                       and (term == 8 or row[term] not in (row[a], row[b]))}
            moved = {key: [mapping[i] for i in values]
                     for key, values in certificate["protected"][str(k)].items()}
            check_petersen(roots, allowed, moved)
            checked += 1
    return checked


def rejection_controls(roots, common, certificate):
    actions = []
    base = certificate["protected"]["2"]
    duplicate = {"petersen": [base["petersen"][0]] * 10,
                 "isolated": base["isolated"]}
    short = {"petersen": base["petersen"], "isolated": base["isolated"][:3]}
    switched = {"petersen": list(reversed(base["petersen"])),
                "isolated": base["isolated"]}
    for item in (duplicate, short, switched):
        actions.append(("petersen", item))
    actions += [("support", base), ("independent", sorted(common)[:8]),
                ("shift", shifts_for_reduction(roots)[:-1]),
                ("shift", (99,) + shifts_for_reduction(roots)[1:]),
                ("binary", (-1,)), ("binary", (1 << 121,))]
    rejected = 0
    for kind, value in actions:
        try:
            if kind == "petersen":
                check_petersen(roots, fixed_set(roots, 2), value)
            elif kind == "support":
                check_petersen(roots, set(), value)
            elif kind == "independent":
                check_independent(roots, common, value)
            elif kind == "shift":
                validate_shifts(roots, value)
            else:
                binary_basis(value, 120)
        except ValueError:
            rejected += 1
    need(rejected == len(actions), "every control rejects")
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print only the generated receipt")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    raw = read_bounded(here / "CERTIFICATE.json", 16384)
    certificate = json.loads(raw)
    need(certificate["schema_version"] == 1, "certificate schema")
    need(set(certificate["protected"]) == {str(k) for k in range(2, 9)},
         "complete protected certificates")
    roots = root_lines()
    common = common_set(roots)
    need(len(common) == 45, "45 common demands")
    for term in list(range(2, 8)) + [8]:
        allowed = fixed_set(roots, term)
        need(len(allowed) == (57 if term == 8 else 29), "protected core size")
        check_petersen(roots, allowed, certificate["protected"][str(term)])
    independent = certificate["common_independent"]
    need(len(independent) == 8, "eight common independent lines")
    check_independent(roots, common, independent)
    vertices, isolated, edges = graph44(roots, common)
    need(isolated in independent, "seven independent H44 lines after deletion")
    columns = fitting_code(roots, vertices, 8)
    shifts, row_checks = local_contracts(roots, common)
    for term in list(range(2, 8)) + [8]:
        columns += fitting_code(roots, tuple(sorted(demands(roots, shifts, term))), 9)
    transported = pair_transport(roots, certificate)
    controls = rejection_controls(roots, common, certificate)
    receipt = {"status": "PASS_A7_TWO_COORDINATE_CODE_REDUCTION", "roots": len(roots),
               "common_vertices": len(common), "reduced_vertices": len(vertices),
               "reduced_edges": edges, "coordinate_pairs": 28,
               "transported_protected_witnesses": transported,
               "local_choice_checks": row_checks, "literal_decoder_outputs": columns,
               "rejected_controls": controls, "new_fitting_code_rank": 8,
               "lower_COPY_per_bit": 71, "upper_COPY_per_bit": 72,
               "python_version": sys.version.split()[0], "sha256": {}}
    for name in ("CERTIFICATE.json", "PROOF.md", "README.md", "SOURCES.json",
                 "TASK.json", "VERIFY.json", "verify.py"):
        data = read_bounded(here / name, 131072)
        receipt["sha256"][name] = hashlib.sha256(data).hexdigest()
    if not args.emit:
        print(receipt["status"])
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
