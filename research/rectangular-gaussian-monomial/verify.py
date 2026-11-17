#!/usr/bin/env python3
"""Check the rectangular Gaussian classification on small exact rational blocks."""

from fractions import Fraction
from itertools import permutations, product
from math import prod
from typing import NamedTuple

Point = tuple[int, ...]
Order = tuple[int, ...]
Weights = tuple[Fraction, ...]
Table = tuple[Weights, ...]


class Axis(NamedTuple):
    base: int
    row_step: int
    column_step: int
    row_origin: int
    column_origin: int


class Fixture(NamedTuple):
    name: str
    row_shape: Point
    column_shape: Point
    axes: tuple[Axis, ...]
    expected_pairs: int
    exhaustive: bool = True


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def gaussian(fixture: Fixture, rows: tuple[Point, ...], columns: tuple[Point, ...]) -> Table:
    def entry(x: Point, y: Point) -> Fraction:
        value = Fraction(1)
        for a, b, axis in zip(x, y, fixture.axes, strict=True):
            row_coordinate = axis.row_origin + axis.row_step * a
            column_coordinate = axis.column_origin + axis.column_step * b
            value *= Fraction(1, axis.base**2) ** (row_coordinate - column_coordinate)**2
        return value

    return tuple(
        tuple(Fraction((-1)**(i + j) * (i + 2), j + 3) * entry(x, y)
              for j, y in enumerate(columns))
        for i, x in enumerate(rows)
    )


def centered_core(
    fixture: Fixture, rows: tuple[Point, ...], columns: tuple[Point, ...],
) -> Table:
    return tuple(
        tuple(prod(
            Fraction(axis.base) ** (
                axis.row_step * axis.column_step *
                (2 * a - m + 1) * (2 * b - n + 1)
            )
            for a, b, m, n, axis in zip(
                x, y, fixture.row_shape, fixture.column_shape, fixture.axes, strict=True,
            )
        ) for y in columns)
        for x in rows
    )


def coordinate_order(
    points: tuple[Point, ...], shape: Point, directions: Order, signs: Point,
) -> Order:
    indices = {point: index for index, point in enumerate(points)}
    result = []
    for point in points:
        image = [0] * len(shape)
        for source, target in enumerate(directions):
            value = point[source]
            image[target] = value if signs[source] == 1 else shape[target] - 1 - value
        result.append(indices[tuple(image)])
    return tuple(result)


def predicted_pairs(
    fixture: Fixture, rows: tuple[Point, ...], columns: tuple[Point, ...],
) -> set[tuple[Order, Order]]:
    weights = tuple(axis.base ** (axis.row_step * axis.column_step) for axis in fixture.axes)
    signatures = tuple(zip(fixture.row_shape, fixture.column_shape, weights, strict=True))
    dimension = len(signatures)
    return {
        (coordinate_order(rows, fixture.row_shape, directions, signs),
         coordinate_order(columns, fixture.column_shape, directions, signs))
        for directions in permutations(range(dimension))
        if all(signatures[i] == signatures[j] for i, j in enumerate(directions))
        for signs in product((-1, 1), repeat=dimension)
    }


def endpoint_holds(
    table: Table, p: Order, q: Order, u: Weights, v: Weights,
) -> bool:
    return all(
        u[i] * row[j] == table[p[i]][q[j]] * v[j]
        for i, row in enumerate(table)
        for j in range(len(q))
    )


def pivot_weights(table: Table, p: Order, q: Order) -> tuple[Weights, Weights]:
    # Solve UG=GV at column zero and at row p(0), normalizing v[0] to one.
    u = tuple(table[k][q[0]] / table[i][0] for i, k in enumerate(p))
    v = tuple(u[0] * table[0][j] / table[p[0]][k] for j, k in enumerate(q))
    return u, v


def exhaustive_pairs(table: Table) -> tuple[set[tuple[Order, Order]], int]:
    require(len(table) <= 4 and len(table[0]) <= 6, "exhaustive fixture exceeds 4 by 6")
    matches = set()
    checked = 0
    for p, q in product(permutations(range(len(table))), permutations(range(len(table[0])))):
        checked += 1
        if endpoint_holds(table, p, q, *pivot_weights(table, p, q)):
            matches.add((p, q))
    return matches, checked


def check_fixture(fixture: Fixture) -> tuple[int, int, int]:
    rows = tuple(product(*(range(m) for m in fixture.row_shape)))
    columns = tuple(product(*(range(n) for n in fixture.column_shape)))
    table = gaussian(fixture, rows, columns)
    core = centered_core(fixture, rows, columns)
    row_gauge = tuple(row[0] / central[0] for row, central in zip(table, core, strict=True))
    col_gauge = tuple(value / (row_gauge[0] * middle)
                      for value, middle in zip(table[0], core[0], strict=True))
    require(all(
        table[i][j] == row_gauge[i] * core[i][j] * col_gauge[j]
        for i in range(len(rows)) for j in range(len(columns))
    ), f"{fixture.name}: centered factorization")

    pairs = predicted_pairs(fixture, rows, columns)
    require(len(pairs) == fixture.expected_pairs, f"{fixture.name}: number of predicted pairs")
    checked = 0
    if fixture.exhaustive:
        found, checked = exhaustive_pairs(table)
        require(found == pairs, f"{fixture.name}: exhaustive endpoint search disagrees")

    scalar = Fraction(-7, 3)
    for p, q in pairs:
        u = tuple(scalar * row_gauge[k] / row_gauge[i] for i, k in enumerate(p))
        v = tuple(scalar * col_gauge[j] / col_gauge[k] for j, k in enumerate(q))
        require(endpoint_holds(table, p, q, u, v), f"{fixture.name}: gauge lift")
        pivot_u, pivot_v = pivot_weights(table, p, q)
        require(
            u == tuple(v[0] * value for value in pivot_u)
            and v == tuple(v[0] * value for value in pivot_v),
            f"{fixture.name}: scalar-normalized lift",
        )
    print(f"{fixture.name}: pairs={len(pairs)} exhaustive_candidates={checked}")
    return len(pairs), checked, len(pairs) * len(rows) * len(columns)


def check_controls() -> None:
    fixture = Fixture("controls", (2,), (3,), (Axis(2, 2, 1, -1, 2),), 2)
    table = gaussian(fixture, ((0,), (1,)), ((0,), (1,), (2,)))
    p, q = (1, 0), (2, 1, 0)
    identity_columns = (0, 1, 2)
    require(
        not endpoint_holds(table, p, identity_columns, *pivot_weights(table, p, identity_columns)),
        "a row-only reflection must fail",
    )
    require(
        not endpoint_holds(table, p, q, (Fraction(1),) * 2, (Fraction(1),) * 3),
        "the ungauged permutation lifts must fail",
    )
    u, v = pivot_weights(table, p, q)
    require(
        not endpoint_holds(table, p, q, (2 * u[0], u[1]), v),
        "a change to just one monomial weight must fail",
    )

    constant = ((Fraction(1),) * 3,) * 2
    require(
        endpoint_holds(constant, p, identity_columns, *pivot_weights(constant, p, identity_columns)),
        "a zero effective weight permits independent reflections",
    )


def main() -> None:
    axis = Axis(2, 1, 1, 0, 0)
    fixtures = (
        Fixture("one_axis", (2,), (3,), (Axis(2, 2, 1, -1, 2),), 2),
        Fixture("unequal_column_lengths", (2, 2), (2, 3), (axis, axis), 4),
        Fixture("distinct_effective_weights", (2, 2), (2, 2), (axis, Axis(3, 1, 1, 1, 0)), 4),
        Fixture("equal_effective_weights", (2, 2), (2, 2),
                (Axis(2, 2, 1, 0, 1), Axis(4, 1, 1, 2, -1)), 8),
        Fixture("rectangular_with_axis_exchange", (2, 2, 2), (2, 2, 3),
                (Axis(2, 2, 1, 0, 1), Axis(4, 1, 1, 2, -1), Axis(3, 1, 1, 0, 0)), 16, False),
    )
    counts = tuple(check_fixture(fixture) for fixture in fixtures)
    pairs, candidates, entries = (sum(values) for values in zip(*counts, strict=True))
    check_controls()
    print(f"pairs={pairs} exhaustive_candidates={candidates} lifted_entries={entries} controls=4")
    print("PASS_RECTANGULAR_GAUSSIAN_MONOMIAL")


if __name__ == "__main__":
    main()
