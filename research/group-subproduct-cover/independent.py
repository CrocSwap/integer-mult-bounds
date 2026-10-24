#!/usr/bin/env python3
"""Recompute triple classes and all regular-action columns without primary code.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import itertools
import json
from pathlib import Path


def check(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def permutation_group(order21):
    # Group elements are permutations; regular-action addresses are those elements.
    if order21:
        permutations = [tuple((i + 2**j * x) % 7 for x in range(7))
                        for i in range(7) for j in range(3)]
    else:
        permutations = [tuple((i + x) % 7 for x in range(7)) for i in range(7)]
    index = {p: i for i, p in enumerate(permutations)}
    check(len(index) == len(permutations), "faithful element encoding")

    def product(a, b):
        left, right = permutations[a], permutations[b]
        return index[tuple(left[right[x]] for x in range(7))]

    return len(permutations), product


def quaternion_group():
    elements = [tuple(sign * int(i == j) for j in range(4))
                for sign in (1, -1) for i in range(4)]
    index = {q: i for i, q in enumerate(elements)}

    def product(a, b):
        r, x, y, z = elements[a]
        s, u, v, w = elements[b]
        value = (r*s-x*u-y*v-z*w, r*u+x*s+y*w-z*v,
                 r*v-x*w+y*s+z*u, r*w+x*v-y*u+z*s)
        return index[value]

    return len(elements), product


def census(size, product):
    records = []
    histogram = {2: 0, 3: 0}
    columns = 0
    for targets in itertools.combinations(range(1, size), 3):
        relation = next(((g, h) for g, h in itertools.permutations(targets, 2)
                         if product(g, h) in set(targets) - {g, h}), None)
        if relation is None:
            word = targets
            masks = [1 << i for i in range(3)]
        else:
            word = relation
            g, h = word
            masks = [{g: 1, h: 2, product(g, h): 3}[t] for t in targets]
        # Two independent dirty registers must retain every address basis vector.
        for mask, target in zip(masks + [0, 0], targets + (0, 0)):
            for address in range(size):
                output = address
                for position in reversed(range(len(word))):
                    if mask >> position & 1:
                        output = product(word[position], output)
                check(output == product(target, address), "regular endpoint")
                columns += 1
        records.append([list(targets), len(word)])
        histogram[len(word)] += 1
    return {
        "triples": len(records), "two_calls": histogram[2], "three_calls": histogram[3],
        "records_sha256": hashlib.sha256(encoded(records).encode()).hexdigest(),
        "regular_columns": columns,
    }


def main():
    groups = {"C7": permutation_group(False), "C7:C3": permutation_group(True),
              "Q8": quaternion_group()}
    actual = {name: census(*group) for name, group in groups.items()}
    expected = json.loads((Path(__file__).resolve().parent / "RESULT.json").read_text())["groups"]
    check(encoded(actual) == encoded(expected), "independent receipt mismatch")
    size, product = groups["C7:C3"]
    check(product(1, 3) != product(3, 1), "noncommuting order-21 control")
    check(not any(product(g, h) in {3, 6, 12} - {g, h}
                  for g, h in itertools.permutations((3, 6, 12), 2)), "actual exclusion")
    _, q = groups["Q8"]
    check(q(1, 2) == 3 and q(2, 1) == 7, "quaternion orientation")
    # A faithful group action can still have a kernel on linear combinations.
    # In the regular action this formal element has fourteen nonzero outputs at e.
    regular = {product(3*i, 0): 1 for i in range(7)}
    regular.update({product(3*i+1, 0): -1 for i in range(7)})
    check(len(regular) == 14 and 0 in regular and 1 in regular, "regular alias detection")
    columns = sum(row["regular_columns"] for row in actual.values())
    triples = sum(row["triples"] for row in actual.values())
    print(f"PASS_INDEPENDENT_SUBPRODUCT_COVER triples={triples} regular_columns={columns} no_new_kappa")


if __name__ == "__main__":
    main()
