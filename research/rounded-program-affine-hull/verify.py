#!/usr/bin/env python3
"""Exact bounded corroboration of PROOF.md; standard library, no writes."""

from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from math import gcd, lcm
from pathlib import Path
import json

type Step = tuple[bool, tuple[tuple[int, Q], ...], Q]
type Program = tuple[int, tuple[Step, ...], tuple[int, int]]
type Vector = tuple[Q, Q]

MAX_STEPS = 8
MAX_PERIOD = 12
PACKAGE_FILES = (
    "PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def round_half_up(value: Q) -> Q:
    shifted = value + Q(1, 2)
    return Q(shifted.numerator // shifted.denominator)


def program(k: int, steps: tuple[Step, ...], outputs: tuple[int, int]) -> Program:
    require(type(k) is int and 1 <= k <= 2, "parameter count")
    require(1 <= len(steps) <= MAX_STEPS, "step count")
    for position, (rounded, terms, offset) in enumerate(steps):
        require(type(rounded) is bool and isinstance(offset, Q), "step fields")
        require(len(terms) <= MAX_STEPS + 2, "term count")
        for index, coefficient in terms:
            require(type(index) is int and 0 <= index < k + position, "reference")
            require(isinstance(coefficient, Q), "coefficient")
            require(abs(coefficient) <= 12 and coefficient.denominator <= 12,
                    "coefficient bound")
        require(abs(offset) <= 12 and offset.denominator <= 12, "offset bound")
    require(len(outputs) == 2 and all(type(i) is int and 0 <= i < k + len(steps)
                                    for i in outputs), "outputs")
    return k, steps, outputs


def evaluate(p: Program, z: tuple[int, ...]) -> Vector:
    k, steps, outputs = p
    require(len(z) == k and all(type(x) is int for x in z), "parameter tuple")
    values = [Q(x) for x in z]
    for rounded, terms, offset in steps:
        value = offset + sum((c * values[i] for i, c in terms), Q(0))
        values.append(round_half_up(value) if rounded else value)
    return values[outputs[0]], values[outputs[1]]


def linear_data(p: Program) -> tuple[int, tuple[tuple[Q, ...], ...]]:
    k, steps, outputs = p
    rows = [tuple(Q(i == j) for j in range(k)) for i in range(k)]
    period = 1
    for rounded, terms, _offset in steps:
        row = tuple(sum((c * rows[i][j] for i, c in terms), Q(0))
                    for j in range(k))
        if rounded:
            period = lcm(period, *(x.denominator for x in row))
        rows.append(row)
    require(period <= MAX_PERIOD, "period capacity")
    return period, tuple(rows[i] for i in outputs)


def subtract(left: Vector, right: Vector) -> Vector:
    return left[0] - right[0], left[1] - right[1]


def integer_basis(vectors: list[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    """Column Hermite basis using Bezout on the first coordinate."""
    first, second = 0, 0
    for x, y in vectors:
        if x == 0:
            continue
        if first == 0:
            first, second = abs(x), y if x > 0 else -y
            continue
        divisor = gcd(first, x)
        modulus = abs(x) // divisor
        a = pow(first // divisor, -1, modulus) if modulus > 1 else 0
        b = (divisor - a * first) // x
        require(a * first + b * x == divisor, "Bezout identity")
        first, second = divisor, a * second + b * y
    if first == 0:
        vertical = gcd(*(y for _x, y in vectors))
        return ((0, vertical),) if vertical else ()
    vertical = gcd(*(y - (x // first) * second for x, y in vectors))
    if vertical:
        return (first, second % vertical), (0, vertical)
    return ((first, second),)


def rational_basis(vectors: list[Vector]) -> tuple[int, tuple[tuple[int, int], ...]]:
    denominator = lcm(*(v.denominator for row in vectors for v in row))
    scaled = [(int(x * denominator), int(y * denominator)) for x, y in vectors]
    return denominator, integer_basis(scaled)


def same_lattice(left: list[Vector], right: list[Vector]) -> bool:
    denominator = lcm(*(v.denominator for row in left + right for v in row))
    a = [(int(x * denominator), int(y * denominator)) for x, y in left]
    b = [(int(x * denominator), int(y * denominator)) for x, y in right]
    return integer_basis(a) == integer_basis(b)


def in_hermite(v: Vector, h: int, r: int, k: int) -> bool:
    first = v[0] / h
    return first.denominator == 1 and ((v[1] - r * first) / k).denominator == 1


def certificate(p: Program) -> tuple[int, Vector, list[Vector], dict]:
    k = p[0]
    q, matrix = linear_data(p)
    base = evaluate(p, (0,) * k)
    residues = {c: evaluate(p, c) for c in product(range(q), repeat=k)}
    drift = [tuple(q * matrix[j][i] for j in range(2)) for i in range(k)]
    generators = drift + [subtract(v, base) for v in residues.values()]
    return q, base, generators, residues


def check_program(p: Program) -> dict[str, int]:
    q, base, generators, residues = certificate(p)
    k = p[0]
    _q, matrix = linear_data(p)
    literal = []
    for z in product(range(-q, 2 * q), repeat=k):
        value = evaluate(p, z)
        residue = tuple(x % q for x in z)
        displacement = tuple(x - r for x, r in zip(z, residue, strict=True))
        expected = tuple(residues[residue][j] + sum(
            (matrix[j][i] * displacement[i] for i in range(k)), Q(0))
            for j in range(2))
        require(value == expected, "actual translation identity")
        literal.append(subtract(value, base))
    require(same_lattice(generators, literal), "literal output hull")
    closure_checks = 0
    if q <= 2:
        for h, k2 in product(range(1, 4), repeat=2):
            for r in range(k2):
                for offset in (Q(0), Q(1, 2)):
                    anchor = subtract(base, (offset, Q(0)))
                    claimed = all(in_hermite(v, h, r, k2)
                                  for v in [anchor] + generators)
                    observed = all(in_hermite(v, h, r, k2)
                                   for v in [anchor] + literal)
                    require(claimed == observed, "target affine closure")
                    closure_checks += 1
    return {"programs": 1, "literal_outputs": len(literal),
            "residue_outputs": len(residues), "closure_checks": closure_checks}


def nested_program(a: Q, b: Q, alpha: Q, beta: Q) -> Program:
    return program(1, (
        (True, ((0, a),), alpha),
        (True, ((1, b),), beta),
        (False, ((2, Q(1, 3)),), Q(0)),
    ), (0, 3))


def shear_program(h: int, r: int, k: int, a: Q, b: Q,
                  alpha: Q, beta: Q) -> Program:
    return program(2, (
        (False, ((0, Q(h)),), Q(1, 3)),
        (False, ((0, Q(r)), (1, Q(k))), Q(-1, 4)),
        (True, ((2, a),), alpha),
        (False, ((3, Q(1)), (4, Q(1))), Q(0)),
        (True, ((5, b),), beta),
        (False, ((2, Q(1)), (6, Q(1))), Q(0)),
    ), (7, 5))


def census() -> dict[str, int]:
    totals = dict(programs=0, literal_outputs=0, residue_outputs=0, closure_checks=0)
    slopes_a = tuple(Q(x, 2) for x in (-3, -1, 0, 1, 3))
    slopes_b = (Q(-2, 3), Q(0), Q(2, 3), Q(3, 2))
    for a, b, alpha, beta in product(slopes_a, slopes_b, (Q(0), Q(1, 2)),
                                    (Q(0), Q(1, 2))):
        result = check_program(nested_program(a, b, alpha, beta))
        totals = {key: totals[key] + result[key] for key in totals}
    slopes = (Q(-1, 2), Q(0), Q(1, 2), Q(2, 3))
    for h, r, k in ((1, 0, 1), (2, 0, 1), (3, 0, 2), (2, 1, 3)):
        for a, b, alpha, beta in product(slopes, slopes, (Q(0), Q(1, 2)),
                                        (Q(0), Q(1, 2))):
            result = check_program(shear_program(h, r, k, a, b, alpha, beta))
            totals = {key: totals[key] + result[key] for key in totals}
    require(totals["programs"] == 336, "complete program inventory")
    return totals


def basis_controls() -> int:
    """Compare full-rank normal-form indices with every two-column minor."""
    vectors = tuple(product(range(-1, 2), repeat=2))
    for rows in product(vectors, repeat=3):
        basis = integer_basis(list(rows))
        minors = gcd(*(a * d - b * c for a, b in rows for c, d in rows))
        if minors:
            require(len(basis) == 2, "full-rank normal form")
            require(basis[0][0] * basis[1][1] == minors, "index from minors")
        else:
            require(len(basis) <= 1, "rank-deficient normal form")
            nonzero = [v for v in rows if v != (0, 0)]
            if nonzero:
                x, y = nonzero[0]
                content = gcd(x, y)
                sign = 1 if x > 0 or (x == 0 and y > 0) else -1
                unit = (sign * x // content, sign * y // content)
                scale = gcd(*(coordinate for v in rows for coordinate in v))
                require(basis == ((scale * unit[0], scale * unit[1]),),
                        "rank-one normal form")
            else:
                require(basis == (), "zero normal form")
        for x, y in rows:
            if len(basis) == 2:
                h, r = basis[0]
                require(in_hermite((Q(x), Q(y)), h, r, basis[1][1]), "basis spans")
    return len(vectors) ** 3


def semantic_controls() -> dict:
    p = program(2, (
        (False, ((0, Q(3)),), Q(0)),
        (False, ((1, Q(2)),), Q(0)),
        (True, ((2, Q(1, 2)),), Q(0)),
        (False, ((3, Q(1)), (4, Q(1))), Q(0)),
    ), (2, 5))
    q, base, generators, residues = certificate(p)
    reduced_h = [(Q(6), Q(3)), (Q(0), Q(2)), (Q(3), Q(2))]
    nested = nested_program(Q(1, 2), Q(1, 2), Q(0), Q(0))
    zero = program(1, ((True, ((0, Q(0)),), Q(1, 3)),), (1, 1))
    linear = program(1, ((False, ((0, Q(2, 3)),), Q(1, 4)),), (0, 1))
    checks = {
        "example period and origin": q == 2 and base == (0, 0),
        "residue screen passes": all(in_hermite(v, 3, 0, 2) for v in residues.values()),
        "literal drift witness": evaluate(p, (2, 0)) == (6, 3),
        "omit-drift rejects": not all(in_hermite(v, 3, 0, 2) for v in generators),
        "exact hull": same_lattice(generators, [(Q(3), Q(0)), (Q(0), Q(1))]),
        "ideal-image rejects": not in_hermite((Q(3), Q(3, 2)), 3, 0, 1)
        and all(in_hermite(v, 3, 0, 1) for v in generators)
        and not same_lattice(generators, [(Q(3), Q(3, 2)), (Q(0), Q(2))]),
        "nonrectangular period": same_lattice(generators, reduced_h),
        "hull not image finite control": all(
            evaluate(p, (0, m)) != (0, 1) for m in range(-3, 4)),
        "nested denominator": linear_data(nested)[0] == 4,
        "actual inner rounding": evaluate(nested, (1,))[1] == Q(1, 3),
        "invalid period two rejects": evaluate(nested, (2,))[1] != Q(1, 6),
        "signed ties": round_half_up(Q(-1, 2)) == 0 and round_half_up(Q(1, 2)) == 1,
        "rank-zero image": rational_basis(certificate(zero)[2]) == (1, ()),
        "unrounded rational map": linear_data(linear)[0] == 1,
    }
    for name, condition in checks.items():
        require(condition, name)
    check_program(zero)
    check_program(linear)
    return {"example_hull": "3Z x Z", "example_rejected_target": "3Z x 2Z",
            "example_drift_witness": [6, 3], "semantic_controls": list(checks)}


def invalid_controls() -> int:
    invalid = (
        (0, ((False, ((0, Q(1)),), Q(0)),), (0, 0)),
        (1, ((False, ((1, Q(1)),), Q(0)),), (0, 0)),
        (1, ((False, ((0, 1),), Q(0)),), (0, 0)),
        (1, ((False, ((0, Q(1, 13)),), Q(0)),), (0, 0)),
        (1, ((False, ((0, Q(1)),), Q(0)),), (0, 2)),
    )
    rejected = 0
    for args in invalid:
        try:
            program(*args)
        except ValueError:
            rejected += 1
    require(rejected == len(invalid), "invalid inputs must reject")
    return rejected


def main() -> None:
    result = census()
    result["basis_controls"] = basis_controls()
    result.update(semantic_controls())
    result["invalid_controls"] = invalid_controls()
    directory = Path(__file__).resolve().parent
    hashes = {}
    for name in PACKAGE_FILES:
        source = directory / name
        require(source.stat().st_size <= 128 * 1024, "package source capacity")
        data = source.read_bytes()
        require(len(data) <= 128 * 1024, "package source capacity")
        hashes[name] = sha256(data).hexdigest()
    print(json.dumps({"result": result, "sha256": hashes}, sort_keys=True))
    print("PASS_ROUNDED_PROGRAM_AFFINE_HULL")


if __name__ == "__main__":
    main()
