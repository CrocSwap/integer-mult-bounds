#!/usr/bin/env python3
"""Check the two-prime completion proof on fixed exact examples."""

from itertools import combinations, product


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def powers(prime, order):
    """Sparse monomial residues modulo the prime-power cyclotomic polynomial."""
    step = order // prime
    degree = order - step
    residues = [((exponent, 1),) for exponent in range(degree)]
    for offset in range(step):
        residues.append(tuple((offset + j * step, -1) for j in range(prime - 1)))
    return degree, tuple(residues)


def evaluate(phases, bases):
    """Sum roots in the tensor product of the two integral power bases."""
    (x_degree, x_powers), (y_degree, y_powers) = bases
    coefficients = [[0] * y_degree for _ in range(x_degree)]
    for x, y in phases:
        for i, a in x_powers[x % len(x_powers)]:
            for j, b in y_powers[y % len(y_powers)]:
                coefficients[i][j] += a * b
    return tuple(map(tuple, coefficients))


def pairing(left, right, bases):
    differences = ((a - c, b - d) for (a, b), (c, d) in zip(left, right, strict=True))
    return evaluate(differences, bases)


def orthogonal_columns(matrix, bases):
    zero = evaluate((), bases)
    return all(pairing(left, right, bases) == zero
               for left, right in combinations(zip(*matrix, strict=True), 2))


def project(matrix, keep=0):
    return tuple(tuple((x, 0) if keep == 0 else (0, y) for x, y in row)
                 for row in matrix)


def normalized_column(partial, bases):
    n = len(partial)
    column = []
    for index, row in enumerate(partial):
        gram_row = pairing(row, partial[0], bases)
        coefficients = [list(-value for value in power_row) for power_row in gram_row]
        coefficients[0][0] += n if index == 0 else 0
        column.append(tuple(map(tuple, coefficients)))
    return tuple(column)


def reduce_at_q(coefficients, q):
    return tuple(sum(row) % q for row in coefficients)


def check_erasures(matrix, bases, q):
    projected = project(matrix)
    require(orthogonal_columns(matrix, bases), "mixed fixture is not orthogonal")
    require(orthogonal_columns(projected, bases), "fixture loses projected orthogonality")
    n = len(matrix)
    entries = 0
    for erased in range(n):
        partial = tuple(row[:erased] + row[erased + 1:] for row in matrix)
        column = normalized_column(partial, bases)
        projected_column = normalized_column(project(partial), bases)
        x0, y0 = matrix[0][erased]
        for index, row in enumerate(matrix):
            x, y = row[erased]
            expected = evaluate(((x - x0, y - y0),), bases)
            require(column[index] == expected, "reconstruction changed the erased phase")
            require(projected_column[index] == evaluate(((x - x0, 0),), bases),
                    "projected reconstruction changed the retained prime-power phase")
            residue = reduce_at_q(projected_column[index], q)
            require(reduce_at_q(column[index], q) == residue, "reduction mismatch")
            opposite = tuple(-value % q for value in reduce_at_q(expected, q))
            require(residue != opposite, "the opposite sign also passed reduction")
            entries += 1
    return n, entries


def mixed_fixture(p, p_power):
    """Fourier blocks with a column-block-dependent row phase."""
    indices = tuple(product(range(p), repeat=2))
    matrix = tuple(
        tuple(((p_power // p) * (r * j + s * k) + s * j, s * j)
              for j, k in indices)
        for r, s in indices
    )
    # At rows (0,0),(0,1) and columns (0,0),(1,0), the cross ratio
    # has exponent one in each component, even after row and column gauges.
    require(matrix[0][0] == matrix[0][p] == matrix[1][0] == (0, 0),
            "mixed cross-ratio normalization changed")
    require(matrix[1][p] == (1, 1), "fixture lacks a primitive mixed cross ratio")
    return matrix


def check_projection_boundaries():
    bases = powers(3, 3), powers(5, 5)
    mixed_cycles = tuple((i, 0) for i in range(3)) + tuple((0, j) for j in range(5))
    require(evaluate(mixed_cycles, bases) == evaluate((), bases),
            "the two mixed cycles must vanish together")
    collapsed = tuple((x, 0) for x, _ in mixed_cycles)
    require(evaluate(collapsed, bases) == evaluate(((0, 0),) * 5, bases),
            "the five-cycle should contribute five after projection")

    indices = tuple(product(range(3), range(5)))
    partial = tuple(tuple((r * j, s * k) for j, k in indices[:-1]) for r, s in indices)
    require(orthogonal_columns(partial, bases), "boundary partial Fourier matrix is invalid")
    zero = evaluate((), bases)
    for kept_part, discarded_phase in ((0, (0, 1)), (1, (1, 0))):
        columns = tuple(zip(*project(partial, keep=kept_part), strict=True))
        left = columns[0]
        right = columns[indices.index(discarded_phase)]
        require(pairing(left, right, bases) != zero,
                "discarded prime did not collapse two columns")


def main():
    fixtures = (
        (3, 5, 3, 5),
        (3, 5, 9, 5),
        (3, 5, 3, 25),
        (3, 5, 9, 25),
        (5, 7, 5, 7),
        (5, 3, 5, 3),
    )
    erasures = 0
    entries = 0
    for p, q, p_power, q_power in fixtures:
        bases = powers(p, p_power), powers(q, q_power)
        fixture_erasures, fixture_entries = check_erasures(mixed_fixture(p, p_power), bases, q)
        erasures += fixture_erasures
        entries += fixture_entries
    check_projection_boundaries()
    print("PASS_TWO_PRIME_COLUMN_COMPLETION")
    print(f"{len(fixtures)} mixed fixtures, {erasures} erasures, {entries} recovered entries")
    print("All opposite signs reject modulo q. Mixed-cycle and pq-row controls pass.")


if __name__ == "__main__":
    main()
