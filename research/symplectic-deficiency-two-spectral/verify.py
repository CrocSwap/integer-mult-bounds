#!/usr/bin/env python3
"""Exact finite controls for the written deficiency-two completion theorem."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
from fractions import Fraction
from pathlib import Path

Vector = tuple[int, ...]
Line = frozenset[Vector]


def point(vector: Vector, prime: int) -> Vector:
    first = next(entry for entry in vector if entry)
    inverse = pow(first, -1, prime)
    return tuple(entry * inverse % prime for entry in vector)


def pairing(left: Vector, right: Vector, prime: int, split: bool) -> int:
    if split:
        value = left[0] * right[1] - left[1] * right[0]
        value -= left[2] * right[3] - left[3] * right[2]
    else:
        value = sum(left[i] * right[i + 2] - left[i + 2] * right[i]
                    for i in range(2))
    return value % prime


def projective_points(prime: int) -> list[Vector]:
    assert prime in (3, 5)
    vectors = itertools.product(range(prime), repeat=4)
    return sorted({point(v, prime) for v in vectors if any(v)})


def line_span(left: Vector, right: Vector, prime: int) -> Line:
    vectors = (tuple((a * x + b * y) % prime for x, y in zip(left, right))
               for a, b in itertools.product(range(prime), repeat=2))
    return frozenset(point(v, prime) for v in vectors if any(v))


def lagrangians(points: list[Vector], prime: int, split: bool) -> set[Line]:
    lines = {line_span(u, v, prime) for u, v in itertools.combinations(points, 2)
             if pairing(u, v, prime, split) == 0}
    assert all(len(line) == prime + 1 for line in lines)
    return lines


def graph_line(matrix: tuple[int, ...], prime: int) -> Line:
    a, b, c, d = matrix
    return frozenset(point((x, y, (a * x + b * y) % prime,
                           (c * x + d * y) % prime), prime)
                     for x, y in itertools.product(range(prime), repeat=2)
                     if x or y)


def field_puncture(prime: int) -> list[Line]:
    squares = {x * x % prime for x in range(1, prime)}
    nonsquare = next(x for x in range(1, prime) if x not in squares)
    return [graph_line((a, b, b, nonsquare * a % prime), prime)
            for a, b in itertools.product(range(prime), repeat=2) if a or b]


def matrix_product(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(left[2 * i + t] * right[2 * t + j] for t in range(2)) % 3
                 for i, j in itertools.product(range(2), repeat=2))


def quaternion_partial() -> list[Line]:
    identity, first, second = (1, 0, 0, 1), (0, 1, 2, 0), (1, 1, 1, 2)
    matrices = [tuple(sign * x % 3 for x in matrix)
                for matrix in (identity, first, second, matrix_product(first, second))
                for sign in (1, -1)]
    assert len(set(matrices)) == 8
    return [graph_line(matrix, 3) for matrix in matrices]


def hole_graph(points: list[Vector], lines: list[Line], prime: int,
               split: bool) -> tuple[list[Vector], list[list[int]]]:
    if len(lines) != prime * prime - 1 or len(set(lines)) != len(lines):
        raise ValueError("wrong partial-spread size or repeated line")
    covered: set[Vector] = set()
    for line in lines:
        if len(line) != prime + 1 or not line.issubset(points):
            raise ValueError("invalid projective line")
        if any(pairing(u, v, prime, split) for u, v in itertools.combinations(line, 2)):
            raise ValueError("nonisotropic line")
        if covered.intersection(line):
            raise ValueError("intersecting old lines")
        covered.update(line)
    holes = sorted(set(points) - covered)
    adjacency = [[int(pairing(u, v, prime, split) != 0) for v in holes] for u in holes]
    assert len(holes) == 2 * (prime + 1)
    assert all(sum(row) == prime for row in adjacency)
    return holes, adjacency


def exact_kernel(matrix: list[list[int]]) -> tuple[int, int, list[list[Fraction]]]:
    size = len(matrix)
    assert 1 <= size <= 16 and all(len(row) == size for row in matrix)
    rows = [[Fraction(x) for x in row] for row in matrix]
    pivots: list[int] = []
    determinant = Fraction(1)
    for column in range(size):
        rank = len(pivots)
        pivot = next((i for i in range(rank, size) if rows[i][column]), None)
        if pivot is None:
            continue
        if pivot != rank:
            rows[pivot], rows[rank] = rows[rank], rows[pivot]
            determinant = -determinant
        divisor = rows[rank][column]
        determinant *= divisor
        rows[rank] = [x / divisor for x in rows[rank]]
        for i in range(size):
            if i != rank and rows[i][column]:
                coefficient = rows[i][column]
                rows[i] = [x - coefficient * y for x, y in zip(rows[i], rows[rank])]
        pivots.append(column)
    basis = []
    for free in sorted(set(range(size)) - set(pivots)):
        vector = [Fraction(int(i == free)) for i in range(size)]
        for row, pivot in enumerate(pivots):
            vector[pivot] = -rows[row][free]
        assert all(sum(x * y for x, y in zip(row, vector)) == 0 for row in matrix)
        basis.append(vector)
    assert determinant.denominator == 1
    return len(pivots), int(determinant) if len(pivots) == size else 0, basis


def signless(adjacency: list[list[int]]) -> list[list[int]]:
    size = len(adjacency)
    assert all(adjacency[i][i] == 0 for i in range(size))
    assert all(adjacency[i][j] == adjacency[j][i]
               for i, j in itertools.product(range(size), repeat=2))
    return [[entry + (sum(row) if i == j else 0) for j, entry in enumerate(row)]
            for i, row in enumerate(adjacency)]


def fixture(prime: int, split: bool, lines: list[Line], completable: bool) -> dict:
    points = projective_points(prime)
    inventory = lagrangians(points, prime, split)
    assert len(inventory) == (prime + 1) * (prime * prime + 1)
    assert set(lines).issubset(inventory)
    holes, adjacency = hole_graph(points, lines, prime, split)
    rank, determinant, basis = exact_kernel(signless(adjacency))
    candidates = {line for line in inventory if line.issubset(holes)}
    extensions = [pair for pair in itertools.combinations(candidates, 2)
                  if pair[0].isdisjoint(pair[1])]
    assert len(extensions) == int(completable)
    assert (determinant == 0) == completable
    assert len(basis) == int(completable)
    if completable:
        normalized = [x / basis[0][0] for x in basis[0]]
        assert set(normalized) == {Fraction(-1), Fraction(1)}
        recovered = {frozenset(h for h, x in zip(holes, normalized) if x == sign)
                     for sign in (-1, 1)}
        assert recovered == set(extensions[0])
    else:
        assert determinant > 0 and not candidates
    try:
        hole_graph(points, lines[:-1] + [lines[0]], prime, split)
    except ValueError as error:
        assert "repeated" in str(error)
    else:
        raise AssertionError("duplicate-line mutation was accepted")
    return {"q": prime, "form": "split" if split else "standard",
            "old_lines": len(lines), "holes": len(holes), "degree": prime,
            "enumerated_lagrangians": len(inventory), "completion_pairs": len(extensions),
            "signless_rank": rank, "signless_determinant": determinant}


def component_bound_control() -> dict:
    # C4 disjoint union K3 is regular with N=3k+1. Its Q is singular,
    # although the full graph is not bipartite. The strict size gate matters.
    edges = {(0, 1), (1, 2), (2, 3), (0, 3), (4, 5), (4, 6), (5, 6)}
    adjacency = [[int((min(i, j), max(i, j)) in edges) for j in range(7)]
                 for i in range(7)]
    assert all(sum(row) == 2 for row in adjacency)
    rank, determinant, basis = exact_kernel(signless(adjacency))
    assert rank == 6 and determinant == 0 and len(basis) == 1
    assert basis[0][4:] == [0, 0, 0]
    return {"vertices": 7, "degree": 2, "rank": rank,
            "scope": "abstract graph control, not a symplectic-spread example"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = {"status": "PASS_SYMPLECTIC_DEFICIENCY_TWO_SPECTRAL",
              "fixtures": [fixture(3, False, field_puncture(3), True),
                           fixture(3, True, quaternion_partial(), False),
                           fixture(5, False, field_puncture(5), True)],
              "component_bound_control": component_bound_control(),
              "scope": "finite exact controls; the all-dimension theorem is a written proof"}
    if args.receipt is not None:
        package = Path(__file__).resolve().parent
        destination = args.receipt.resolve()
        if destination.is_relative_to(package.parents[1]):
            raise ValueError("receipt must be outside the checkout")
        receipt = {"result": result, "python": platform.python_version(),
                   "sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in sorted(package.iterdir()) if path.is_file()}}
        destination.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
