"""Exact finite corroboration of the optimal-second-callee classification.

Produced by Nick Petalas. Apache-2.0.
Fixed prime-field domains only; normal execution writes nothing.
"""

import hashlib
import itertools
import json
from pathlib import Path

Matrix = tuple[tuple[int, ...], ...]
DOMAINS = ((2, 3), (5, 2))
COUNT_DOMAINS = ((2, 1), (2, 2), (2, 3), (2, 4),
                 (3, 1), (3, 2), (3, 3), (5, 1), (5, 2), (7, 1), (7, 2))


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def eye(n: int) -> Matrix:
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def zero(n: int) -> Matrix:
    return tuple((0,) * n for _ in range(n))


def add(a: Matrix, b: Matrix, q: int, sign: int = 1) -> Matrix:
    return tuple(tuple((x + sign * y) % q for x, y in zip(ar, br))
                 for ar, br in zip(a, b))


def mul(a: Matrix, b: Matrix, q: int) -> Matrix:
    return tuple(tuple(sum(x * y for x, y in zip(ar, bc)) % q
                       for bc in zip(*b)) for ar in a)


def vector(a: Matrix, x: tuple[int, ...], q: int) -> tuple[int, ...]:
    return tuple(sum(u * v for u, v in zip(row, x)) % q for row in a)


def row_reduce(a: Matrix, q: int) -> tuple[Matrix, Matrix, tuple[int, ...]]:
    """Return R,U,pivots with U A=R, using bounded row elimination."""
    n, m = len(a), len(a[0])
    rows, transform, pivots = [list(row) for row in a], [list(r) for r in eye(n)], []
    for col in range(m):
        pivot = next((i for i in range(len(pivots), n) if rows[i][col]), None)
        if pivot is None:
            continue
        k = len(pivots)
        rows[k], rows[pivot] = rows[pivot], rows[k]
        transform[k], transform[pivot] = transform[pivot], transform[k]
        scale = pow(rows[k][col], -1, q)
        rows[k] = [(x * scale) % q for x in rows[k]]
        transform[k] = [(x * scale) % q for x in transform[k]]
        for i in range(n):
            if i != k:
                factor = rows[i][col]
                rows[i] = [(x - factor * y) % q for x, y in zip(rows[i], rows[k])]
                transform[i] = [(x - factor * y) % q
                                for x, y in zip(transform[i], transform[k])]
        pivots.append(col)
    return tuple(map(tuple, rows)), tuple(map(tuple, transform)), tuple(pivots)


def rank(a: Matrix, q: int) -> int:
    return len(row_reduce(a, q)[2])


def inverse(a: Matrix, q: int) -> Matrix:
    reduced, transform, pivots = row_reduce(a, q)
    need(len(pivots) == len(a), "inverse of a singular matrix")
    need(reduced == eye(len(a)), "invalid inverse reduction")
    need(mul(a, transform, q) == eye(len(a)), "inverse postcondition")
    return transform


def inner_inverse(a: Matrix, q: int) -> Matrix:
    _, transform, pivots = row_reduce(a, q)
    rows = [list(r) for r in zero(len(a))]
    for i, pivot in enumerate(pivots):
        rows[pivot] = list(transform[i])
    g = tuple(map(tuple, rows))
    need(mul(mul(a, g, q), a, q) == a, "A G A must equal A")
    return g


def matrices(q: int, n: int):
    need(q in (2, 3, 5, 7) and 1 <= n <= 4, "unsupported finite domain")
    need(q ** (n * n) <= 65536, "matrix enumeration capacity exceeded")
    for entries in itertools.product(range(q), repeat=n * n):
        yield tuple(tuple(entries[i * n:(i + 1) * n]) for i in range(n))


def block(a: Matrix, r: Matrix) -> Matrix:
    z = zero(len(a))
    return tuple(x + y for x, y in zip(a, r)) + tuple(x + y for x, y in zip(r, z))


def conditions(a: Matrix, r: Matrix, g: Matrix, q: int) -> tuple[bool, bool, bool]:
    s = rank(a, q)
    horizontal = tuple(x + y for x, y in zip(a, r))
    return (rank(horizontal, q) == s,
            rank(a + r, q) == s,
            mul(mul(r, g, q), r, q) == zero(len(a)))


def literal_error(p: Matrix, pi: Matrix, t: Matrix, ti: Matrix, q: int) -> Matrix:
    """Execute the six body operations on every complete basis input."""
    n = len(p)
    columns = []
    for j in range(2 * n):
        h0 = tuple(int(j == i) for i in range(n))
        d0 = tuple(int(j == n + i) for i in range(n))
        h, d = h0, tuple((x - y) % q for x, y in zip(d0, h0))
        h, d = vector(p, d, q), vector(pi, h, q)
        d = tuple((x + y) % q for x, y in zip(d, h))
        h, d = vector(t, d, q), vector(ti, h, q)
        d = tuple((-x) % q for x in d)
        d = tuple((x + y) % q for x, y in zip(d, h))
        columns.append(tuple((x - y) % q for x, y in zip(h, d0))
                       + tuple((x - y) % q for x, y in zip(d, h0)))
    return tuple(zip(*columns))


def equality_lemma() -> dict:
    cases = alternate_g = 0
    for q in (2, 3):
        domain = tuple(matrices(q, 2))
        for a in domain:
            g, s = inner_inverse(a, q), rank(a, q)
            for r in domain:
                actual = rank(block(a, r), q) == s
                need(actual == all(conditions(a, r, g, q)), "block equality iff failed")
                cases += 1
            for other_g in domain:
                if mul(mul(a, other_g, q), a, q) == a:
                    for r in domain:
                        need(conditions(a, r, g, q) == conditions(a, r, other_g, q)
                             or not all(conditions(a, r, g, q)[:2]),
                             "inner inverse dependence under containments")
                    alternate_g += 1
    return {"all_A_R_pairs": cases, "all_inner_inverses": alternate_g}


def wrapper_classification() -> list[dict]:
    rows = []
    for q, n in DOMAINS:
        group = tuple(a for a in matrices(q, n) if rank(a, q) == n)
        inverses = {a: inverse(a, q) for a in group}
        optimal = pairs = changed = 0
        by_rank = [0] * (n + 1)
        for p in group:
            a = add(mul(p, p, q), eye(n), q, -1)
            g, s = inner_inverse(a, q), rank(a, q)
            for t in group:
                r = add(t, p, q, -1)
                actual = rank(literal_error(p, inverses[p], t, inverses[t], q), q) == s
                predicted = all(conditions(a, r, g, q))
                need(actual == predicted, "new equality classification failed")
                if actual:
                    optimal += 1
                    by_rank[rank(r, q)] += 1
                    changed += int(r != zero(n))
                pairs += 1
        rows.append({"q": q, "n": n, "invertible_first_maps": len(group),
                     "ordered_pairs": pairs, "optimal_pairs": optimal,
                     "changed_optimal_pairs": changed, "optimal_by_rank_Q_minus_P": by_rank})
    return rows


def gaussian(n: int, r: int, q: int) -> int:
    numerator = denominator = 1
    for j in range(r):
        numerator *= q ** n - q ** j
        denominator *= q ** r - q ** j
    need(numerator % denominator == 0, "nonintegral Gaussian coefficient")
    return numerator // denominator


def square_zero_counts() -> list[dict]:
    rows = []
    for q, n in COUNT_DOMAINS:
        observed = [0] * (n // 2 + 1)
        visited = 0
        for s in matrices(q, n):
            visited += 1
            if mul(s, s, q) == zero(n):
                r = rank(s, q)
                need(r <= n // 2, "square-zero rank bound")
                observed[r] += 1
        expected = []
        for r in range(n // 2 + 1):
            gl = 1
            for j in range(r):
                gl *= q ** r - q ** j
            expected.append(gaussian(n, r, q) * gaussian(n - r, r, q) * gl)
        need(observed == expected, "square-zero rank-stratum count failed")
        rows.append({"q": q, "n": n, "matrices_enumerated": visited,
                     "count_by_rank": observed, "total": sum(observed)})
    return rows


def controls() -> dict:
    q, p = 5, ((2, 0), (0, 2))
    a = add(mul(p, p, q), eye(2), q, -1)
    g = inner_inverse(a, q)
    t = ((2, 1), (0, 2))
    e = literal_error(p, inverse(p, q), t, inverse(t, q), q)
    need(t != p and all(conditions(a, add(t, p, q, -1), g, q)), "changed optimum")
    agreements = 0
    for x in itertools.product(range(q), repeat=4):
        agreements += int(vector(e, x, q) == (0,) * 4)
    need(agreements == 25, "first fixture must attain 25 of 625 pairs")
    bad_square = ((3, 0), (0, 2))
    need(not all(conditions(a, add(bad_square, p, q, -1), g, q)), "square-zero control")
    singular_a = ((1, 0), (0, 0))
    bad_image, bad_kernel = ((0, 0), (1, 0)), ((0, 1), (0, 0))
    need(conditions(singular_a, bad_image, singular_a, q) == (False, True, True),
         "image containment is necessary")
    need(conditions(singular_a, bad_kernel, singular_a, q) == (True, False, True),
         "kernel containment is necessary")
    need(rank(block(singular_a, bad_image), q) > 1, "image mutant rank")
    need(rank(block(singular_a, bad_kernel), q) > 1, "kernel mutant rank")
    r = ((4, 1), (4, 1))
    singular_t = add(((2, 0), (0, 3)), r, q)
    need(all(conditions(a, r, g, q)) and rank(singular_t, q) == 1,
         "admissible Q must separately be invertible")
    nilpotent = ((0, 1), (0, 0))
    need(not all(conditions(zero(2), nilpotent, zero(2), 2)), "involutory uniqueness")
    return {"changed_scalar_optimum_agreements": agreements,
            "first_fixture_pairs": 625, "control_groups": 6}


def main() -> None:
    result = {"claim_type": "scoped written proof with exact finite corroboration",
              "block_equality": equality_lemma(),
              "wrapper_classification": wrapper_classification(),
              "square_zero_counts": square_zero_counts(), "controls": controls()}
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["source_sha256"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                               for name in names}
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_OPTIMAL_SECOND_CALLEES no_new_kappa")


if __name__ == "__main__":
    main()
