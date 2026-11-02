"""Finite evidence for a written all-prime, all-workspace theorem.

Produced by Nick Petalas. Apache-2.0. No external runtime inputs.
"""

import hashlib
import json
from pathlib import Path

from algebra import (
    coefficients, formal_gate, formal_product, gate, group_table, identity, inverse,
    mul, multiply, projectors, quotient_census, require, target,
)


def expect_rejection(operation, message):
    try:
        operation()
    except ValueError:
        return 1
    raise ValueError("control accepted: " + message)


def formal_loops():
    labels, table = group_table()
    outside = [i for i, (_, j) in enumerate(labels) if j]
    loops = 0
    products = set()
    for a in outside:
        for b in outside:
            for c in outside:
                completed = table[c][table[b][a]]
                if labels[completed][1]:
                    continue
                for p in projectors(2):
                    actual = formal_product(formal_gate(p, b), formal_gate(p, a), table)
                    actual = formal_product(formal_gate(p, c), actual, table)
                    require(actual == formal_gate(p, completed), "literal full-formal loop endpoint")
                    loops += 1
                products.add(completed)
    require(products == {i for i, (_, j) in enumerate(labels) if not j}, "all kernel labels reached")
    return loops


def attaining_words():
    labels, table = group_table()
    lookup = {label: i for i, label in enumerate(labels)}
    normals = [i for i, (a, j) in enumerate(labels) if a != 1 and j == 0]
    endpoints = 0
    words = 0
    for first in normals:
        for second in normals:
            desired = target((first, second, 0))
            for replaced in ((), (0,), (1,), (0, 1)):
                actual = target((0, 0, 0))
                for role, label in enumerate((first, second)):
                    p = tuple(tuple(int(i == role == j) for j in range(3)) for i in range(3))
                    sequence = (label,)
                    if role in replaced:
                        sequence = (lookup[(1, 1)], lookup[(labels[label][0], 2)])
                    for paid in sequence:
                        actual = formal_product(formal_gate(p, paid), actual, table)
                require(actual == desired, "all formal coefficients and arbitrary dirty role restored")
                words += 1
            endpoints += 1
    return {"target_pairs": endpoints, "words": words, "roles": 3, "group_labels": 21}


def weighted_screen():
    cases = 0
    for a in range(1, 10):
        for b in range(1, 10):
            expected = 2 * min(a, 2 * b)
            witnesses = (2 * a, a + 2 * b, 4 * b)
            require(min(witnesses) == expected, "attaining weighted envelope")
            for normal in range(13):
                for outside in range(13):
                    if 3 * normal + 2 * outside < 6:
                        continue
                    if normal == 0 and outside < 4:
                        continue
                    require(a * normal + b * outside >= expected, "rank plus loop lower envelope")
                    cases += 1
    return cases


def direct_triples():
    factors = [(p, gate(p, scalar, 2, 7))
               for p in projectors(2) for scalar in (2, 3)]
    loops = 0
    for p, first in factors:
        for q, second in factors:
            for r, third in factors:
                actual = multiply(third, multiply(second, first, 2, 7), 2, 7)
                if actual == identity(2):
                    require(p == q == r, "direct triple loop has a common projector")
                    loops += 1
    require(loops == 12, "direct triples agree with pair/inverse census")
    return {"triples": len(factors) ** 3, "loops": loops}


def character_matrix(matrix, labels):
    rows = []
    for row in matrix:
        result = []
        for entry in row:
            value = 0
            for index, (_, exponent) in enumerate(labels):
                if (entry >> index) & 1:
                    value ^= (1, 2, 3)[exponent]
            result.append(value)
        rows.append(tuple(result))
    return tuple(rows)


def controls():
    p = ((1, 0), (0, 0))
    total = 0
    for bad in (((1, 2), (0, 0)), ((1, 0), (0, 1)), ((0, 1), (0, 0))):
        total += expect_rejection(lambda bad=bad: gate(bad, 2, 2, 7), "projector domain")
    for bad in (0, 1, 4):
        total += expect_rejection(lambda bad=bad: gate(p, bad, 2, 7), "scalar domain")
    for bad in (-1, 1 << 21):
        total += expect_rejection(lambda bad=bad: coefficients(bad), "coefficient domain")
    # Dropping the binary restriction really changes the three-factor theorem.
    nonbinary = (((2, 0), (0, 1)), ((2, 3), (0, 1)), ((2, 1), (0, 1)))
    actual = multiply(nonbinary[2], multiply(nonbinary[1], nonbinary[0], 2, 7), 2, 7)
    require(actual == identity(2), "nonbinary counterexample closes")
    require(len(set(nonbinary)) == 3, "nonbinary projectors differ")
    labels, table = group_table()
    lookup = {label: i for i, label in enumerate(labels)}
    one_output = formal_gate(p, lookup[(2, 0)])
    fake_pair = target((lookup[(2, 0)], lookup[(3, 0)]))
    require(character_matrix(one_output, labels) == character_matrix(fake_pair, labels) == identity(2),
            "quotient alone accepts the wrong full endpoint")
    total += expect_rejection(lambda: require(one_output == fake_pair, "full endpoint"), "quotient-only test")
    dirty = formal_gate(((1, 0, 0), (0, 0, 0), (1, 0, 0)), lookup[(2, 0)])
    total += expect_rejection(lambda: require(dirty == target((lookup[(2, 0)], 0, 0)), "restoration"),
                              "omitted dirty-output restoration")
    altered = multiply(gate(p, 3, 2, 7), multiply(gate(p, 2, 2, 7), gate(p, 2, 2, 7), 2, 7), 2, 7)
    total += expect_rejection(lambda: require(altered == identity(2), "altered loop"), "changed scalar")
    return total


def main():
    fields = ((2, 7), (3, 11))
    for degree, polynomial in fields:
        for value in range(1, 1 << degree):
            require(mul(value, inverse(value, degree, polynomial), degree, polynomial) == 1,
                    "finite-field inverse")
    receipt = {
        "status": "PASS_SEMILINEAR_TWO_NORMAL_PRICES",
        "claim_type": "scoped written proof with exact finite corroboration",
        "tariff": "2 min(a, 2b)",
        "quotient": [quotient_census(d, f, r) for d, f in fields for r in range(1, 4)],
        "direct_triples": direct_triples(),
        "literal_outside_loops": formal_loops(),
        "attainment": attaining_words(),
        "weighted_grid_cases": weighted_screen(),
        "rejection_controls": controls(),
    }
    package = Path(__file__).resolve().parent
    receipt["sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(package.iterdir()) if p.is_file()}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
