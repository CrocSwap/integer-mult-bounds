#!/usr/bin/env python3
"""Independent finite corroboration by literal polynomial execution.

No imports from the primary verifier or predecessor programs, no closed power
sum or node-weight formula, and no floating point.  The universal statement is
the written proof; these finite checks cover implementation and scope failures.
Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""

from fractions import Fraction
from math import isqrt


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(left, right, scale=1):
    result = dict(left)
    for exponent, value in right.items():
        result[exponent] = result.get(exponent, 0) + scale * value
        if result[exponent] == 0:
            del result[exponent]
    return result


def multiply(left, right):
    result = {}
    for p, x in left.items():
        for q, y in right.items():
            exponent = tuple(a + b for a, b in zip(p, q))
            result[exponent] = result.get(exponent, 0) + x * y
    return {p: value for p, value in result.items() if value}


def cube(poly):
    return multiply(multiply(poly, poly), poly)


A = {(1, 0, 0): 1}
B = {(0, 1, 0): 1}
Y = {(0, 0, 1): 1}
CUBIC_EXPONENTS = ((3, 0, 0), (2, 1, 0), (1, 2, 0), (0, 3, 0))


def child_prefix(r):
    """Execute every retained child, with formal dirty input Y."""
    a, y = dict(A), dict(Y)
    for _ in range(r):
        y = add(y, cube(a))
        a = add(a, B)
    return a, dict(B), y


def repair_program(r, d, e):
    # Visit e, d, 0 so the last query is already at the restored source.
    return [
        ("shear", e - r), ("query", -Fraction(r, 2)),
        ("shear", d - e), ("query", -Fraction(r, 2)),
        ("shear", -d), ("query", Fraction(r)),
    ]


def execute(state, program):
    a, b, y = state
    for op, value in program:
        if op == "shear":
            a = add(a, b, value)
        elif op == "query":
            y = add(y, cube(a), value)
        else:
            raise ValueError("unknown operation")
    return a, b, y


def expected(r):
    return A, B, add(Y, cube(A), r)


def pell_terms(count):
    r, n = 1, 0
    result = []
    for _ in range(count):
        r, n = 2 * r + 3 * n, r + 2 * n
        result.append((r, n))
    return result


def directions(r, n):
    require(r >= 3 and n > 0 and r * r - 3 * n * n == 1,
            "outside nondegenerate positive Pell domain")
    d, e = Fraction(r - 1 - n, 2), Fraction(r - 1 + n, 2)
    require(d.denominator == e.denominator == 1 and 0 < d < e < r,
            "nonintegral or collapsed direction")
    return int(d), int(e)


def cube_vector(u, denominator=1):
    # denominator^3 times (A + (u/denominator)B)^3, from multiplication.
    poly = cube(add({p: denominator * v for p, v in A.items()}, B, u))
    return tuple(poly.get(p, 0) for p in CUBIC_EXPONENTS)


def direct_defect_vectors(limit):
    """Build defects by adding each actual child, never power-sum formulas."""
    running = (0, 0, 0, 0)
    constant = cube_vector(0)
    result = {}
    for r in range(1, limit + 1):
        term = cube_vector(r - 1)
        running = tuple(x + y for x, y in zip(running, term))
        result[r] = tuple(x - r * c for x, c in zip(running, constant))
    return result


def grid_check(limit, denominator):
    """All 0 <= d < e <= r on the declared fixed-denominator grid."""
    defects = direct_defect_vectors(limit)
    tested, accepted = 0, []
    for r in range(3, limit + 1):
        vectors = [cube_vector(u, denominator)
                   for u in range(denominator * r + 1)]
        target = tuple(2 * denominator**3 * x for x in defects[r])
        for u, left in enumerate(vectors):
            for v in range(u + 1, len(vectors)):
                right = vectors[v]
                tested += 1
                actual = tuple(r * (x + y - 2 * c)
                               for x, y, c in zip(left, right, vectors[0]))
                if actual == target:
                    accepted.append((r, Fraction(u, denominator),
                                     Fraction(v, denominator)))
    expected_hits = []
    # This membership calculation neither generates nor filters the search.
    for r in range(3, limit + 1):
        quotient, remainder = divmod(r * r - 1, 3)
        n = isqrt(quotient)
        if remainder == 0 and n * n == quotient:
            expected_hits.append((r, *directions(r, n)))
    require(accepted == expected_hits, "grid disagrees with Pell membership")
    return tested, len(accepted)


def numeric_execution(r, program, initial):
    a, b, y = map(Fraction, initial)
    for _ in range(r):
        y += a**3
        a += b
    for op, value in program:
        if op == "shear":
            a += value * b
        else:
            y += value * a**3
    aa, bb, yy = map(Fraction, initial)
    require((a, b, y) == (aa, bb, yy + r * aa**3),
            "dirty numerical restoration failed")


def main():
    terms = pell_terms(32)
    require(terms[:4] == [(2, 1), (7, 4), (26, 15), (97, 56)],
            "Pell recurrence anchors")
    descent_steps = 0
    for k, (r, n) in enumerate(terms, 1):
        require(r * r - 3 * n * n == 1, "Pell norm")
        rr, nn = r, n
        for _ in range(k):
            old = rr
            rr, nn = 2 * rr - 3 * nn, 2 * nn - rr
            require(0 < rr < old and nn >= 0, "positive strict descent")
            require(rr * rr - 3 * nn * nn == 1, "descent norm")
            descent_steps += 1
        require((rr, nn) == (1, 0), "descent terminal")

    polynomial_programs = 0
    for r, n in terms[1:8]:  # 7, 26, 97, 362, 1351, 5042, 18817.
        d, e = directions(r, n)
        program = repair_program(r, d, e)
        require(execute(child_prefix(r), program) == expected(r),
                "literal polynomial program failed")
        polynomial_programs += 1

    inputs = [(0, 0, 13), (1, 0, -7), (0, 1, 5), (-2, 3, 11),
              (3, -2, -17), (Fraction(1, 2), Fraction(-3, 4), Fraction(5, 7)),
              (Fraction(-7, 3), Fraction(2, 5), Fraction(-11, 13)),
              (19, 23, -29)]
    dirty_cases = 0
    for r, n in terms[1:6]:
        for initial in inputs:
            numeric_execution(r, repair_program(r, *directions(r, n)), initial)
            dirty_cases += 1

    counts = [grid_check(160, 1), grid_check(32, 8)]

    r, n = 7, 4
    valid = repair_program(r, *directions(r, n))
    mutants = []
    for index, delta in ((1, 1), (0, 1)):
        changed = list(valid)
        op, value = changed[index]
        changed[index] = op, value + delta
        mutants.append(changed)
    changed = list(valid)
    changed[1] = "query", -changed[1][1]
    mutants.append(changed)
    changed = list(valid)
    changed[0], changed[1] = changed[1], changed[0]
    mutants.append(changed)
    mutants.extend([valid[:4] + valid[5:], valid[:-1]])
    for changed in mutants:
        require(execute(child_prefix(r), changed) != expected(r),
                "bad weight/direction/sign/order/restore/query accepted")
    require(execute(child_prefix(r - 1), valid) != expected(r),
            "omitted retained child accepted")
    require(execute(child_prefix(7), repair_program(7, Fraction(1, 2),
                                                  Fraction(11, 2))) != expected(7),
            "nonintegral rational non-Pell directions accepted")
    require(execute(child_prefix(6), repair_program(6, 1, 4)) != expected(6),
            "non-Pell arity accepted")
    domain_rejections = 0
    for pair in ((1, 0), (2, 1), (7, 3), (7, -4), (-7, 4)):
        try:
            directions(*pair)
        except ValueError:
            domain_rejections += 1
        else:
            raise ValueError("invalid Pell domain accepted")
    require(domain_rejections == 5, "scope controls incomplete")

    print("PASS_INDEPENDENT_CUBIC_PELL"
          f" polynomial_programs={polynomial_programs} dirty_cases={dirty_cases}"
          f" grid_pairs={sum(x for x, _ in counts)} grid_hits={sum(y for _, y in counts)}"
          f" pell_terms={len(terms)} descent_steps={descent_steps}"
          " mutants=9 domain_rejections=5 no_new_kappa")


if __name__ == "__main__":
    main()
