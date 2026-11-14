#!/usr/bin/env python3
"""Bounded exact failure controls for the all-size proof in PROOF.md.

Standard library only. No assertions are used, so -O cannot disable checks.
The matrices are constructed literally; denominator-cleared Bareiss minors
are checked independently of the rational row reduction used for ranks.
"""

from fractions import Fraction as F
from itertools import permutations
from math import lcm
import json
import random


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def zeros(rows, cols=None):
    return [[F(0) for _ in range(rows if cols is None else cols)] for _ in range(rows)]


def identity(n):
    a = zeros(n)
    for i in range(n):
        a[i][i] = F(1)
    return a


def transpose(a):
    return [list(row) for row in zip(*a)]


def add(a, b):
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def sub(a, b):
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(a, c):
    return [[c * x for x in row] for row in a]


def multiply(a, b):
    out = zeros(len(a), len(b[0]))
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        out[i][j] += x * y
    return out


def kron(a, b):
    return [[x * y for x in ar for y in br] for ar in a for br in b]


def tensor(factors):
    out = [[F(1)]]
    for a in factors:
        out = kron(out, a)
    return out


def shift(n):
    a = zeros(n)
    for i in range(1, n):
        a[i][i - 1] = F(1)
    return a


def displacements(a):
    z = shift(len(a))
    return sub(multiply(a, z), multiply(z, a)), sub(a, multiply(multiply(z, a), transpose(z)))


def entry_displacements(a):
    n = len(a)
    d = [[(a[i][j + 1] if j + 1 < n else F(0)) -
          (a[i - 1][j] if i else F(0)) for j in range(n)] for i in range(n)]
    e = [[a[i][j] - (a[i - 1][j - 1] if i and j else F(0))
          for j in range(n)] for i in range(n)]
    return d, e


def rref(a):
    out = [row[:] for row in a]
    pivots = []
    row = 0
    for col in range(len(out[0])):
        pivot = next((i for i in range(row, len(out)) if out[i][col]), None)
        if pivot is None:
            continue
        out[row], out[pivot] = out[pivot], out[row]
        value = out[row][col]
        out[row] = [x / value for x in out[row]]
        for i in range(len(out)):
            if i != row and out[i][col]:
                value = out[i][col]
                out[i] = [x - value * y for x, y in zip(out[i], out[row])]
        pivots.append(col)
        row += 1
        if row == len(out):
            break
    return out, pivots


def rank(a):
    return len(rref(a)[1])


def inverse(a):
    n = len(a)
    out, pivots = rref([row + eye for row, eye in zip(a, identity(n))])
    require(pivots[:n] == list(range(n)), "inverse requested for a singular matrix")
    result = [row[n:] for row in out]
    require(multiply(a, result) == identity(n), "left inverse residual")
    require(multiply(result, a) == identity(n), "right inverse residual")
    return result


def determinant(a):
    """Integer Bareiss elimination after clearing denominators row by row."""
    work = []
    denominator = 1
    for row in a:
        common = lcm(*(x.denominator for x in row))
        denominator *= common
        work.append([int(x * common) for x in row])
    n = len(work)
    sign, previous = 1, 1
    for k in range(n - 1):
        pivot_row = next((i for i in range(k, n) if work[i][k]), None)
        if pivot_row is None:
            return F(0)
        if pivot_row != k:
            work[k], work[pivot_row] = work[pivot_row], work[k]
            sign = -sign
        pivot = work[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = pivot * work[i][j] - work[i][k] * work[k][j]
                require(numerator % previous == 0, "nonintegral Bareiss step")
                work[i][j] = numerator // previous
        for i in range(k + 1, n):
            work[i][k] = 0
        previous = pivot
    return F(sign * work[-1][-1], denominator)


def select(a, indices):
    return [[a[i][j] for j in indices] for i in indices]


def block(a, b, c, d):
    return [x + y for x, y in zip(a, b)] + [x + y for x, y in zip(c, d)]


def gaussian(n, q, v):
    return [[q ** ((i - j) ** 2) * v ** (i - j) for j in range(n)] for i in range(n)]


def check_gaussian_det(a, q):
    expected = F(1)
    for k in range(1, len(a)):
        expected *= (1 - q ** (2 * k)) ** (len(a) - k)
    require(determinant(a) == expected and expected > 0, "Gaussian Vandermonde determinant")


def reconstruct_generators(a):
    """Recover the minimum ordinary generator count by rank factorization."""
    e = entry_displacements(a)[1]
    reduced, pivots = rref(e)
    c = [[row[j] for j in pivots] for row in e]
    r = reduced[:len(pivots)]
    require(multiply(c, r) == e, "rank factorization residual")
    n = len(a)
    recovered = zeros(n)
    for k in range(len(pivots)):
        u = [c[i][k] for i in range(n)]
        v = r[k]
        lower = [[u[i - j] if i >= j else F(0) for j in range(n)] for i in range(n)]
        upper = [[v[j - i] if j >= i else F(0) for j in range(n)] for i in range(n)]
        term = multiply(lower, upper)
        require(entry_displacements(term)[1] == [[x * y for y in v] for x in u],
                "single generator displacement")
        recovered = add(recovered, term)
    require(recovered == a, "Toeplitz generator reconstruction residual")
    return len(pivots)


def generic_controls():
    rng = random.Random(641)
    count, inverse_count = 0, 0
    for m in range(1, 4):
        for n in range(2, 6):
            for _ in range(4):
                a = [[F(rng.randint(-3, 3), rng.randint(1, 3)) for _ in range(m)]
                     for _ in range(m)]
                a = add(a, scale(identity(m), F(20)))
                da = determinant(a)
                require(da != 0, "fixture A unexpectedly singular")
                coeff = {k: F(rng.choice((-3, -2, -1, 1, 2, 3)), rng.randint(1, 4))
                         for k in range(1 - n, n)}
                b = [[coeff[i - j] for j in range(n)] for i in range(n)]
                h = kron(a, b)
                d, e = displacements(h)
                require((d, e) == entry_displacements(h), "literal shift orientation")
                require(rank(d) == rank(e) == 2 * m, "general forward rank")
                r = sub(scale(identity(m), coeff[-1]), scale(shift(m), coeff[n - 1]))
                s = sub(scale(identity(m), coeff[1]), scale(transpose(shift(m)), coeff[1 - n]))
                dc = [i * n for i in range(m)] + [i * n + n - 1 for i in range(m)]
                ec = [i * n for i in range(m)] + [i * n + 1 for i in range(m)]
                dm, em = select(d, dc), select(e, ec)
                require(dm == block(multiply(r, a), scale(sub(multiply(a, shift(m)),
                        multiply(shift(m), a)), coeff[0]), zeros(m), scale(multiply(a, r), F(-1))),
                        "Sylvester boundary minor entries")
                require(em == block(scale(sub(a, multiply(multiply(shift(m), a),
                        transpose(shift(m)))), coeff[0]), multiply(r, a), multiply(a, s), zeros(m)),
                        "Stein boundary minor entries")
                require(determinant(dm) == (-coeff[-1] ** 2) ** m * da ** 2,
                        "Sylvester boundary minor determinant")
                require(determinant(em) == (-coeff[-1] * coeff[1]) ** m * da ** 2,
                        "Stein boundary minor determinant")
                if determinant(b):
                    hi = inverse(h)
                    di = entry_displacements(hi)[0]
                    require(di == scale(multiply(multiply(hi, d), hi), F(-1)),
                            "inverse Sylvester identity")
                    require(rank(di) == 2 * m, "inverse Sylvester rank")
                    inverse_count += 1
                count += 1
    return count, inverse_count


def gaussian_controls():
    dimensions = [(2,), (3,), (4,), (2, 2), (2, 3), (3, 2), (3, 3),
                  (2, 4), (4, 2), (2, 2, 2), (2, 2, 3)]
    count, generator_count = 0, 0
    qs, vs = [F(1, 2), F(2, 3), F(1, 3)], [F(2, 3), F(3, 2), F(2)]
    for dims in dimensions:
        factors = [gaussian(n, qs[i % 3], vs[i % 3]) for i, n in enumerate(dims)]
        for i, a in enumerate(factors):
            check_gaussian_det(a, qs[i % 3])
        h = tensor(factors)
        hi = inverse(h)
        expected = 2 * len(h) // dims[-1]
        for x in (h, hi):
            d, e = displacements(x)
            require((d, e) == entry_displacements(x), "Gaussian literal shift orientation")
            require(rank(d) == rank(e) == expected, "Gaussian tensor forward/inverse ranks")
            require([list(reversed(row)) for row in reversed(x)] == transpose(x),
                    "tensor persymmetry")
            require(reconstruct_generators(x) == expected, "minimum generator construction")
            generator_count += 1
        z = shift(len(h))
        reverse = sub(hi, multiply(multiply(transpose(z), hi), z))
        require(rank(reverse) == rank(entry_displacements(h)[1]), "Schur-complement rank identity")
        count += 1
    # Distinct factors, all six lexicographic axis orders; no arbitrary permutation claim.
    factors = [gaussian(2, F(1, 2), F(2)), gaussian(3, F(1, 3), F(3, 2)),
               gaussian(2, F(2, 3), F(2, 3))]
    ranks = []
    for order in permutations(range(3)):
        h = tensor([factors[i] for i in order])
        expected = 2 * len(h) // len(factors[order[-1]])
        for x in (h, inverse(h)):
            require(tuple(map(rank, entry_displacements(x))) == (expected, expected),
                    "axis-order rank formula")
        ranks.append(expected)
    require(min(ranks) == 8, "optimal lexicographic axis order")
    return count, generator_count, len(ranks)


def failure_controls():
    controls = []
    # Missing adjacent coefficients and singular outer factor must not be accepted.
    d, e = displacements(identity(6))
    require((rank(d), rank(e)) == (0, 1), "identity negative control")
    controls.append("zero-adjacent-coefficients")
    a = [[F(1), F(2)], [F(2), F(4)]]
    h = kron(a, gaussian(2, F(1, 2), F(2)))
    require(all(rank(x) < 4 for x in displacements(h)), "singular A negative control")
    controls.append("singular-outer-factor")
    h = kron(identity(2), gaussian(3, F(1, 2), F(1)))
    wrong = kron(shift(2), identity(3))
    require(rank(sub(multiply(h, wrong), multiply(wrong, h))) == 0,
            "wrong-axis shift control")
    require(rank(displacements(h)[0]) == 4, "full shift distinction")
    controls.append("axis-shift-is-not-full-shift")
    b = gaussian(2, F(1, 2), F(1))
    h = kron(b, b)
    gray = select(h, [0, 1, 3, 2])
    require(tuple(map(rank, displacements(h))) == (4, 4), "lexicographic baseline")
    require(tuple(map(rank, displacements(gray))) == (2, 2), "Gray-order scope control")
    controls.append("arbitrary-coordinate-permutation-can-reduce-rank")
    factors = [gaussian(2, F(1, 2), F(1)), gaussian(2, F(1, 3), F(2)),
               gaussian(2, F(2, 3), F(3, 2))]
    product = identity(8)
    for axis in range(3):
        local = tensor([factors[i] if i == axis else identity(2) for i in range(3)])
        product = multiply(local, product)
    require(product == tensor(factors), "direct separable circuit control")
    require(tuple(map(rank, displacements(product))) == (8, 8), "high rank with cheap circuit")
    controls.append("separable-circuit-despite-full-displacement-rank")
    # Force an intentionally false formula through the same explicit check path.
    caught = False
    try:
        require(rank(displacements(product)[0]) == 7, "deliberately wrong rank")
    except VerificationError:
        caught = True
    require(caught, "failure detection was disabled")
    controls.append("wrong-rank-rejected-under-optimized-python")
    return controls


def main():
    generic, inverse_generic = generic_controls()
    gaussian_cases, generators, axis_orders = gaussian_controls()
    controls = failure_controls()
    result = {
        "status": "PASS", "arithmetic": "exact fractions; integer Bareiss minors",
        "seed": 641, "generic_forward_cases": generic,
        "generic_inverse_sylvester_cases": inverse_generic,
        "gaussian_tensor_cases": gaussian_cases,
        "minimum_generator_reconstructions": generators,
        "distinct_axis_orders": axis_orders, "negative_controls": controls,
        "claim_scope": "finite controls for PROOF.md; no kappa or runtime lower bound"
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
