#!/usr/bin/env python3
"""Exact finite controls for the separately proved all-depth macro-cut bound.

Brian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import json


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def eye(n):
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))


def mul(a, b):
    n = len(a)
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(n))
                       for j in range(n)) for i in range(n))


def inverse(a):
    n = len(a)
    rows = [list(row) + list(unit) for row, unit in zip(a, eye(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        need(pivot is not None, "singular cut operator")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        divisor = rows[j][j]
        rows[j] = [x / divisor for x in rows[j]]
        for i in range(n):
            if i != j:
                coefficient = rows[i][j]
                rows[i] = [x - coefficient * y for x, y in zip(rows[i], rows[j])]
    return tuple(tuple(row[n:]) for row in rows)


def norm(a):
    return max(sum(map(abs, row)) for row in a)


def toeplitz(f):
    return tuple(tuple(f[i - j] if i >= j else Q(0)
                       for j in range(len(f))) for i in range(len(f)))


def conv(a, b):
    return tuple(sum(a[j] * b[i - j] for j in range(i + 1))
                 for i in range(len(a)))


def split(f, wrong_schur=False):
    n, m = len(f), len(f) // 2
    e, o = f[::2], f[1::2]
    k = []
    for i in range(m):
        k.append(o[i] - sum(e[j] * k[i - j] for j in range(1, i + 1)))
    ok = conv(o, k)
    s = tuple(e[i] + (1 if wrong_schur else -1) * (ok[i - 1] if i else 0)
              for i in range(m))
    left, right = [list(row) for row in eye(n)], [list(row) for row in eye(n)]
    for i in range(m):
        for j in range(i + 1):
            left[m + i][j] = k[i - j]
            if i > j:
                right[i][m + j] = k[i - j - 1]
    return e, s, tuple(map(tuple, left)), tuple(map(tuple, right))


def diagonal(a, b):
    m = len(a)
    return tuple(tuple(a[i][j] if i < m and j < m else
                       b[i - m][j - m] if i >= m and j >= m else Q(0)
                       for j in range(2 * m)) for i in range(2 * m))


def unpermute(a):
    n = len(a)
    order = list(range(0, n, 2)) + list(range(1, n, 2))
    positions = [order.index(i) for i in range(n)]
    return tuple(tuple(a[i][j] for j in positions) for i in positions)


def cuts(f):
    """All cut matrices, including every pair of independently reached child cuts."""
    n = len(f)
    need(n > 0 and n & (n - 1) == 0 and f[0] == 1, "unit dyadic symbol")
    if n == 1:
        return {eye(1)}
    e, s, left, right = split(f)
    need(unpermute(mul(left, mul(diagonal(toeplitz(e), toeplitz(s)), right)))
         == toeplitz(f), "literal parity factorization")
    states = {eye(n), toeplitz(f)}
    for pe in cuts(e):
        for ps in cuts(s):
            states.add(unpermute(mul(diagonal(pe, ps), right)))
    return states


def verify():
    # Signed, dense, zero, pure-odd, and eta>1/2 cases exercise distinct boundaries.
    fixtures = [
        (1,), (1, 0), (1, Q(1, 2), 0, 0),
        (1, Q(1, 4), Q(1, 8), Q(1, 8), 0, 0, 0, 0),
        (1, Q(1, 4), -Q(1, 4), Q(1, 8), -Q(1, 8), 0, 0, 0),
        (1, Q(1, 16), -Q(1, 16), Q(1, 16), -Q(1, 16),
         Q(1, 16), -Q(1, 16), Q(1, 16)),
        (1, Q(1, 2), *([0] * 14)),
    ]
    receipt = []
    for values in fixtures:
        f = tuple(map(Q, values))
        eta = sum(map(abs, f[1:]))
        need(eta < 1, "strict tail budget")
        bound, t = Q(1) / (1 - eta), toeplitz(f)
        ti, states = inverse(t), cuts(f)
        maxima = [Q(0)] * 4
        for p in states:
            pi = inverse(p)
            operators = p, pi, mul(t, pi), mul(p, ti)
            need(mul(p, pi) == eye(len(f)), "cut inverse identity")
            need(mul(operators[2], p) == t, "suffix times prefix identity")
            need(mul(operators[2], operators[3]) == eye(len(f)), "suffix inverse identity")
            for i, op in enumerate(operators):
                maxima[i] = max(maxima[i], norm(op))
                need(norm(op) <= bound, "uniform macro-cut bound")
        receipt.append({"n": len(f), "tail_l1": str(eta), "cut_states": len(states),
                        "bound": str(bound), "max_norms_P_Pinv_Q_Qinv": list(map(str, maxima))})
    f = tuple(map(Q, (1, Q(1, 2), 0, 0)))
    e, s, left, right = split(f, wrong_schur=True)
    need(unpermute(mul(left, mul(diagonal(toeplitz(e), toeplitz(s)), right)))
         != toeplitz(f), "wrong Schur sign must change endpoint")
    e, s, left, right = split(f)
    suffix = mul(toeplitz(f), inverse(unpermute(right)))
    need(suffix[-1] == (0, -Q(1, 4), Q(1, 2), 1), "literal suffix witness row")
    need(norm(suffix) == Q(7, 4), "three-halves is not an all-cut bound")
    for n in (4, 16):
        geometric = toeplitz((Q(1), Q(1, 2), *([Q(0)] * (n - 2))))
        need(norm(inverse(geometric)) == 2 - Q(1, 2) ** (n - 1),
             "geometric inverse lower-bound family")
    middle = diagonal(toeplitz(e), toeplitz(s))
    need(unpermute(mul(middle, right)) != toeplitz(f), "missing left shear must fail")
    need(unpermute(mul(right, mul(middle, left))) != toeplitz(f), "reversed macro order must fail")
    need(norm(toeplitz(tuple(map(Q, (1, 2, 0, 0))))) > 2,
         "outside-tail control must exceed the half-budget bound")
    print(json.dumps({"fixtures": receipt, "failure_controls": 4}, indent=2))
    print("PASS_TRIANGULAR_PARITY_UNIFORM_PREFIX")


if __name__ == "__main__":
    verify()
