#!/usr/bin/env python3
"""Finite corroboration of the degree-conditioned polynomial cost law."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import comb
from pathlib import Path

CONFIGURATIONS = ((2, 4), (3, 2), (4, 2), (5, 1))
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
ZERO = ()
ONE = (1,)
IDENTITY = (ONE, ZERO, ZERO, ONE)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def raw_multiply(q, a, b):
    if q != 4:
        return a * b % q
    value = 0
    for bit in range(2):
        if b & (1 << bit):
            value ^= a << bit
    if value & 4:
        value ^= 7  # F4 = F2[z]/(z^2+z+1).
    return value


class Field:
    def __init__(self, q):
        require(q in (2, 3, 4, 5), "unsupported finite field")
        self.q = q
        self.add = tuple(tuple(a ^ b if q == 4 else (a+b) % q
                               for b in range(q)) for a in range(q))
        self.mul = tuple(tuple(raw_multiply(q, a, b) for b in range(q))
                         for a in range(q))
        self.neg = tuple(next(b for b in range(q) if self.add[a][b] == 0)
                         for a in range(q))
        self.inv = (0,) + tuple(next(b for b in range(1, q)
                                    if self.mul[a][b] == 1) for a in range(1, q))
        for a, b, c in product(range(q), repeat=3):
            require(self.mul[a][self.add[b][c]] ==
                    self.add[self.mul[a][b]][self.mul[a][c]], "field distributivity")


def trim(values):
    values = list(values)
    for _ in range(len(values)):
        if not values or values[-1]:
            break
        values.pop()
    return tuple(values)


def add(field, a, b):
    return trim(field.add[a[i] if i < len(a) else 0][b[i] if i < len(b) else 0]
                for i in range(max(len(a), len(b))))


def scale(field, a, c):
    return trim(field.mul[x][c] for x in a)


def multiply(field, a, b):
    require(len(a) <= 9 and len(b) <= 9, "polynomial capacity")
    if not a or not b:
        return ZERO
    out = [0] * (len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] = field.add[out[i+j]][field.mul[x][y]]
    return trim(out)


def matmul(field, a, b):
    return tuple(add(field, multiply(field, a[2*i], b[j]),
                     multiply(field, a[2*i+1], b[2+j]))
                 for i in range(2) for j in range(2))


def determinant(field, matrix):
    a, b, c, d = matrix
    return add(field, multiply(field, a, d), scale(field, multiply(field, b, c), field.neg[1]))


def degree(matrix):
    return max(len(p)-1 for p in matrix)


def directions(field):
    return ((0, 1),) + tuple((1, b) for b in range(field.q))


def transvection(field, row, f):
    a, b = row
    column = (field.neg[b], a)
    return tuple(add(field, ONE if i == j else ZERO,
                     scale(field, f, field.mul[column[i]][row[j]]))
                 for i in range(2) for j in range(2))


def polynomials(field, cap):
    require(0 <= cap <= 4, "degree cap")
    return tuple(trim(p) for p in product(range(field.q), repeat=cap+1))


def free_matrices(field):
    return tuple(tuple(trim((x,)) for x in m)
                 for m in product(range(field.q), repeat=4)
                 if field.add[field.mul[m[0]][m[3]]][field.neg[field.mul[m[1]][m[2]]]])


def inverse_free(field, matrix):
    a, b, c, d = matrix
    det = determinant(field, matrix)
    require(len(det) == 1 and det[0], "free inverse domain")
    s = field.inv[det[0]]
    return tuple(scale(field, p, s) for p in
                 (d, scale(field, b, field.neg[1]), scale(field, c, field.neg[1]), a))


def direct_census(field, cap):
    """Enumerate every determinant-unit quadruple via equal product tails."""
    polys = polynomials(field, cap)
    buckets = defaultdict(list)
    for a, d in product(polys, repeat=2):
        ad = multiply(field, a, d)
        padded = ad + (0,) * (2*cap+1-len(ad))
        buckets[padded[1:]].append((a, d, padded[0]))
    targets = set()
    comparisons = 0
    for pairs in buckets.values():
        for a, d, ad0 in pairs:
            for b, c, bc0 in pairs:
                comparisons += 1
                if ad0 != bc0:
                    targets.add((a, b, c, d))
    return targets, comparisons


def normal_forms(field, cap):
    levels = [[] for _ in range(cap+1)]
    levels[0].append((IDENTITY, None, 0))
    coefficients = tuple(f for f in polynomials(field, cap) if f and f[0] == 0)
    for total in range(cap):
        for matrix, last, cost in levels[total]:
            for row in directions(field):
                if row == last:
                    continue
                for f in coefficients:
                    new_degree = total+len(f)-1
                    if new_degree <= cap:
                        new = matmul(field, matrix, transvection(field, row, f))
                        require(degree(new) == new_degree, "reduced degree identity")
                        levels[new_degree].append((new, row, cost+1))
    return levels


def census(field, cap):
    direct, comparisons = direct_census(field, cap)
    free = free_matrices(field)
    order = (field.q**2-1)*(field.q**2-field.q)
    require(len(free) == order, "free group cardinality")
    seen = {}
    histograms = [Counter() for _ in range(cap+1)]
    for total, level in enumerate(normal_forms(field, cap)):
        for matrix, _, cost in level:
            for endpoint in free:
                target = matmul(field, matrix, endpoint)
                require(target not in seen, "normal-form collision")
                seen[target] = cost
                histograms[total][cost] += 1
    require(set(seen) == direct, "independent determinant census mismatch")
    require(len(seen) == order*field.q**(2*cap), "degree-bounded total")
    for total in range(1, cap+1):
        for cost in range(1, total+1):
            expected = order*(field.q+1)*(field.q-1)**cost*field.q**(total-1)*comb(total-1, cost-1)
            require(histograms[total][cost] == expected, "joint degree-cost count")
        require(sum(histograms[total].values()) ==
                order*(field.q**2-1)*field.q**(2*total-2), "exact-degree total")
    return {"q": field.q, "maximum_degree": cap, "targets": len(seen),
            "product_tail_comparisons": comparisons,
            "degree_cost_counts": [dict(c) for c in histograms]}


def literal_controls(field):
    polys = polynomials(field, 1)
    invertible = 0
    for row in directions(field):
        a, b = row
        v = (field.neg[b], a)
        pivot = 0 if v[0] else 1
        for u in product(polys, repeat=2):
            matrix = tuple(add(field, ONE if i == j else ZERO, scale(field, u[i], row[j]))
                           for i in range(2) for j in range(2))
            det = determinant(field, matrix)
            if len(det) != 1 or not det[0]:
                continue
            invertible += 1
            const = tuple(trim((p[0],)) if p else ZERO for p in matrix)
            w = add(field, u[pivot], scale(field, trim(u[pivot][:1]), field.neg[1]))
            f = scale(field, w, field.inv[v[pivot]])
            require(matmul(field, const, transvection(field, row, f)) == matrix,
                    "literal paid-factor splitting")
    for s in free_matrices(field):
        inverse = inverse_free(field, s)
        for row in directions(field):
            new = matmul(field, matmul(field, s, transvection(field, row, (0, 1))), inverse)
            candidates = (transvection(field, z, (0, c))
                          for z in directions(field) for c in range(1, field.q))
            require(new in candidates, "scaled free conjugation")
    return invertible


def formula_controls(results):
    # Check full probability law, first moment and second centered moment exactly.
    for q in range(2, 17):
        for d in range(1, 33):
            mass = [Fraction(comb(d-1, r-1)*(q-1)**(r-1), q**(d-1))
                    for r in range(1, d+1)]
            mean = 1+Fraction((d-1)*(q-1), q)
            require(sum(mass) == 1, "probability normalization")
            require(sum(r*p for r, p in enumerate(mass, 1)) == mean, "mean")
            require(sum((r-mean)**2*p for r, p in enumerate(mass, 1)) ==
                    Fraction((d-1)*(q-1), q*q), "variance")
    f = Field(3)
    t = (0, 1)
    row = (0, 1)
    require(matmul(f, transvection(f, row, t), transvection(f, row, t)) ==
            transvection(f, row, (0, 2)), "equal-direction merging control")
    require(matmul(f, transvection(f, row, t), transvection(f, row, (0, 2))) ==
            IDENTITY, "opposite-coefficient cancellation control")
    require(degree(transvection(f, row, ONE)) == 0, "constant coefficient control")
    require(len(determinant(f, ((1, 1), ZERO, ZERO, ONE))) == 2, "nonunit determinant control")
    require(determinant(f, (ZERO, ZERO, ZERO, ONE)) == ZERO, "singular endpoint control")
    s = ((2,), ZERO, ZERO, ONE)
    conjugate = matmul(f, matmul(f, s, transvection(f, row, t)), inverse_free(f, s))
    require(conjugate != transvection(f, row, t), "missing conjugation scalar control")
    require(results[0]["degree_cost_counts"][4] == {1: 144, 2: 432, 3: 432, 4: 144},
            "binary degree-four compatibility")
    require(results[1]["degree_cost_counts"][2] != {1: 1152, 2: 1152},
            "missing field-weight control")
    return 8


def receipt(results, paid_counts, controls):
    root = Path(__file__).resolve().parent
    sources = json.loads((root / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            payload = (root.parent.parent / row["path"]).read_bytes()
            require(sha256(payload).hexdigest() == row["sha256"], "source hash")
    hashes = {name: sha256((root / name).read_bytes()).hexdigest() for name in FILES}
    result = {"schema": "polynomial-cost-distribution/v1", "files_sha256": hashes,
              "censuses": results, "invertible_paid_parameters": paid_counts,
              "control_groups": controls, "probability_cases": 480}
    print(json.dumps(result, sort_keys=True))
    print("PASS_POLYNOMIAL_COST_DISTRIBUTION targets=" + str(sum(r["targets"] for r in results))
          + " fields=4 probability_cases=480 controls=" + str(controls) + " no_new_kappa")


def main():
    results = []
    paid_counts = {}
    for q, cap in CONFIGURATIONS:
        field = Field(q)
        results.append(census(field, cap))
        paid_counts[q] = literal_controls(field)
    controls = formula_controls(results)
    receipt(results, paid_counts, controls)


if __name__ == "__main__":
    main()
