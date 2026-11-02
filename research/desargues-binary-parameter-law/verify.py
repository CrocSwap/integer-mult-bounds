#!/usr/bin/env python3
"""Exact polynomial certificate and independent GF(32) incidence checks."""

import hashlib
import itertools
import json
import platform
import sys
from pathlib import Path

type Poly = frozenset[tuple[int, int, int]]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def add(*values: Poly) -> Poly:
    result: set[tuple[int, int, int]] = set()
    for value in values:
        result.symmetric_difference_update(value)
    return frozenset(result)


def multiply(left: Poly, right: Poly) -> Poly:
    result: set[tuple[int, int, int]] = set()
    for a in left:
        for b in right:
            term = tuple(a[i] + b[i] for i in range(3))
            require(sum(term) <= 2, "polynomial capacity exceeded")
            result.symmetric_difference_update((term,))
    return frozenset(result)


def linear(mask: int) -> Poly:
    require(1 <= mask < 16, "invalid affine form")
    terms = ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    return frozenset(terms[i] for i in range(4) if mask >> i & 1)


def symbolic_vectors() -> tuple[list[list[Poly]], list[list[Poly]]]:
    z = frozenset()
    one, u, v, w = (linear(m) for m in (1, 2, 4, 8))
    points = [
        [one, z, z], [z, one, z], [z, z, one], [one, one, one],
        [u, one, z], [v, z, one], [add(one, w), one, one],
        [z, v, u], [u, add(u, w), u], [v, v, add(v, w)],
    ]
    lines = [
        [z, z, one], [z, one, z], [z, one, one],
        [one, z, z], [one, z, one], [one, one, z],
        [one, u, v], [one, u, add(one, u, w)],
        [one, add(one, v, w), v], [add(u, v, w), u, v],
    ]
    return points, lines


def incidences() -> frozenset[tuple[int, int]]:
    result = {(p, i) for i in range(3) for p in (0, i + 1, i + 4)}
    for index, (i, j) in enumerate(((0, 1), (0, 2), (1, 2))):
        for offset, line in ((1, 3 + index), (4, 6 + index)):
            result.update(((i + offset, line), (j + offset, line), (7 + index, line)))
        result.add((7 + index, 9))
    require(len(result) == 30, "incidence specification")
    require(len({frozenset(j for i, j in result if i == p) for p in range(10)}) == 10,
            "point signatures are not distinct")
    require(len({frozenset(i for i, j in result if j == l) for l in range(10)}) == 10,
            "line signatures are not distinct")
    return frozenset(result)


def polynomial_certificate(points: list, lines: list) -> dict:
    factorizations = {linear(1): ()}
    for i in range(2, 16):
        factorizations[linear(i)] = (i,)
        for j in range(i, 16):
            product = multiply(linear(i), linear(j))
            require(product not in factorizations, "ambiguous polynomial factors")
            factorizations[product] = (i, j)
    wanted = incidences()
    factors = set()
    transcript = []
    for i, point in enumerate(points):
        for j, line in enumerate(lines):
            value = add(*(multiply(point[k], line[k]) for k in range(3)))
            require((not value) == ((i, j) in wanted), "symbolic incidence mismatch")
            if value:
                require(value in factorizations, "unfactored nonincidence")
                factors.update(factorizations[value])
                transcript.append([i, j, list(factorizations[value])])
    require(factors == set(range(2, 16)), "missing affine obstruction")
    digest = hashlib.sha256(json.dumps(transcript, separators=(",", ":")).encode()).hexdigest()
    return {"incidences": len(wanted), "nonincidences": len(transcript),
            "required_nonconstant_affine_forms": len(factors), "factor_digest": digest}


def field_table(degree: int) -> list[list[int]]:
    require(degree in (4, 5), "only the two fixed verification fields are supported")
    modulus = {4: 0b10011, 5: 0b100101}[degree]
    q = 1 << degree
    table = [[0] * q for _ in range(q)]
    for a in range(q):
        for b in range(q):
            value, shifted = 0, a
            for bit in range(degree):
                if b >> bit & 1:
                    value ^= shifted
                shifted <<= 1
                if shifted & q:
                    shifted ^= modulus
            table[a][b] = value
    for a in range(1, q):
        require(sorted(table[a]) == list(range(q)), "field has a zero divisor")
    return table


def cross(a: tuple, b: tuple, table: list) -> tuple:
    return tuple(table[a[(i + 1) % 3]][b[(i + 2) % 3]] ^
                 table[a[(i + 2) % 3]][b[(i + 1) % 3]] for i in range(3))


def geometric_incidence(u: int, v: int, w: int, table: list) -> bool:
    """Construct every line and intersection afresh, without symbolic vectors."""
    origin = (1, 0, 0)
    a = ((0, 1, 0), (0, 0, 1), (1, 1, 1))
    b = ((u, 1, 0), (v, 0, 1), (1 ^ w, 1, 1))
    pairs = ((0, 1), (0, 2), (1, 2))
    sides_a = tuple(cross(a[i], a[j], table) for i, j in pairs)
    sides_b = tuple(cross(b[i], b[j], table) for i, j in pairs)
    c = tuple(cross(sides_a[i], sides_b[i], table) for i in range(3))
    points = (origin,) + a + b + c
    lines = tuple(cross(a[i], b[i], table) for i in range(3))
    lines += sides_a + sides_b + (cross(c[0], c[1], table),)
    actual = frozenset((i, j) for i, p in enumerate(points) for j, line in enumerate(lines)
                       if table[p[0]][line[0]] ^ table[p[1]][line[1]] ^ table[p[2]][line[2]] == 0)
    return actual == incidences()


def binary_rank(values: tuple[int, ...]) -> int:
    pivots = [0] * 5
    rank = 0
    for initial in values:
        value = initial
        for bit in range(4, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    rank += 1
                    break
    return rank


def finite_check() -> dict:
    table = field_table(5)
    total, exact = 0, 0
    single_relation_masks = set()
    for u, v, w in itertools.product(range(32), repeat=3):
        geometry = geometric_incidence(u, v, w, table)
        rank = binary_rank((1, u, v, w))
        require(geometry == (rank == 4), "GF(32) criterion disagreement")
        total += 1
        exact += geometry
        if rank == 3:
            zeros = [m for m in range(2, 16)
                     if ((m & 1) ^ (u if m & 2 else 0) ^
                         (v if m & 4 else 0) ^ (w if m & 8 else 0)) == 0]
            require(len(zeros) == 1 and not geometry, "single-relation control")
            single_relation_masks.add(zeros[0])
    require(total == 32 ** 3 and exact == (32 - 2) * (32 - 4) * (32 - 8), "count formula")
    require(single_relation_masks == set(range(2, 16)), "incomplete condition-deletion controls")
    require(geometric_incidence(2, 4, 8, field_table(4)), "degree-four constructor")
    return {"field_order": 32, "triples": total, "exact": exact,
            "rejected": total - exact, "condition_deletion_controls": len(single_relation_masks)}


def mutation_controls() -> int:
    points, lines = symbolic_vectors()
    bad_axis = [row[:] for row in lines]
    bad_axis[9][0] = add(bad_axis[9][0], linear(1))
    bad_points = [row[:] for row in points]
    bad_points[3][0] = frozenset()
    rejected = 0
    for p, l in ((points, bad_axis), (bad_points, lines)):
        try:
            polynomial_certificate(p, l)
        except ValueError:
            rejected += 1
    require(rejected == 2, "symbolic corruption accepted")
    try:
        field_table(3)
    except ValueError:
        rejected += 1
    require(rejected == 3, "unsupported field accepted")
    return rejected


def main() -> None:
    require(len(sys.argv) == 1, "no command-line arguments supported")
    symbolic = polynomial_certificate(*symbolic_vectors())
    finite = finite_check()
    controls = mutation_controls()
    package = Path(__file__).resolve().parent
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    for name in files:
        require((package / name).stat().st_size <= 256 * 1024, "receipt input capacity exceeded")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in files}
    print(json.dumps({"symbolic": symbolic, "finite": finite, "mutation_controls": controls,
                      "python": platform.python_version(), "files_sha256": hashes}, sort_keys=True))
    print("PASS_DESARGUES_BINARY_PARAMETER_LAW")


if __name__ == "__main__":
    main()
