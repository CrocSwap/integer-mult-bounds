#!/usr/bin/env python3
"""Exact literal words over binary dual-number products. Apache-2.0."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

import numpy as np


IDENTITY = (1, 0, 0, 1)
LINES = ((1, 0), (0, 1), (1, 1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(a, b):
    """(a0+a1 e)(b0+b1 e) with e^2=0; restrict to 0,1 for F2."""
    return (a & b & 1) | ((((a & 1) * (b >> 1)) ^
                           ((a >> 1) * (b & 1))) << 1)


def matrix_product(a, b):
    return tuple(multiply(a[2 * i], b[j]) ^
                 multiply(a[2 * i + 1], b[2 + j])
                 for i in range(2) for j in range(2))


def invertible(a):
    return (multiply(a[0], a[3]) ^ multiply(a[1], a[2])) & 1


def paid(u, y):
    return tuple(IDENTITY[2 * i + j] ^ multiply(u[i], y[j])
                 for i in range(2) for j in range(2))


def alphabet(size):
    require(size in (2, 4), "only F2 and F2[e]/e^2 are supported")
    matrices = tuple(a for a in product(range(size), repeat=4) if invertible(a))
    free = tuple(a for a in product(range(2), repeat=4) if invertible(a))
    factors = tuple(tuple(sorted({paid(u, y) for u in product(range(size), repeat=2)
                                  if invertible(paid(u, y))})) for y in LINES)
    require(len(matrices) == (6 if size == 2 else 96), "GL2 inventory")
    require(all(len(f) == (2 if size == 2 else 8) for f in factors), "paid inventory")
    return matrices, free, factors


def literal_costs(size, components):
    """Union Cartesian boxes for every common y1,y2,S, without a pivot test."""
    require(1 <= components <= 3, "component bound")
    matrices, free, factors = alphabet(size)
    index = {a: i for i, a in enumerate(matrices)}
    costs = np.full((len(matrices),) * components, 3, dtype=np.uint8)
    for s, f1, f2 in product(free, factors, factors):
        endpoints = sorted({index[matrix_product(matrix_product(a, b), s)]
                            for a, b in product(f1, f2)})
        costs[np.ix_(*([endpoints] * components))] = 2
    for s, f1 in product(free, factors):
        endpoints = sorted({index[matrix_product(a, s)] for a in f1})
        costs[np.ix_(*([endpoints] * components))] = 1
    for s in free:
        costs[(index[s],) * components] = 0
    return matrices, costs


def delta_values(matrices, components):
    """Literal binary ranks of the two common-input columns for every free T."""
    _, free, _ = alphabet(2)
    shape = (len(matrices),) * components
    delta = np.full(shape, 2, dtype=np.uint8)
    for t in free:
        columns = [matrix_product(a, t) for a in matrices]
        c1 = np.zeros(shape, dtype=np.uint16)
        c2 = np.zeros(shape, dtype=np.uint16)
        for i in range(components):
            view = [1] * components
            view[i] = len(matrices)
            left = np.array([(a[0] ^ 1) | (a[2] << 2) for a in columns], np.uint16)
            right = np.array([a[1] | ((a[3] ^ 1) << 2) for a in columns], np.uint16)
            c1 |= left.reshape(view) << (4 * i)
            c2 |= right.reshape(view) << (4 * i)
        rank = np.where((c1 == 0) & (c2 == 0), 0,
                        np.where((c1 == 0) | (c2 == 0) | (c1 == c2), 1, 2))
        np.minimum(delta, rank, out=delta, casting="unsafe")
    return delta


def pivot_mask(matrices, components):
    """Independent unit-pivot predicate, not used to construct literal costs."""
    mask = np.zeros((len(matrices),) * components, dtype=bool)
    for phi, t in product(LINES, repeat=2):
        good = []
        for a in matrices:
            value = 0
            for i, j in product(range(2), repeat=2):
                value ^= multiply(phi[i], multiply(a[2 * i + j], t[j]))
            good.append(bool(value & 1))
        indices = np.flatnonzero(good)
        mask[np.ix_(*([indices] * components))] = True
    return mask


def three_factor_words(matrices):
    """Check the noncommutative-order formula on each local GL2 element."""
    reversed_failures = 0
    for a, b, c, d in matrices:
        r = 0 if d & 1 else 1
        big_d = d ^ multiply(r, b)
        require(big_d & 1, "D must be a unit")
        inverse = next(x for x in range(4) if multiply(big_d, x) == 1)
        f = multiply(inverse, c ^ multiply(r, a))
        e = a ^ multiply(b, f)
        first = paid((0, r), (1, 0))
        second = paid((b, big_d ^ 1), (0, 1))
        third = paid((e ^ 1, f), (1, 0))
        target = (a, b, c, d)
        require(matrix_product(matrix_product(first, second), third) == target,
                "three-factor witness")
        changed = (third[0] ^ 1, *third[1:])
        require(matrix_product(matrix_product(first, second), changed) != target,
                "changed-factor control")
        reversed_failures += matrix_product(matrix_product(third, second), first) != target
    require(reversed_failures > 0, "word-order control")
    return reversed_failures


def check_arithmetic():
    for a, b, c in product(range(4), repeat=3):
        require(multiply(a, b) == multiply(b, a), "commutativity")
        require(multiply(multiply(a, b), c) == multiply(a, multiply(b, c)),
                "associativity")
        require(multiply(a, b ^ c) == multiply(a, b) ^ multiply(a, c),
                "distributivity")
        require((multiply(a, b) & 1) == ((a & 1) * (b & 1)), "residue map")
    require(multiply(2, 2) == 0 and multiply(2, 1) == 2, "nonzero nilpotent")


def check_case(components):
    matrices, costs = literal_costs(4, components)
    residue_matrices, residue_costs = literal_costs(2, components)
    residue_index = {a: i for i, a in enumerate(residue_matrices)}
    projection = np.array([residue_index[tuple(x & 1 for x in a)] for a in matrices])
    reduced = residue_costs[np.ix_(*([projection] * components))]
    delta = delta_values(matrices, components)
    require(np.array_equal(costs, np.maximum(delta, reduced)), "exact cost formula")
    require(np.array_equal(costs <= 2, reduced <= 2), "radical invariance")
    require(np.array_equal(costs <= 2, pivot_mask(matrices, components)), "unit pivots")
    require(np.all(costs >= delta), "column lower bound")
    histogram = [int(np.count_nonzero(costs == i)) for i in range(4)]
    require(sum(histogram) == 96 ** components, "all invertible targets counted")
    failures = int(np.count_nonzero(costs == 3))
    require(failures == (49152 if components == 3 else 0), "sharp binary threshold")
    transitions = [[int(np.count_nonzero((reduced == i) & (costs == j)))
                    for j in range(4)] for i in range(4)]
    return {"components": components, "targets": costs.size, "cost_histogram": histogram,
            "residue_to_lift_cost": transitions,
            "cost_bytes_sha256": sha256(costs.tobytes()).hexdigest()}


def check_controls():
    matrices, costs = literal_costs(4, 1)
    index = {a: i for i, a in enumerate(matrices)}
    require(int(costs[index[(3, 0, 0, 1)]]) == 1, "one nilpotent diagonal")
    require(int(costs[index[(3, 0, 0, 3)]]) == 2, "two nilpotent diagonals")
    binary, quotient_costs = literal_costs(2, 3)
    bi = {a: i for i, a in enumerate(binary)}
    obstruction = (IDENTITY, (0, 1, 1, 1), (1, 1, 1, 0))
    require(int(quotient_costs[tuple(bi[a] for a in obstruction)]) == 3,
            "known residue obstruction")
    require(not np.all(pivot_mask(binary, 3)), "common-chart control")
    _, two_costs = literal_costs(2, 2)
    require(np.all(two_costs <= 2), "dropped-component control")
    require(all(a in bi for a in obstruction), "each component separately free")


def source_binding():
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    sources = json.loads((package / "SOURCES.json").read_text())
    for entry in sources["files"]:
        if entry["usage"] == "input":
            raw = (root / entry["path"]).read_bytes()
            require(sha256(raw).hexdigest() == entry["sha256"], "source changed")
    names = ("verify.py", "PROOF.md", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json")
    return {name: sha256((package / name).read_bytes()).hexdigest() for name in names}


def main():
    check_arithmetic()
    matrices, _, _ = alphabet(4)
    reversed_failures = three_factor_words(matrices)
    check_controls()
    results = [check_case(k) for k in range(1, 4)]
    receipt = {"sources": source_binding(), "cases": results,
               "reversed_word_failures": reversed_failures}
    encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_RIGHT_VECTOR_LOCAL_PRODUCTS targets=" +
          str(sum(r["targets"] for r in results)) +
          " cost3=49152 formula=exact receipt=" + sha256(encoded.encode()).hexdigest() +
          " no_new_kappa")


if __name__ == "__main__":
    main()
