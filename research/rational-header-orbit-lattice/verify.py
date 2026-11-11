#!/usr/bin/env python3
"""Exact corroboration of rational header lattice invariants. Apache-2.0."""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    require(1 <= n <= 8, "matrix dimension")
    return [[F(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def multiply(a, b):
    require(1 <= len(a) <= 9 and len(a[0]) == len(b) <= 9, "matrix shape")
    require(1 <= len(b[0]) <= 9, "matrix width")
    return [[sum(x * y for x, y in zip(row, col))
             for col in zip(*b)] for row in a]


def inverse(a):
    n = len(a)
    aug = [list(row) + tail for row, tail in zip(a, identity(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if aug[i][j]), None)
        require(pivot is not None, "singular matrix")
        aug[j], aug[pivot] = aug[pivot], aug[j]
        scale = aug[j][j]
        aug[j] = [x / scale for x in aug[j]]
        for i in range(n):
            if i != j:
                scale = aug[i][j]
                aug[i] = [x - scale * y for x, y in zip(aug[i], aug[j])]
    return [row[n:] for row in aug]


def sign_form(n):
    require(n in (2, 4, 6, 8), "even dimension")
    return [[F((i > j) - (i < j)) for j in range(n)] for i in range(n)]


def canonical(n):
    return identity(n) + [[F(-((-1) ** i)) for i in range(n)]]


def apply(a, vectors):
    return transpose(multiply(a, transpose(vectors)))


def basis(vectors):
    n = len(vectors[0])
    require(len(vectors) == n + 1, "saturated tuple")
    return transpose(vectors[:n])


def same_lattice(a, b):
    ab = multiply(inverse(a), b)
    ba = multiply(inverse(b), a)
    return all(x.denominator == 1 for m in (ab, ba) for row in m for x in row)


def residues(vectors, lattice_basis):
    coords = apply(inverse(lattice_basis), vectors)
    require(all(x.denominator == 1 for row in coords for x in row),
            "vector outside lattice")
    return Counter(tuple(x.numerator % 2 for x in row) for row in coords)


def ambient_residues(vectors):
    require(all(x.denominator % 2 for row in vectors for x in row),
            "not 2-locally integral")
    return Counter(tuple(x.numerator % 2 for x in row) for row in vectors)


def move(vectors, index, direction):
    require(direction in (-1, 1) and 0 <= index < len(vectors) - 1,
            "Hurwitz move")
    result = [list(row) for row in vectors]
    a, b = result[index:index + 2]
    if direction == 1:
        result[index:index + 2] = [b, [2 * y - x for x, y in zip(a, b)]]
    else:
        result[index:index + 2] = [[2 * x - y for x, y in zip(a, b)], a]
    return result


def check_header(vectors, omega):
    n = len(omega)
    require(n in (2, 4, 6, 8) and len(vectors) == n + 1, "header shape")
    rows = multiply(vectors, omega)
    gram = multiply(rows, transpose(vectors))
    expected = [[F((i > j) - (i < j)) for j in range(n + 1)]
                for i in range(n + 1)]
    require(gram == expected, "normalized Gram")
    product = identity(n)
    for x, y in zip(vectors, rows):
        unit = [[F(i == j) - 2 * x[i] * y[j] for j in range(n)]
                for i in range(n)]
        product = multiply(unit, product)
    require(product == [[F(-(i == j)) for j in range(n)] for i in range(n)],
            "full header product")
    b = basis(vectors)
    require(multiply(multiply(transpose(b), omega), b) == sign_form(n),
            "intrinsic integral frame")


def rational_transvection(omega, vector, parameter):
    row = multiply([vector], omega)[0]
    n = len(vector)
    return [[F(i == j) + parameter * vector[i] * row[j] for j in range(n)]
            for i in range(n)]


def rational_walks():
    fixtures = steps = 0
    for n in (2, 4, 6, 8):
        omega = sign_form(n)
        for denominator in (3, 5, 7):
            v = [F((i % 3) - 1) for i in range(n)]
            g = rational_transvection(omega, v, F(1, denominator))
            start = apply(g, canonical(n))
            check_header(start, omega)
            b = basis(start)
            invariant = residues(start, b)
            fixtures += 1
            current = start
            for k in range(16):
                index, direction = (3 * k + 1) % n, (-1 if k % 3 == 0 else 1)
                following = move(current, index, direction)
                check_header(following, omega)
                require(same_lattice(b, basis(following)), "changed lattice")
                require(residues(following, b) == invariant, "changed intrinsic residues")
                require(move(following, index, -direction) == current, "inverse move")
                current = following
                steps += 1
    return {"rational_fixtures": fixtures, "literal_walk_steps": steps}


def odd_denominator_family():
    omega = sign_form(2)
    family = []
    for m in range(1, 32, 2):
        g = [[F(1, m), F(0)], [F(0), F(m)]]
        vectors = apply(g, canonical(2))
        check_header(vectors, omega)
        require(ambient_residues(vectors) == ambient_residues(canonical(2)),
                "ambient reduction differs")
        require(residues(vectors, g) == residues(canonical(2), identity(2)),
                "intrinsic reference coordinates")
        family.append((m, vectors, g))
    pairs = 0
    for (_, _, a), (_, _, b) in combinations(family, 2):
        require(not same_lattice(a, b), "family lattices coincide")
        require(a[0][0] * a[1][1] == b[0][0] * b[1][1] == 1,
                "covolume control")
        pairs += 1
    return {"odd_denominator_headers": len(family), "distinct_lattice_pairs": pairs}


def intrinsic_counterexample():
    omega = sign_form(4)
    g = rational_transvection(omega, [F(1), F(0), F(1), F(0)], F(1, 3))
    start = apply(g, canonical(4))
    h = rational_transvection(omega, [F(1), F(0), F(0), F(0)], F(1))
    other = apply(multiply(g, h), canonical(4))
    check_header(start, omega)
    check_header(other, omega)
    require(same_lattice(basis(start), basis(other)), "same-lattice control")
    require(residues(start, basis(start)) != residues(other, basis(start)),
            "intrinsic residue obstruction absent")
    return {"same_lattice_different_residue_pairs": 1}


def rejection_controls():
    caught = 0
    try:
        inverse([[F(1), F(2)], [F(2), F(4)]])
    except ValueError:
        caught += 1
    try:
        ambient_residues([[F(1, 2), F(0)]])
    except ValueError:
        caught += 1
    try:
        residues([[F(1, 3), F(0)]], identity(2))
    except ValueError:
        caught += 1
    try:
        move(canonical(2), 2, 1)
    except ValueError:
        caught += 1
    altered = canonical(2)
    altered[2][0] += 1
    try:
        check_header(altered, sign_form(2))
    except ValueError:
        caught += 1
    require(caught == 5, "rejection controls")
    return {"rejection_controls": caught}


def source_hashes():
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result = {}
    for name in names:
        with (root / name).open("rb") as source:
            raw = source.read(256 * 1024 + 1)
        require(len(raw) <= 256 * 1024, "package file size")
        result[name] = sha256(raw).hexdigest()
    return result


def main():
    require(len(sys.argv) == 1, "no command-line arguments accepted")
    result = {"status": "PASS_RATIONAL_HEADER_ORBIT_LATTICE", "no_new_kappa": True}
    for counts in (rational_walks(), odd_denominator_family(),
                   intrinsic_counterexample(), rejection_controls()):
        result.update(counts)
    result["source_sha256"] = source_hashes()
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
