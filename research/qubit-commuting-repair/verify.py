#!/usr/bin/env python3
"""Exact finite corroboration of the written qubit repair theorem; no output files."""
from dataclasses import dataclass, replace
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path
import sys


Vector = tuple[F, F, F]
Matrix = tuple[tuple[F, ...], ...]
AXES = ((F(1), F(0), F(0)), (F(0), F(1), F(0)), (F(0), F(0), F(1)))
PAULI = (
    ((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 0)),
    ((0, 0, 0, 1), (0, 0, -1, 0), (0, -1, 0, 0), (1, 0, 0, 0)),
    ((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, 1, 0), (0, 0, 0, -1)),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def transpose(a: Matrix) -> Matrix:
    return tuple(zip(*a, strict=True))


def multiply(a: Matrix, b: Matrix) -> Matrix:
    columns = transpose(b)
    return tuple(tuple(dot(row, col) for col in columns) for row in a)


def subtract(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(x - y for x, y in zip(r, s, strict=True))
                 for r, s in zip(a, b, strict=True))


def observable(v: Vector, scalar: F) -> Matrix:
    # Realification R(A) = [[Re A, -Im A], [Im A, Re A]].
    return tuple(tuple(scalar * (r == c) + sum(v[k] * PAULI[k][r][c]
                       for k in range(3)) for c in range(4)) for r in range(4))


def norm2(a: Matrix) -> F:
    # ||A||_(2,2)^2 = ||R(A)||_F^2 / 4, for arbitrary complex A.
    return sum(x * x for row in a for x in row) / 4


def cross2(a, b):
    return sum((a[i] * b[j] - a[j] * b[i]) ** 2
               for i, j in combinations(range(3), 2))


def covariance(vectors) -> Matrix:
    return tuple(tuple(sum(v[i] * v[j] for v in vectors)
                       for j in range(3)) for i in range(3))


def identity(n: int) -> Matrix:
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


@dataclass(frozen=True)
class Witness:
    vectors: tuple[Vector, Vector, Vector]
    scalars: Vector
    frame: tuple[Vector, Vector, Vector]
    eigenvalues: Vector
    repaired: tuple[Vector, Vector, Vector]
    repaired_scalars: Vector
    error2: F
    delta2: F


def witness(vectors, scalars, frame, eigenvalues) -> Witness:
    direction = frame[0]
    repaired = tuple(tuple(dot(v, direction) * x for x in direction) for v in vectors)
    return Witness(vectors, scalars, frame, eigenvalues, repaired, scalars,
                   sum(eigenvalues[1:]), 4 * sum(cross2(a, b)
                   for a, b in combinations(vectors, 2)))


def validate(case: Witness) -> None:
    require(all(len(v) == 3 for v in (*case.vectors, *case.frame, *case.repaired)),
            'vector dimensions')
    require(multiply(case.frame, transpose(case.frame)) == identity(3), 'frame')
    l1, l2, l3 = case.eigenvalues
    require(l1 >= l2 >= l3 >= 0, 'eigenvalue order')
    s = covariance(case.vectors)
    for n, eigenvalue in zip(case.frame, case.eigenvalues, strict=True):
        require(tuple(dot(row, n) for row in s) == tuple(eigenvalue * x for x in n),
                'spectral certificate')
    for v, a in zip(case.vectors, case.scalars, strict=True):
        require(abs(a) <= 1 and dot(v, v) <= (1 - abs(a)) ** 2, 'input contraction')
    for v, a in zip(case.repaired, case.repaired_scalars, strict=True):
        require(abs(a) <= 1 and dot(v, v) <= (1 - abs(a)) ** 2, 'output contraction')
    original = tuple(observable(v, a) for v, a in zip(case.vectors, case.scalars, strict=True))
    repaired = tuple(observable(v, a) for v, a in zip(case.repaired, case.repaired_scalars, strict=True))
    for a, b in combinations(repaired, 2):
        require(multiply(a, b) == multiply(b, a), 'commuting repair')
    error2 = sum(norm2(subtract(a, b)) for a, b in zip(original, repaired, strict=True))
    delta2 = sum(norm2(subtract(multiply(a, b), multiply(b, a)))
                 for a, b in combinations(original, 2))
    require(case.error2 == error2 == l2 + l3, 'optimal distance')
    require(case.delta2 == delta2 == 4 * (l1*l2 + l1*l3 + l2*l3), 'commutator norm')
    require(3 * error2 ** 2 <= delta2, 'sharp bound')
    require(delta2 - 3 * error2 ** 2 ==
            4 * (l1-l2) * (l2+l3) + (l2-l3) * (l2+3*l3), 'gap identity')
    require((3 * error2 ** 2 == delta2) == (l2 == l3 == 0 or l1 == l2 == l3),
            'equality classification')


def check_grid() -> dict:
    raw = tuple(product((-1, 0, 1), repeat=3))
    vectors = tuple(tuple(F(x, 4) for x in v) for v in raw)
    pair_checks = 0
    for a, b in product(vectors, repeat=2):
        left, right = observable(a, F(1, 4)), observable(b, F(-1, 4))
        commutator = subtract(multiply(left, right), multiply(right, left))
        require(norm2(commutator) == 4 * cross2(a, b), 'literal pair norm')
        require((commutator == tuple((F(0),)*4 for _ in range(4))) ==
                (cross2(a, b) == 0), 'literal pair commutation')
        pair_checks += 1
    triple_checks = 0
    for indices in product(range(27), repeat=3):
        vs = tuple(raw[i] for i in indices)
        s = covariance(vs)
        trace = sum(s[i][i] for i in range(3))
        trace_square = sum(s[i][j] ** 2 for i in range(3) for j in range(3))
        require(trace ** 2 - trace_square ==
                2 * sum(cross2(a, b) for a, b in combinations(vs, 2)), 'Gram identity')
        triple_checks += 1
    return {'literal_matrix_pairs': pair_checks, 'covariance_triples': triple_checks}


def frames():
    rotation = ((F(3, 5), F(-4, 5), F(0)),
                (F(4, 5), F(3, 5), F(0)), AXES[2])
    permutation = (AXES[1], AXES[2], AXES[0])
    return (AXES, rotation, permutation, multiply(rotation, permutation),
            multiply(permutation, rotation))


def check_spectra() -> tuple[dict, Witness]:
    count = 0
    equality = 0
    first = None
    for radii in combinations_with_replacement((F(0), F(1, 8), F(1, 4), F(3, 8)), 3):
        radii = tuple(reversed(radii))
        eig = tuple(x*x for x in radii)
        for q, r in product(frames(), repeat=2):
            # V = R diag(radii) Q, hence V^T V = Q^T diag(eig) Q.
            vectors = multiply(tuple(tuple(r[i][j] * radii[j] for j in range(3))
                                     for i in range(3)), q)
            for scalars in ((F(0),)*3, (F(-1, 4), F(0), F(1, 4))):
                case = witness(vectors, scalars, q, eig)
                validate(case)
                count += 1
                equality += int(case.delta2 > 0 and 3 * case.error2 ** 2 == case.delta2)
                if eig[0] > eig[1] > eig[2] > 0:
                    first = case
    require(first is not None, 'strict-spectrum fixture exists')
    return {'spectral_repairs': count, 'noncommuting_equality_fixtures': equality}, first


def check_controls(case: Witness) -> int:
    bad = (
        replace(case, eigenvalues=tuple(reversed(case.eigenvalues))),
        replace(case, frame=(case.frame[1], case.frame[0], case.frame[2])),
        replace(case, frame=(AXES[0], AXES[0], AXES[2])),
        replace(case, error2=case.error2 + 1),
        replace(case, delta2=case.delta2 / 2),
        replace(case, repaired=case.vectors),
        replace(case, scalars=(F(2), F(0), F(0))),
        replace(case, repaired_scalars=(F(2), F(0), F(0))),
        replace(case, repaired_scalars=tuple(a + F(1, 8) for a in case.scalars)),
        replace(case, repaired=tuple((F(0),)*3 for _ in range(3))),
    )
    for mutant in bad:
        try:
            validate(mutant)
        except ValueError:
            continue
        raise ValueError('a rejection control passed')
    # The tempting stronger constant 1/sqrt(2) fails on the Pauli triple.
    require(F(2) ** 2 > F(12, 4), 'false stronger constant rejects')
    return len(bad) + 1


def main() -> None:
    require(len(sys.argv) == 1, 'no command-line arguments accepted')
    counts = check_grid()
    spectra, case = check_spectra()
    counts.update(spectra)
    counts['rejection_controls'] = check_controls(case)
    sharp = witness(AXES, (F(0),)*3, AXES, (F(1),)*3)
    validate(sharp)
    require((sharp.error2, sharp.delta2) == (F(2), F(12)), 'Pauli attainer')
    counts['scaled_pauli_attainers'] = 0
    for denominator in range(1, 33):
        t = F(1, denominator)
        scaled = tuple(tuple(t * x for x in axis) for axis in AXES)
        sample = witness(scaled, (F(0),)*3, AXES, (t*t,)*3)
        validate(sample)
        require(sample.error2 ** 2 / sample.delta2 == F(1, 3), 'scale invariant ratio')
        counts['scaled_pauli_attainers'] += 1
    package = Path(__file__).resolve().parent
    names = ('README.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps({'status': 'PASS_QUBIT_COMMUTING_REPAIR', 'counts': counts,
                      'sharp_constant_fourth_power': '1/3', 'package_sha256': hashes,
                      'scope': 'Finite exact corroboration of the written dimension-two proof.'},
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
