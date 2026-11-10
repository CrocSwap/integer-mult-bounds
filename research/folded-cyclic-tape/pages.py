"""Exact offline pages for the folded physical solve; no online payloads.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Classical LU/Schur algebra and #5319's effective reciprocal-pivot model.
"""
from fractions import Fraction as Q


def need(value, message):
    if not value:
        raise ValueError(message)


def order(n):
    need(type(n) is int and n > 0, "positive folded size")
    return [i // 2 if i % 2 == 0 else n - 1 - i // 2 for i in range(n)]


def norm(a):
    return max((sum(map(abs, row), Q(0)) for row in a), default=Q(0))


def gap(a):
    n = len(a)
    need(n > 0 and all(len(row) == n for row in a), "nonempty square source")
    return min(Q(a[i][i]) - sum(abs(a[i][j]) for j in range(n) if i != j)
               for i in range(n))


def lu(a):
    a = [[Q(x) for x in row] for row in a]
    n = len(a)
    low = [[Q(i == j) for j in range(n)] for i in range(n)]
    up = [[Q(0) for _ in range(n)] for _ in range(n)]
    for k in range(n):
        for j in range(k, n):
            up[k][j] = a[k][j] - sum(low[k][r] * up[r][j] for r in range(k))
        need(up[k][k] > 0, "positive no-pivot source diagonal")
        for i in range(k + 1, n):
            low[i][k] = (a[i][k] - sum(low[i][r] * up[r][k]
                                      for r in range(k))) / up[k][k]
    return low, up


def trunc(value):
    value = Q(value)
    return (-1 if value < 0 else 1) * (abs(value.numerator) // value.denominator)


def ceil_log2(value):
    value = Q(value)
    need(value > 0, "positive logarithm operand")
    k = max(0, value.numerator.bit_length() - value.denominator.bit_length())
    while Q(1 << k) < value:
        k += 1
    return k


def exact_solve(a, b):
    low, up = lu(a)
    n = len(a)
    y, x = [Q(0)] * n, [Q(0)] * n
    for i in range(n):
        y[i] = b[i] - sum(low[i][j] * y[j] for j in range(i))
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - sum(up[i][j] * x[j] for j in range(i + 1, n))) / up[i][i]
    return x


def schur(a, interior, boundary):
    n = len(a)
    need(sorted(interior + boundary) == list(range(n)), "Schur index partition")
    if not interior:
        return [[a[i][j] for j in boundary] for i in boundary]
    ai = [[a[i][j] for j in interior] for i in interior]
    columns = [exact_solve(ai, [a[i][j] for i in interior]) for j in boundary]
    return [[a[i][j] - sum(a[i][k] * columns[c][r]
                           for r, k in enumerate(interior))
             for c, j in enumerate(boundary)] for i in boundary]


def allocation(a, band, target, radius):
    """A priori two-real-component error/range budget, no observed peaks."""
    n, d, m = len(a), gap(a), norm(a)
    radius = Q(radius)
    need(d > 0 and radius >= 1 and type(target) is int and target >= 0,
         "positive row gap and prescribed target/radius")
    need(type(band) is int and band >= 1, "positive padded factor band")
    ell = m / d
    uc = band + 2 * m * m
    ec = band * m + (ell + band) * uc
    lc = ell + band
    rc = 2 + 4 * m * lc
    error = 2 * ec * radius / (d * d) + 2 * rc / d
    hmax = min(Q(1), 1 / (2 * m), d / (2 * ec),
               d / (2 * band * m), Q(1, 1 << target) / error)
    precision = max(1, ceil_log2(1 / hmax))
    h = Q(1, 1 << precision)
    yf = 2 * m * (radius + 2 * h) / d
    xx = 2 * (radius + rc * h) / d
    carrier = max(Q(1), radius, ell, m, 1 / d, yf, xx)
    width = max(precision + ceil_log2(carrier + 1) + 2,
                ceil_log2(band + 1) + 2, ceil_log2(n + 1) + 2)
    return dict(n=n, band=band, target=target, radius=radius, gap=d, mass=m,
                precision=precision, width=width, coefficient_constant=ec,
                solve_constant=rc, error_bound=error * h, forward_radius=yf,
                solution_radius=xx)


def prepare(a, band, target, radius=1):
    """Exact source LU, then one quantization of factor entries/reciprocals."""
    n = len(a)
    need(n > 0 and all(len(row) == n for row in a), "square source matrix")
    permutation = order(n)
    matrix = [[Q(a[i][j]) for j in permutation] for i in permutation]
    plan = allocation(matrix, band, target, radius)
    need(all(not matrix[i][j] for i in range(n) for j in range(n)
             if abs(i - j) > band), "folded source has declared band")
    low, up = lu(matrix)
    need(all(not low[i][j] and not up[i][j] for i in range(n)
             for j in range(n) if abs(i - j) > band), "exact LU retains band")
    unit = 1 << plan['precision']
    lower = [trunc(low[i][i-d] * unit) if i >= d else 0
             for i in range(n) for d in range(band, 0, -1)]
    upper = []
    for i in range(n - 1, -1, -1):
        upper.extend(trunc(up[i][i+d] * unit) if i+d < n else 0
                     for d in range(1, band + 1))
        reciprocal = trunc(unit / up[i][i])
        need(reciprocal > 0, "positive stored pivot reciprocal")
        upper.append(reciprocal)
    need(all(abs(v) < 1 << (plan['width']-1) for v in lower + upper),
         "all prepared coefficients fit common carrier")
    plan.update(permutation=permutation, lower=lower, upper=upper)
    return plan


def rounded_oracle(plan, rhs):
    """Diagnostic exact integer replay, not the independent matrix oracle."""
    n, b, p = plan['n'], plan['band'], plan['precision']
    lower, upper = plan['lower'], plan['upper']
    y, x = [0] * n, [0] * n
    folded = [rhs[i] for i in plan['permutation']]
    for i in range(n):
        value = folded[i] << p
        for k, d in enumerate(range(b, 0, -1)):
            if i >= d:
                value -= lower[i*b+k] * y[i-d]
        y[i] = trunc(Q(value, 1 << p))
    for pos, i in enumerate(range(n - 1, -1, -1)):
        value = y[i] << p
        for k in range(b):
            if i+k+1 < n:
                value -= upper[pos*(b+1)+k] * x[i+k+1]
        value *= upper[pos*(b+1)+b]
        x[i] = trunc(Q(value, 1 << (2*p)))
    result = [0] * n
    for i, old in enumerate(plan['permutation']):
        result[old] = x[i]
    return result
