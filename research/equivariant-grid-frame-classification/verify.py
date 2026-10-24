#!/usr/bin/env python3
"""Exact finite corroboration of the frame-group rounding theorem.

Produced by Nick Petalas. Apache-2.0. Standard library only; no source imports.
"""

import argparse
from fractions import Fraction as F
import hashlib
from itertools import permutations, product
import json
from math import ceil, floor, gcd, lcm
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(d):
    require(1 <= d <= 3, "fixture dimension outside 1..3")
    return tuple(tuple(int(i == j) for j in range(d)) for i in range(d))


def apply(a, x):
    return tuple(sum(c * v for c, v in zip(row, x)) for row in a)


def multiply(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(a)))
                       for j in range(len(a))) for i in range(len(a)))


def difference(x, y):
    return tuple(a - b for a, b in zip(x, y))


def determinant(a):
    d = len(a)
    total = 0
    for p in permutations(range(d)):
        inversions = sum(p[i] > p[j] for i in range(d) for j in range(i + 1, d))
        term = (-1) ** inversions
        for i in range(d):
            term *= a[i][p[i]]
        total += term
    return total


def invariant_norm(group, x):
    return max(abs(v) for g in group for v in apply(g, x))


def fixed_basis(stabilizer, d):
    """Rational row reduction, followed by clearing each basis denominator."""
    rows = [[F(h[i][j] - int(i == j)) for j in range(d)]
            for h in stabilizer for i in range(d)]
    pivots = []
    rank = 0
    for col in range(d):
        pivot = next((r for r in range(rank, len(rows)) if rows[r][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][col]
        rows[rank] = [v / scale for v in rows[rank]]
        for r in range(len(rows)):
            if r != rank:
                scale = rows[r][col]
                rows[r] = [v - scale * w for v, w in zip(rows[r], rows[rank])]
        pivots.append(col)
        rank += 1
    basis = []
    for free in range(d):
        if free in pivots:
            continue
        x = [F(int(j == free)) for j in range(d)]
        for r, col in enumerate(pivots):
            x[col] = -rows[r][free]
        denominator = lcm(*(v.denominator for v in x))
        z = tuple(int(v * denominator) for v in x)
        divisor = gcd(*z)
        z = tuple(v // divisor for v in z)
        require(all(apply(h, z) == z for h in stabilizer), "invalid fixed basis")
        basis.append(z)
    require(len(basis) + rank == d, "nullity mismatch")
    return tuple(basis)


def round_point(group, x):
    """Finite orbit canonicalization and nearest stabilizer-fixed lattice point."""
    y = min(apply(g, x) for g in group)
    transports = [g for g in group if apply(g, x) == y]
    stabilizer = tuple(h for h in group if apply(h, y) == y)
    basis = fixed_basis(stabilizer, len(x))
    radius = sum((invariant_norm(group, b) for b in basis), F(0)) / 2
    require(radius <= 20, "fixture candidate-radius cap exceeded")
    boxes = [range(ceil(v - radius), floor(v + radius) + 1) for v in y]
    candidates = []
    for z in product(*boxes):
        if all(apply(h, z) == z for h in stabilizer):
            error = invariant_norm(group, difference(z, y))
            if error <= radius:
                candidates.append((error, z))
    require(bool(candidates), "fixed lattice covering failed")
    error, z = min(candidates)
    outputs = []
    for g in transports:
        inverse = next(h for h in group if multiply(h, g) == identity(len(x)))
        outputs.append(apply(inverse, z))
    require(all(q == outputs[0] for q in outputs), "transport ambiguity")
    require(invariant_norm(group, difference(outputs[0], x)) == error,
            "transport changed invariant error")
    return outputs[0], radius


def powers(a, order):
    require(1 <= order <= 8, "fixture order cap exceeded")
    out = [identity(len(a))]
    for _ in range(1, order):
        out.append(multiply(a, out[-1]))
    require(multiply(a, out[-1]) == out[0], "wrong declared order")
    return tuple(out)


def fixture_groups():
    c3 = powers(((0, -1), (1, -1)), 3)
    c4 = powers(((0, -1), (1, 0)), 4)
    reflection = ((1, 0), (0, -1))
    d4 = tuple(sorted(set(c4 + tuple(multiply(g, reflection) for g in c4))))
    p, pinv = ((1, 2), (0, 1)), ((1, -2), (0, 1))
    sheared = tuple(multiply(multiply(p, g), pinv) for g in d4)
    s3 = tuple(tuple(tuple(int(j == perm[i]) for j in range(3))
                     for i in range(3)) for perm in permutations(range(3)))
    negative_swap = (identity(2), ((0, -1), (-1, 0)))
    return {"order_three": c3, "dihedral_eight": d4,
            "sheared_dihedral_eight": sheared,
            "permutation_six": s3, "negative_swap": negative_swap}


def check_group(group):
    require(1 <= len(group) <= 8, "group size cap exceeded")
    d = len(group[0])
    require(identity(d) in group, "missing identity")
    require(len(set(group)) == len(group), "duplicate group element")
    for g in group:
        require(abs(determinant(g)) == 1, "nonunimodular frame")
        require(any(multiply(h, g) == identity(d) for h in group), "missing inverse")
        for h in group:
            require(multiply(g, h) in group, "group is not closed")


def check_rounders():
    report = {}
    for name, group in fixture_groups().items():
        check_group(group)
        d = len(group[0])
        points = calls = 0
        worst = F(0)
        for denominator in (1, 2, 3, 4):
            for numerators in product(range(-2, 3), repeat=d):
                x = tuple(F(v, denominator) for v in numerators)
                q, radius = round_point(group, x)
                require(all(isinstance(v, int) for v in q), "noninteger output")
                error = max(abs(v) for v in difference(q, x))
                require(error <= radius, "absolute-error bound failed")
                if denominator == 1:
                    require(q == x, "integer input changed")
                worst = max(worst, error)
                for g in group:
                    other, _ = round_point(group, apply(g, x))
                    require(other == apply(g, q), "equivariance failed")
                    calls += 1
                points += 1
        report[name] = {"dimension": d, "order": len(group), "points": points,
                        "equivariance_checks": calls, "maximum_observed_error": str(worst)}
    return report


def check_seed_matrices():
    counts = {}
    for d, entries, moduli in ((2, range(-2, 3), range(2, 9)),
                               (3, range(-1, 2), range(2, 5))):
        checked = 0
        for values in product(entries, repeat=d * d):
            z = tuple(tuple(values[i * d + j] for j in range(d)) for i in range(d))
            for m in moduli:
                e = tuple(tuple(m * z[i][j] - int(i == j) for j in range(d))
                          for i in range(d))
                det = determinant(e)
                require(det != 0 and (det - (-1) ** d) % m == 0,
                        "refined-grid error matrix is singular")
                checked += 1
        counts[str(d)] = checked
    return counts


def check_controls():
    """Each control discriminates a premise or an essential construction step."""
    swap = ((0, -1), (-1, 0))
    x = (F(1, 2), F(-1, 2))
    require(apply(swap, x) == x, "stabilizer fixture changed")
    naive = min(product((0, 1), (-1, 0)))
    require(apply(swap, naive) != naive, "unrestricted tie lost its ambiguity")
    constrained, _ = round_point((identity(2), swap), x)
    require(apply(swap, constrained) == constrained, "fixed tie not repaired")
    # Coordinatewise nearest-even rounding need not commute with finite frames.
    reflection = ((1, 1), (0, -1))
    witness = None
    for a, b in product(range(-4, 5), repeat=2):
        v = (F(a, 2), F(b, 2))
        lhs = tuple(round(t) for t in apply(reflection, v))
        rhs = apply(reflection, tuple(round(t) for t in v))
        if lhs != rhs and witness is None:
            witness = {"input": [str(t) for t in v], "lhs": lhs, "rhs": rhs}
    require(witness is not None, "coordinatewise failure disappeared")
    shear = ((1, 1), (0, 1))
    # With m=1, q(x)=x is equivariant even for this infinite shear group.
    seed_outputs = identity(2)
    unrefined_error = tuple(tuple(seed_outputs[i][j] - int(i == j)
                                 for j in range(2)) for i in range(2))
    require(determinant(unrefined_error) == 0, "m=1 error matrix changed")
    for point in product(range(-2, 3), repeat=2):
        require(apply(shear, point) == tuple(int(v) for v in apply(shear, point)),
                "identity rounder left the unrefined integer domain")
    for k in range(21):
        g = ((1, k), (0, 1))
        require(apply(g, (0, F(1, 2))) == (F(k, 2), F(1, 2)), "orbit changed")
        require(apply(g, (0, F(-1, 2)))[0] == F(-k, 2), "linear error growth")
    require(determinant(shear) == 1, "shear not unimodular")
    r = ((1, 1), (0, -1))
    s = ((1, 0), (0, -1))
    require(multiply(r, r) == identity(2) and multiply(s, s) == identity(2),
            "involution generators changed")
    require(multiply(r, s) == ((1, -1), (0, 1)), "infinite product changed")
    return {"stabilizer_tie": {"input": list(map(str, x)), "naive": naive,
                               "fixed": constrained},
            "coordinatewise_failure": witness,
            "controls": ["stabilizer tie", "coordinatewise finite-frame failure",
                         "m=1 singular seed", "shear error growth",
                         "finite-order generators with infinite product"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="exclusively create an external receipt")
    args = parser.parse_args()
    report = {"claim_type": "scoped proof", "evidence": "finite corroboration",
              "rounders": check_rounders(), "seed_matrices": check_seed_matrices(),
              "controls": check_controls()}
    package = Path(__file__).resolve().parent
    report["package_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(package.iterdir()) if p.is_file()}
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        require(not args.receipt.resolve().is_relative_to(package),
                "receipt must be outside the package")
        with args.receipt.open("x", encoding="utf-8") as output:
            output.write(payload)
    print(payload, end="")
    print("PASS_EQUIVARIANT_GRID_FRAME_CLASSIFICATION no_new_kappa")


if __name__ == "__main__":
    main()
