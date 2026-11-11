#!/usr/bin/env python3
"""Exact corroboration for polynomial two-gap insertions. Apache-2.0."""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path

type Monomial = tuple[int, int, int, int]
type Poly = dict[Monomial, int]
type Matrix = list[list[Poly]]

ONE: Monomial = (0, 0, 0, 0)
X: Monomial = (1, 0, 0, 0)
EPS: Monomial = (0, 0, 0, 1)
WIDTH = 8


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def add(a: Poly, b: Poly) -> Poly:
    result = a.copy()
    for monomial, value in b.items():
        result[monomial] = result.get(monomial, 0) + value
        if result[monomial] == 0:
            del result[monomial]
    return result


def scale(a: Poly, coefficient: int) -> Poly:
    return {m: coefficient * value for m, value in a.items()
            if coefficient * value != 0}


def mul(a: Poly, b: Poly) -> Poly:
    result: Poly = {}
    for left, u in a.items():
        for right, v in b.items():
            monomial = tuple(left[i] + right[i] for i in range(4))
            if monomial[3] <= 1:
                result[monomial] = result.get(monomial, 0) + u * v
    return {m: value for m, value in result.items() if value}


def identity() -> Matrix:
    return [[{ONE: 1} if i == j else {} for j in range(WIDTH)]
            for i in range(WIDTH)]


def matrix_mul(a: Matrix, b: Matrix) -> Matrix:
    result = [[{} for _ in range(WIDTH)] for _ in range(WIDTH)]
    for i in range(WIDTH):
        for k in range(WIDTH):
            if a[i][k]:
                for j in range(WIDTH):
                    result[i][j] = add(result[i][j], mul(a[i][k], b[k][j]))
    return result


def gates() -> list[Matrix]:
    result = []
    for stage in range(3):
        variable = tuple(int(i == stage) for i in range(4))
        for support in ((0,), (1,), (2 + 2 * stage, 3 + 2 * stage)):
            gate = identity()
            for i in support:
                gate[i][i] = {ONE: 1, variable: 1}
            result.append(gate)
    require(len(result) == 9, "nine literal gates required")
    return result


def insertion(matrix: Matrix) -> Matrix:
    result = identity()
    for i in range(WIDTH):
        for j in range(WIDTH):
            result[i][j] = add(result[i][j], mul({EPS: 1}, matrix[i][j]))
    return result


def run_word(r: Matrix, s: Matrix) -> Matrix:
    word = gates()
    factors = [word[0], insertion(r), word[1], insertion(s), *word[2:]]
    result = identity()
    for factor in factors:
        result = matrix_mul(result, factor)
    return result


def target() -> Matrix:
    result = identity()
    for factor in gates():
        result = matrix_mul(result, factor)
    for i in range(WIDTH):
        result[i][i] = mul(result[i][i], {ONE: 1, EPS: 1})
    return result


def gap_scales() -> tuple[Matrix, Matrix]:
    """Derive each entry's two scales from the literal prefix/suffix."""
    word = gates()
    suffix = identity()
    for factor in word[2:]:
        suffix = matrix_mul(suffix, factor)
    first_right = matrix_mul(word[1], suffix)
    second_left = matrix_mul(word[0], word[1])
    a = [[mul(word[0][i][i], first_right[j][j])
          for j in range(WIDTH)] for i in range(WIDTH)]
    b = [[mul(second_left[i][i], suffix[j][j])
          for j in range(WIDTH)] for i in range(WIDTH)]
    return a, b


def reduce_mod(poly: Poly, prime: int) -> Poly:
    return {m: c % prime for m, c in poly.items() if c % prime}


def column_rank(columns: list[Poly], prime: int) -> int:
    basis: dict[Monomial, Poly] = {}
    for column in columns:
        remaining = reduce_mod(column, prime)
        for _ in range(len(columns) + 1):
            if not remaining:
                break
            pivot = min(remaining)
            if pivot not in basis:
                inverse = pow(remaining[pivot], -1, prime)
                basis[pivot] = reduce_mod(scale(remaining, inverse), prime)
                break
            multiple = scale(basis[pivot], -remaining[pivot])
            remaining = reduce_mod(add(remaining, multiple), prime)
        else:
            raise ValueError("column elimination exceeded its finite bound")
    return len(basis)


def check_dimensions(a: Matrix, b: Matrix) -> list[dict[str, int]]:
    records = []
    for prime, degree in product((2, 3, 5, 7), range(1, 5)):
        rank = 0
        for i, j in product(range(WIDTH), repeat=2):
            columns = [mul(factor, {(power, 0, 0, 0): 1})
                       for factor in (a[i][j], b[i][j])
                       for power in range(degree + 1)]
            rank += column_rank(columns, prime)
        dimension = 128 * (degree + 1) - rank
        require(dimension == 64 * degree + 50, "wrong affine dimension")
        records.append({"prime": prime, "degree": degree,
                        "rank": rank, "dimension": dimension})
    return records


def all_polynomials(prime: int, degree: int) -> list[Poly]:
    return [{(power, 0, 0, 0): value
             for power, value in enumerate(coefficients) if value}
            for coefficients in product(range(prime), repeat=degree + 1)]


def predicted_pair(r: Poly, s: Poly, i: int, j: int, prime: int) -> bool:
    t = {ONE: 1, X: 1}
    if i == j:
        difference = add(add(r, s), {ONE: -1})
    elif i == 1:
        difference = add(r, mul(t, s))
    elif j == 1:
        difference = add(mul(t, r), s)
    else:
        difference = add(r, s)
    return not reduce_mod(difference, prime)


def check_entry_pairs(a: Matrix, b: Matrix) -> int:
    examined = 0
    for prime, degree in ((2, 1), (2, 2), (3, 1), (3, 2)):
        polynomials = all_polynomials(prime, degree)
        total_solutions = 1
        for i, j in product(range(WIDTH), repeat=2):
            hits = 0
            for r, s in product(polynomials, repeat=2):
                lhs = add(mul(a[i][j], r), mul(b[i][j], s))
                rhs = a[i][i] if i == j else {}
                actual = not reduce_mod(add(lhs, scale(rhs, -1)), prime)
                require(actual == predicted_pair(r, s, i, j, prime),
                        "entry criterion disagrees with literal gap scales")
                hits += int(actual)
                examined += 1
            total_solutions *= hits
        require(total_solutions == prime ** (64 * degree + 50),
                "Cartesian product of enumerated entry solutions disagrees")
    return examined


def zero_matrix() -> Matrix:
    return [[{} for _ in range(WIDTH)] for _ in range(WIDTH)]


def check_witnesses() -> tuple[int, int]:
    expected = target()
    require(run_word(identity(), zero_matrix()) == expected,
            "affine origin is not a solution")
    successes = 0
    for other in (0, 2, 3, 4, 5, 6, 7):
        for power in range(4):
            p = {(power, 0, 0, 0): 1}
            t_p = mul({ONE: 1, X: 1}, p)
            for row_crossing in (False, True):
                r, s = identity(), zero_matrix()
                if row_crossing:
                    r[1][other], s[1][other] = scale(t_p, -1), p
                else:
                    r[other][1], s[other][1] = p, scale(t_p, -1)
                require(run_word(r, s) == expected,
                        "polynomial crossing witness fails over the integers")
                successes += 1
    r, s = identity(), zero_matrix()
    controls = []
    r[1][0], s[1][0] = {ONE: -1}, {ONE: 1, X: 1}
    controls.append(run_word(r, s) != expected)
    s[1][0] = {ONE: 1}
    controls.append(run_word(r, s) != expected)
    r[1][0], s[1][0] = {ONE: -1, X: -1}, {}
    controls.append(run_word(r, s) != expected)
    controls.append(run_word(identity(), identity()) != expected)
    require(all(controls), "a false witness passed")
    return successes, len(controls)


def main() -> None:
    a, b = gap_scales()
    dimensions = check_dimensions(a, b)
    examined = check_entry_pairs(a, b)
    witnesses, controls = check_witnesses()
    package = Path(__file__).resolve().parent
    files = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    receipt = {"dimensions": dimensions, "entry_pairs_examined": examined,
               "integer_crossing_witnesses": witnesses,
               "false_witnesses_rejected": controls,
               "sha256": {name: sha256((package / name).read_bytes()).hexdigest()
                          for name in files}}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_POLYNOMIAL_TWO_GAP_INSERTIONS")


if __name__ == "__main__":
    main()
