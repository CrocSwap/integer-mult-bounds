#!/usr/bin/env python3
"""Exact finite corroboration for the partial-axis theorem; standard library."""

import argparse
import copy
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
BOUND_FILES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank2(rows, width):
    """At most len(rows)*width pivot steps, no mutable shared basis."""
    basis = [0] * width
    rank = 0
    for original in rows:
        value = original
        for pivot in range(width - 1, -1, -1):
            if not (value >> pivot) & 1:
                continue
            if basis[pivot]:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                rank += 1
                break
    return rank


def geometry(n, axes, scale=1):
    require(4 <= n <= 12, "finite checker dimension must be 4..12")
    require(0 <= axes < (1 << n), "axis mask outside dimension")
    require(scale != 0, "axis scale must be nonzero")
    roots = []
    for i in range(n):
        if (axes >> i) & 1:
            roots.append(tuple(scale * (j == i) for j in range(n)))
    for i, j in itertools.combinations(range(n), 2):
        for sign in (1, -1):
            roots.append(tuple((h == i) + sign * (h == j) for h in range(n)))
    pairing = []
    for i, row in enumerate(roots):
        bits = 0
        for j, col in enumerate(roots):
            if i == j or sum(a * b for a, b in zip(row, col)) == 0:
                bits |= 1 << j
        pairing.append(bits)
    return roots, pairing


def support(roots, vector, prime=0):
    bits = 0
    for i, row in enumerate(roots):
        value = sum(a * b for a, b in zip(row, vector))
        if prime:
            value %= prime
        if value:
            bits |= 1 << i
    return bits


def cost(pairing, left, right):
    rows = [row & right for i, row in enumerate(pairing) if (left >> i) & 1]
    return rank2(rows, len(pairing))


def projective_vectors(n, prime):
    require((n, prime) in ((4, 3), (5, 3), (4, 5)), "unregistered census")
    vectors = []
    for vector in itertools.product(range(prime), repeat=n):
        nonzero = [v for v in vector if v]
        if nonzero and nonzero[0] == 1:
            vectors.append(vector)
    require(len(vectors) == (prime ** n - 1) // (prime - 1), "projective count")
    return vectors


def axis_index(vector):
    indices = [i for i, v in enumerate(vector) if v]
    return indices[0] if len(indices) == 1 else None


def local_bound(n, axes, x, y):
    marked = any(v and ((axes >> i) & 1) for i, v in enumerate(x)) and any(
        v and ((axes >> i) & 1) for i, v in enumerate(y)
    )
    if marked:
        return n
    if n % 2 == 0:
        return n - 1
    a, b = axis_index(x), axis_index(y)
    if a is not None and b is not None and a != b:
        return n - 2
    return n if a is None and b is None else n - 1


def mixed_support_census(n, prime):
    """Every intermediate axis mask and projective pair in the finite field."""
    vectors = projective_vectors(n, prime)
    comparisons = 0
    digest = hashlib.sha256()
    histogram = {}
    for axes in range(1, (1 << n) - 1):
        roots, pairing = geometry(n, axes)
        supports = [support(roots, x, prime) for x in vectors]
        for i, x in enumerate(vectors):
            for j, y in enumerate(vectors):
                actual = cost(pairing, supports[i], supports[j])
                require(actual >= local_bound(n, axes, x, y), "mixed-axis tariff")
                histogram[actual] = histogram.get(actual, 0) + 1
                digest.update(bytes((axes, i, j, actual)))
                comparisons += 1
    return {"n": n, "prime": prime, "projective_vectors": len(vectors),
            "axis_masks": (1 << n) - 2, "support_pairs": comparisons,
            "rank_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "sha256": digest.hexdigest()}


def coordinate_attainments():
    records = []
    for n in range(4, 13):
        # Every mask through n=6, then all cardinalities by permutation symmetry.
        masks = range(1, (1 << n) - 1) if n <= 6 else ((1 << k) - 1 for k in range(1, n))
        for axes in masks:
            for scale in (1, 2):
                roots, pairing = geometry(n, axes, scale)
                prices = []
                for i in range(n):
                    vector = tuple(int(j == i) for j in range(n))
                    side = support(roots, vector)
                    price = cost(pairing, side, side)
                    require(price == n - 1 + ((axes >> i) & 1), "coordinate price")
                    prices.append(price)
                expected = n * (n - 1) + axes.bit_count()
                require(sum(prices) == expected, "attained punctured floor")
                records.append({"n": n, "axes": axes, "scale": scale,
                                "prices": prices, "total": expected})
    return records


def endpoint(terms, n):
    return [[sum(x[i] * y[j] for x, y in terms) for j in range(n)] for i in range(n)]


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def expansion_fixtures():
    records = []
    for n in range(4, 9):
        unit = [tuple(Fraction(i == j) for i in range(n)) for j in range(n)]
        base = [(x, x) for x in unit]
        difference = tuple(unit[0][i] - unit[1][i] for i in range(n))
        two_cheap = [(unit[0], unit[1]), (unit[1], unit[0]),
                     (difference, difference)] + base[2:]
        minus = tuple(-v for v in unit[0])
        cancel = base + [(unit[0], unit[1]), (minus, unit[1])]
        # A noncoordinate rational dual pair, plus a split one-extra variant.
        left = tuple(unit[0][i] + Fraction(2, 3) * unit[1][i] for i in range(n))
        dual = tuple(unit[1][i] - Fraction(2, 3) * unit[0][i] for i in range(n))
        shear = [(left, unit[0]), (unit[1], dual)] + base[2:]
        half = tuple(v / 2 for v in left)
        split = [(half, unit[0]), (half, unit[0])] + shear[1:]
        for k in range(1, n):
            axes = ((1 << k) - 1) << (n - k)
            roots, pairing = geometry(n, axes)
            for name, terms in (("coordinate", base), ("two-cheap", two_cheap),
                                ("cancel", cancel), ("rational-shear", shear),
                                ("split", split)):
                require(endpoint(terms, n) == identity(n), "exact Gram coefficient identity")
                prices = [cost(pairing, support(roots, x), support(roots, y)) for x, y in terms]
                floor = n * (n - 1) + k
                require(sum(prices) >= floor, "expansion price below floor")
                require(len(terms) == n or sum(prices) > floor, "overcomplete equality")
                records.append({"n": n, "k": k, "name": name, "terms": len(terms),
                                "prices": prices, "cost": sum(prices), "floor": floor})
    return records


def term_count_bounds():
    checked = 0
    for n in range(4, 129):
        for k in range(n + 1):
            floor = n * (n - 1) + k
            for m in range(n, n + 7):
                if n % 2 == 0:
                    bound = m * (n - 1) + k
                elif m == n:
                    bound = n * (n - 1) + k
                elif m == n + 1:
                    bound = m * (n - 1) - 2 + k
                else:
                    bound = m * (n - 2) + 2 * k
                require(bound >= floor, "count lower bound")
                require(m == n or bound > floor, "strict excess for additional terms")
                checked += 1
    return checked


def canonical(value):
    """JSON spelling distinguishes booleans from integers in receipts."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def controls():
    n, axes = 5, 0b11100
    roots, pairing = geometry(n, axes)
    unit = [tuple(int(i == j) for i in range(n)) for j in range(n)]
    x, y = unit[0], unit[1]
    sx, sy = support(roots, x), support(roots, y)
    require(cost(pairing, sx, sy) == n - 2, "unmatched missing-axis cheap witness")
    require(endpoint([(x, y)], n) != identity(n), "cheap term is not an exact expansion")
    require(sum(x[i] * y[i] for i in range(n)) == 0, "cheap term excluded from square dual")
    require(local_bound(n, axes, unit[2], unit[3]) == n, "retained stars need extra charge")
    require(n * (n - 1) < n * (n - 1) + axes.bit_count(), "unmarked-only bill loses axes")
    edge_roots, _ = geometry(4, 0)
    require(support(edge_roots, (1, 1, 1, 1), 2) == 0, "characteristic two loses injection")
    sparse = [1 << i for i in range(len(pairing))]
    require(cost(sparse, sx, sy) != cost(pairing, sx, sy), "sparse mask changes tariff")
    require(canonical({"cost": 1}) != canonical({"cost": True}), "typed receipt control")
    return 8


def evidence():
    return {"schema": "axis-punctured-root-code-floor/v1",
            "claim_type": "scoped proof with finite corroboration",
            "scope": "n>=4; 0<k<n is new; char(K)!=2; fixed dense pairing; root-code Gram",
            "support_censuses": [mixed_support_census(n, p) for n, p in ((4, 3), (5, 3), (4, 5))],
            "coordinate_attainments": coordinate_attainments(),
            "exact_expansions": expansion_fixtures(),
            "count_inequalities": term_count_bounds(), "controls": controls(),
            "file_sha256": {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                            for name in BOUND_FILES}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="create a new generated receipt")
    args = parser.parse_args()
    result = evidence()
    mutation = copy.deepcopy(result)
    mutation["controls"] = True
    require(canonical(mutation) != canonical(result), "whole-receipt type mutation")
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        saved = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
        require(canonical(saved) == canonical(result), "receipt or bound source mismatch")
    pairs = sum(row["support_pairs"] for row in result["support_censuses"])
    print("PASS_AXIS_PUNCTURED_ROOT_CODE_FLOOR " + json.dumps({
        "support_pairs": pairs, "attainments": len(result["coordinate_attainments"]),
        "expansions": len(result["exact_expansions"]),
        "count_inequalities": result["count_inequalities"], "controls": result["controls"]}))


if __name__ == "__main__":
    main()
