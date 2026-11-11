"""Finite corroboration of the new square-zero tensor determinant theorem."""

import hashlib
from itertools import product
import json
from math import gcd
from pathlib import Path
import platform

from algebra import (FIELDS, Field, all_matrices, determinant, fixes_tensor,
                     identity, inverse, matmul, preserves_product, require,
                     transpose, unit_matrix, witness)


def field_checks():
    cases = 0
    for q in FIELDS:
        f = Field(q)
        for a, b, c in product(range(q), repeat=3):
            require(f.mul(a, f.add(b, c)) == f.add(f.mul(a, b), f.mul(a, c)),
                    "distributivity")
            require(f.mul(f.mul(a, b), c) == f.mul(a, f.mul(b, c)), "associativity")
            cases += 1
        for a in range(1, q):
            require(f.mul(a, f.inverse(a)) == 1, "inverse law")
    return cases


def rejects(operation):
    try:
        operation()
    except ValueError:
        return 1
    raise ValueError("invalid operation was accepted")


def image_checks():
    reports = []
    for q, n in product(FIELDS, range(3, 9)):
        f = Field(q)
        powers = {f.power(a, n) for a in range(1, q)}
        actual, equations = set(), set()
        rejected = 0
        exponent = (q - 1) // gcd(n, q - 1)
        for triple in product(range(1, q), repeat=3):
            u, v, w = triple
            allowed = f.mul(v, w) in powers and f.mul(u, w) in powers
            if (f.power(f.mul(v, w), exponent) == 1
                    and f.power(f.mul(u, w), exponent) == 1):
                equations.add(triple)
            if not allowed:
                rejected += rejects(lambda: witness(triple, n, f))
                continue
            matrices = witness(triple, n, f)
            require(tuple(determinant(m, f) for m in matrices) == triple,
                    "wrong attaining determinant")
            require(fixes_tensor(*matrices, f), "literal tensor action failed")
            actual.add(triple)
        require(actual == equations, "equations disagree with constructed image")
        require(len(actual) * gcd(n, q - 1) ** 2 == (q - 1) ** 3, "image order")
        ambient = set(product(range(1, q), repeat=3))
        orbits = set()
        for c in ambient:
            coset = frozenset(tuple(f.mul(a, b) for a, b in zip(c, d)) for d in actual)
            orbits.add(coset)
        require(len(orbits) == gcd(n, q - 1) ** 2, "SL orbit index")
        reports.append(dict(q=q, dimension=n, attained=len(actual), rejected=rejected,
                            special_linear_orbits=len(orbits)))
    return reports


def automorphism_census(q, n):
    """All raw square matrices, tested by unit, inverse and basis products."""
    f = Field(q)
    tested = invertible = accepted = 0
    determinants = set()
    for matrix in all_matrices(n, f):
        tested += 1
        det = determinant(matrix, f)
        if not det:
            continue
        invertible += 1
        if transpose(matrix)[0] != identity(n)[0]:
            continue
        if preserves_product(matrix, matrix, matrix, f):
            accepted += 1
            determinants.add(det)
    expected = 1
    d = n - 1
    for i in range(d):
        expected *= q ** d - q ** i
    require(accepted == expected, "raw automorphism census order")
    require(determinants == set(range(1, q)), "automorphism determinant image")
    return dict(q=q, dimension=n, raw_matrices=tested, invertible=invertible,
                automorphisms=accepted)


def stabilizer_census():
    """Full GL3(F2)^2 search; the output map is forced by the unit."""
    f, n = Field(2), 3
    invertibles = [m for m in all_matrices(n, f) if determinant(m, f)]
    tested = accepted = 0
    determinants = set()
    for first, second in product(invertibles, repeat=2):
        tested += 1
        b = transpose(second)[0]
        output = matmul(unit_matrix(b, f), first, f)
        if not determinant(output, f) or not preserves_product(first, second, output, f):
            continue
        accepted += 1
        covariant = (transpose(inverse(first, f)), transpose(inverse(second, f)), output)
        require(fixes_tensor(*covariant, f), "raw isotopy/covariant conversion")
        determinants.add(tuple(determinant(m, f) for m in covariant))
    require(accepted == 96 and determinants == {(1, 1, 1)}, "full stabilizer census")
    return dict(q=2, dimension=3, input_map_pairs=tested, stabilizers=accepted)


def norm_census():
    reports = []
    for q, n in ((2, 3), (2, 4), (3, 3), (3, 4), (4, 3), (5, 3), (8, 3)):
        f = Field(q)
        units = 0
        image = set()
        for a in product(range(q), repeat=n):
            det = determinant(unit_matrix(a, f), f)
            require(det == f.power(a[0], n), "literal unit multiplication determinant")
            if a[0]:
                units += 1
                image.add(det)
        require(image == {f.power(a, n) for a in range(1, q)}, "norm image")
        reports.append(dict(q=q, dimension=n, elements=q ** n, units=units,
                            norm_image=sorted(image)))
    return reports


def controls():
    f, n = Field(5), 4
    base = witness((2, 2, 3), n, f)
    require(fixes_tensor(*base, f), "control fixture invalid")
    detected = 0
    for factor in range(3):
        changed = [[row[:] for row in matrix] for matrix in base]
        changed[factor][0][0] = f.add(changed[factor][0][0], 1)
        require(not fixes_tensor(*changed, f), "factor mutation was undetected")
        detected += 1
    raw_inputs = (transpose(inverse(base[0], f)), transpose(inverse(base[1], f)), base[2])
    require(not fixes_tensor(*raw_inputs, f), "raw autotopism input convention accepted")
    detected += 1
    for operation in (lambda: Field(6), lambda: Field(True),
                      lambda: witness((0, 1, 1), n, f),
                      lambda: witness((1, 1, 1), 2, f),
                      lambda: witness((1, 2, 1), n, f),
                      lambda: inverse([[1, 0], [0, 0]], f),
                      lambda: list(all_matrices(5, Field(2))),
                      lambda: f.power(1, 65)):
        detected += rejects(operation)
    # Both restrictions are needed; product-one alone is insufficient.
    for triple in ((1, 2, 1), (2, 1, 1), (2, 3, 1)):
        detected += rejects(lambda: witness(triple, n, f))
    return detected


def main():
    result = dict(status="PASS_SQUAREZERO_TENSOR_CHARACTERS",
                  python=platform.python_version(), field_triples=field_checks(),
                  images=image_checks(), norms=norm_census(),
                  automorphisms=[automorphism_census(q, n)
                                 for q, n in ((2, 3), (2, 4), (3, 3))],
                  stabilizer=stabilizer_census(), controls=controls())
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "algebra.py", "verify.py")
    result["sha256"] = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                        for name in names}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
