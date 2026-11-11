"""Check the new coefficient contract; never execute predecessor code."""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product as cartesian
from math import isqrt
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from algebra import (C, V, M, ZERO, ONE, MAX_DIM, MAX_SQUARE_SUM, add, adj,
                     conj, construct, dot, matrix_sum, mul, neg, norm2,
                     outer, product, scale, square_pairs, validate, zero_matrix)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArithmeticError(message)


def rank(a: M) -> int:
    """Independent row elimination, not the column residual constructor."""
    rows = [list(row) for row in a]
    pivot_row = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(pivot_row, len(rows)) if rows[i][j] != ZERO), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        value = rows[pivot_row][j]
        inverse = scale(conj(value), 1/norm2((value,)))
        rows[pivot_row] = [mul(x, inverse) for x in rows[pivot_row]]
        for i in range(len(rows)):
            if i != pivot_row:
                factor = rows[i][j]
                rows[i] = [add(x, neg(mul(factor, y)))
                           for x, y in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def positive_semidefinite(a: M) -> bool:
    """Exact Hermitian Schur criterion, including singular zero pivots."""
    if a != adj(a):
        return False
    h = [list(row) for row in a]
    for k in range(len(a)):
        pivot = h[k][k]
        if pivot[1] or pivot[0] < 0:
            return False
        if pivot == ZERO:
            if any(h[k][j] != ZERO for j in range(k+1, len(a))):
                return False
        else:
            for i in range(k+1, len(a)):
                for j in range(k+1, len(a)):
                    correction = scale(mul(h[i][k], h[k][j]), 1/pivot[0])
                    h[i][j] = add(h[i][j], neg(correction))
    return True


def contract(a: M, columns: tuple[V, ...], rows: tuple[V, ...]) -> dict:
    validate(a)
    r = rank(a)
    require(r <= len(columns) <= 2*r and len(columns) == len(rows), "term count")
    projection = zero_matrix(len(a), len(a))
    rebuilt = zero_matrix(len(a), len(a[0]))
    gram = product(adj(a), a)
    for g, row in zip(columns, rows):
        require(len(g) == len(a) and len(row) == len(a[0]), "factor shape")
        require(0 < norm2(g) <= 1, "column norm")
        require(row == tuple(dot(g, tuple(c)) for c in zip(*a)), "adjoint row")
        projection = matrix_sum(projection, outer(g))
        term = tuple(tuple(mul(x, y) for y in row) for x in g)
        rebuilt = matrix_sum(rebuilt, term)
        row_gram = outer(tuple(conj(x) for x in row))
        difference = matrix_sum(gram, tuple(tuple(neg(x) for x in rr) for rr in row_gram))
        require(positive_semidefinite(difference), "row contraction")
    require(rebuilt == a, "reconstruction")
    require(projection == adj(projection), "Hermitian projection")
    require(product(projection, projection) == projection, "Parseval projection")
    require(product(projection, a) == a and rank(projection) == r, "column-space projection")
    return {"rank": r, "terms": len(rows), "split_surplus": len(rows)-r}


def real(value) -> C:
    return Q(value), Q(0)


def fixtures() -> tuple[M, ...]:
    result = []
    for alphabet in [(real(-1), ZERO, ONE), (ZERO, ONE, (Q(0), Q(1)), (Q(1), Q(1)))]:
        for values in cartesian(alphabet, repeat=4):
            result.append((tuple(values[:2]), tuple(values[2:])))
    for m in range(1, 6):
        for n in range(1, 6):
            for denominator in (1, 3):
                result.append(tuple(tuple(real(Q((i+1)*(j%2+1), denominator))
                                          for j in range(n)) for i in range(m)))
    basis = ((real(1), real(1), real(1)),
             (real(1), real(-1), ZERO),
             (real(1), real(1), real(-2)))
    for exponent in (0, 3, 120):
        for shift in range(8):
            a = tuple(tuple(add(scale(basis[j][i], Q(1, 2**exponent) if j == 2 else Q(1)),
                                scale(basis[0][i], Q(shift) if j else Q(0)))
                            for j in range(3)) for i in range(3))
            result.append(a)
    result.extend((zero_matrix(1, 1), zero_matrix(3, 5),
                   ((ONE, ZERO), (ONE, ZERO), (ONE, ZERO))))
    return tuple(result)


def controls() -> int:
    caught = 0
    invalid = [(), ((ONE,), (ONE, ZERO)), ((1.0,),),
               tuple((ONE,) for _ in range(MAX_DIM+1)),
               (((Q(1, 2**300), Q(0)),),)]
    for matrix in invalid:
        try:
            construct(matrix)
        except ValueError:
            caught += 1
        else:
            raise ArithmeticError("invalid matrix accepted")
    invalid.append(((ONE,), ((Q(256), Q(0)),)))
    try:
        construct(invalid[-1])
    except ValueError:
        caught += 1
    else:
        raise ArithmeticError("residual capacity accepted")
    for value in (0, -1, MAX_SQUARE_SUM+1, True):
        try:
            square_pairs(value)
        except ValueError:
            caught += 1
        else:
            raise ArithmeticError("invalid square capacity accepted")
    a = ((ONE,), (ONE,), (ONE,))
    columns, rows, _ = construct(a)
    faults = [(columns[:1], rows[:1]),
              (columns, tuple(tuple(conj(x) for x in row) for row in rows)),
              (tuple(tuple(scale(x, Q(2)) for x in col) for col in columns), rows),
              (columns, tuple(tuple(scale(x, Q(3)) for x in row) for row in rows))]
    for cols, rr in faults:
        try:
            contract(a, cols, rr)
        except ArithmeticError:
            caught += 1
        else:
            raise ArithmeticError("semantic fault accepted")
    for bad in [((real(-1),),), ((ZERO, ONE), (ONE, ZERO)),
                ((ONE, (Q(0), Q(1))), (ZERO, ONE))]:
        require(not positive_semidefinite(bad), "PSD negative control")
        caught += 1
    require(positive_semidefinite(((ZERO, ZERO), (ZERO, ONE))), "PSD singular control")
    require(square_pairs(MAX_SQUARE_SUM) == (256, 0, 0, 0), "capacity endpoint")
    return caught


def run() -> dict:
    four_square_cases = 0
    for n in range(1, 2049):
        a, b, c, d = square_pairs(n)
        require(a*a+b*b+c*c+d*d == n, "four-square identity")
        one_term_possible = any(x*x+y*y == n for x in range(isqrt(n)+1)
                                for y in range(isqrt(n)+1))
        require((c == d == 0) == one_term_possible, "two-square preference")
        four_square_cases += 1
    stats = [contract(a, *construct(a)[:2]) for a in fixtures()]
    example = ((ONE,), (ONE,), (ONE,))
    columns, rows, _ = construct(example)
    require(len(columns) == 2, "rank-one exact-unit two-term witness")
    require(sum(norm2(g) for g in columns) == 1, "rank-one Parseval trace")
    result = {"status": "PASS_EXACT_UNIT_STEIN_SPLITTING",
              "four_square_cases": four_square_cases,
              "matrix_cases": len(stats),
              "total_rank": sum(s["rank"] for s in stats),
              "total_terms": sum(s["terms"] for s in stats),
              "cases_using_extra_terms": sum(s["split_surplus"] > 0 for s in stats),
              "rejection_controls": controls(),
              "example_column_norms_squared": [str(norm2(g)) for g in columns],
              "example_row_norms_squared": [str(norm2(row)) for row in rows]}
    names = ("algebra.py", "verify.py", "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json")
    result["source_sha256"] = {name: sha256((PACKAGE/name).read_bytes()).hexdigest() for name in names}
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = run()
    rendered = json.dumps(result, sort_keys=True, indent=2)+"\n"
    if args.receipt:
        with args.receipt.open("x", encoding="utf-8") as output:
            require(output.write(rendered) == len(rendered), "receipt write")
    print(rendered, end="")


if __name__ == "__main__":
    main()
