"""Exact finite evidence for row-dependent cyclic-band precision.

This contribution was produced by Nick Petalas. Apache-2.0.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import islice
from pathlib import Path
import json

MAX_N = 257
MAX_W = 8
MAX_Q = 512


def need(condition, message):
    if not condition:
        raise ValueError(message)


def trunc_ratio(numerator, denominator):
    need(denominator > 0, "nonpositive divisor")
    magnitude = abs(numerator) // denominator
    return -magnitude if numerator < 0 else magnitude


def precision(bound, minimum):
    need(bound > 0 and 0 <= minimum <= MAX_Q, "precision arguments")
    for q in range(minimum, MAX_Q + 1):
        if F(1, 1 << q) <= bound:
            return q
    raise ValueError("precision capacity")


def symbolic(n, w):
    need(1 <= n <= MAX_N and 0 <= w <= min(MAX_W, n - 1), "shape")
    adjacency = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if min(j - i, n - j + i) <= w:
                adjacency[i].add(j)
                adjacency[j].add(i)
    lower = [[] for _ in range(n)]
    upper = []
    products = 0
    for k in range(n):
        later = sorted(j for j in adjacency[k] if j > k)
        upper.append([k] + later)
        for i in later:
            lower[i].append(k)
            for j in later:
                adjacency[i].add(j)
                products += 1
    counts = [len(lower[i]) + len(upper[i]) for i in range(n)]
    need(products <= 4 * n * w * w, "symbolic product bound")
    return lower, upper, counts, products


def validate(a, p, delta, maximum, rhs, y_bound):
    n = len(a)
    need(1 <= n <= MAX_N and len(rhs) == n, "matrix/RHS shape")
    need(0 <= p <= 64 and delta > 0 and maximum >= delta, "parameters")
    need(y_bound > 0 and max(map(abs, rhs)) <= y_bound, "RHS bound")
    for i, row in enumerate(a):
        need(len(row) == n, "matrix row")
        need(all((v * (1 << p)).denominator == 1 for v in row), "input grid")
        off = sum(abs(row[j]) for j in range(n) if j != i)
        need(row[i] - off >= delta, "row gap")
        need(sum(map(abs, row)) <= maximum, "row norm")


def allocate(n, w, p, delta, maximum, y_bound, target):
    need(target > 0 and delta > 0 and y_bound > 0, "error budgets")
    k_bound = max(F(1), 2 * maximum)
    e_budget = min(delta / 2, target * delta * delta / (4 * y_bound))
    solve_step = target * delta * delta / (8 * delta + 24 * maximum * maximum)
    q_solve = precision(solve_step, p)
    q_global = precision(e_budget / (n * k_bound), p)
    bulk = min(n, 3 * w + 1)
    q_bulk = precision(e_budget / (bulk * k_bound), p)
    grids = [q_bulk if i < n - w else q_global for i in range(n)]
    need(all(grids[i] <= grids[i + 1] for i in range(n - 1)), "monotone grids")
    return grids, q_solve, q_global, e_budget


def factor(a, lower, upper, grids):
    n = len(a)
    need(len(grids) == n and all(0 <= q <= MAX_Q for q in grids), "factor grids")
    need(all(grids[i] <= grids[i + 1] for i in range(n - 1)), "grid order")
    scales = [1 << q for q in grids]
    c = [{} for _ in range(n)]
    l = [{} for _ in range(n)]
    u = [{} for _ in range(n)]
    for i in range(n):
        for j in lower[i] + upper[i]:
            exact = a[i][j] * scales[i] * scales[i]
            need(exact.denominator == 1, "Schur input grid")
            c[i][j] = exact.numerator
    operations = 0
    for k in range(n):
        for j in upper[k]:
            u[k][j] = trunc_ratio(c[k][j], scales[k])
        need(u[k][k] > 0, "positive pivot")
        for i in upper[k][1:]:
            shift = 1 << (grids[i] - grids[k])
            l[i][k] = trunc_ratio(c[i][k], u[k][k] * shift)
            for j in upper[k][1:]:
                need(j in c[i], "symbolic update closure")
                c[i][j] -= l[i][k] * u[k][j] * shift
                operations += 1
    return l, u, operations


def solve(l, u, grids, q_solve, rhs):
    n = len(l)
    s_solve = 1 << q_solve
    need(all((v * s_solve).denominator == 1 for v in rhs), "RHS solve grid")
    z = [0] * n
    x = [0] * n
    for i in range(n):
        scale = 1 << grids[i]
        total = (rhs[i] * scale * s_solve).numerator
        total -= sum(value * z[j] for j, value in l[i].items())
        z[i] = trunc_ratio(total, scale)
    for i in range(n - 1, -1, -1):
        scale = 1 << grids[i]
        total = z[i] * scale
        total -= sum(value * x[j] for j, value in u[i].items() if j != i)
        x[i] = trunc_ratio(total, u[i][i])
    return [F(value, s_solve) for value in x]


def factor_residual(a, l, u, grids):
    n = len(a)
    residual = [[-v for v in row] for row in a]
    for i in range(n):
        for k, value in {**l[i], i: 1 << grids[i]}.items():
            left = F(value, 1 << grids[i])
            for j, right in u[k].items():
                residual[i][j] += left * F(right, 1 << grids[k])
    return max(sum(map(abs, row)) for row in residual)


def exact_solve(a, rhs):
    """Independent pivoted rational reference, used only for n <= 12."""
    n = len(a)
    need(n <= 12, "reference capacity")
    rows = [list(a[i]) + [rhs[i]] for i in range(n)]
    for k in range(n):
        pivot = k
        for i in range(k + 1, n):
            if abs(rows[i][k]) > abs(rows[pivot][k]):
                pivot = i
        need(rows[pivot][k] != 0, "reference singularity")
        rows[k], rows[pivot] = rows[pivot], rows[k]
        value = rows[k][k]
        rows[k] = [v / value for v in rows[k]]
        for i in range(n):
            if i != k:
                value = rows[i][k]
                rows[i] = [rows[i][j] - value * rows[k][j] for j in range(n + 1)]
    return [row[-1] for row in rows]


def fixture(n, w, gap, signed):
    a = [[F(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and min(abs(i - j), n - abs(i - j)) <= w:
                coefficient = ((17 * i + 11 * j) % 4 + 1)
                sign = -1 if not signed or (i + 3 * j) % 3 else 1
                a[i][j] = F(sign * coefficient, 32)
        a[i][i] = gap + sum(map(abs, a[i]))
    rhs = [F((i % 5) - 2, 2) for i in range(n)]
    return a, rhs


def run_case(a, rhs, w, p, delta, maximum, target):
    validate(a, p, delta, maximum, rhs, F(1))
    lower, upper, counts, expected_ops = symbolic(len(a), w)
    for i, row in enumerate(a):
        need(all(v == 0 or j in lower[i] + upper[i] for j, v in enumerate(row)), "input pattern")
    grids, q_solve, q_global, e_budget = allocate(len(a), w, p, delta, maximum, F(1), target)
    l, u, products = factor(a, lower, upper, grids)
    need(products == expected_ops, "complete factor work")
    actual = factor_residual(a, l, u, grids)
    bound = max(counts[i] * max(F(1), 2 * maximum) / (1 << grids[i]) for i in range(len(a)))
    need(actual <= bound <= e_budget <= delta / 2, "factor certificate")
    x = solve(l, u, grids, q_solve, rhs)
    residual = max(abs(sum(a[i][j] * x[j] for j in range(len(a))) - rhs[i]) for i in range(len(a)))
    h_solve = F(1, 1 << q_solve)
    r_solve = 2 * h_solve * (1 + 3 * maximum * maximum / delta)
    error_bound = (bound + delta * r_solve) / (delta * (delta - bound))
    need(error_bound <= target and residual <= delta * target, "solution certificate")
    if len(a) <= 12:
        reference = exact_solve(a, rhs)
        need(max(abs(v - r) for v, r in zip(x, reference)) <= error_bound, "independent solution")
    return {"n": len(a), "w": w, "bulk_q": grids[0], "border_q": grids[-1],
            "solve_q": q_solve, "global_q": q_global, "entries": sum(counts),
            "fraction_bits": sum(c * q for c, q in zip(counts, grids)),
            "global_fraction_bits": sum(counts) * q_global,
            "factor_products": products, "residual": str(residual), "error_bound": str(error_bound)}


def pattern_checks():
    cases = 0
    positions = 0
    for n in range(1, 130):
        for w in range(min(MAX_W, n - 1) + 1):
            lower, upper, counts, _ = symbolic(n, w)
            for i, count in enumerate(counts):
                need(count <= (min(n, 3 * w + 1) if i < n - w else n), "row support bound")
            need(sum(counts) <= (4 * w + 1) * n, "storage bound")
            positions += sum(counts)
            cases += 1
    return cases, positions


def rejection_checks():
    count = 0
    for denominator in (0, -1):
        try:
            trunc_ratio(1, denominator)
        except ValueError:
            count += 1
        else:
            raise ValueError("bad divisor accepted")
    for shape in ((0, 0), (MAX_N + 1, 1), (4, 4), (20, MAX_W + 1)):
        try:
            symbolic(*shape)
        except ValueError:
            count += 1
        else:
            raise ValueError("bad shape accepted")
    a, rhs = fixture(4, 1, F(1, 8), False)
    lower, upper, _, _ = symbolic(4, 1)
    try:
        factor(a, lower, upper, [20, 19, 20, 20])
    except ValueError:
        count += 1
    else:
        raise ValueError("descending grid accepted")
    try:
        validate(a, 2, F(1, 8), F(2), rhs, F(1))
    except ValueError:
        count += 1
    else:
        raise ValueError("off-grid input accepted")
    return count


def main():
    pattern_cases, positions = pattern_checks()
    small = 0
    for n in range(1, 13):
        for w in range(min(3, n - 1) + 1):
            for exponent in (1, 4, 10):
                for signed in (False, True):
                    gap = F(1, 1 << exponent)
                    a, rhs = fixture(n, w, gap, signed)
                    maximum = max(sum(map(abs, row)) for row in a)
                    # The summary is discarded; run_case checks every invariant.
                    _ = run_case(a, rhs, w, 10, gap, maximum, F(1, 1 << 12))
                    small += 1
    n = 65
    a = [[F(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        a[i][i] = F(1)
        a[i][(i - 1) % n] = a[i][(i + 1) % n] = F(-63, 128)
    rhs = [F(1 if i % 2 == 0 else -1) for i in range(n)]
    improvement = run_case(a, rhs, 1, 7, F(1, 64), F(2), F(1, 1 << 16))
    need(improvement["fraction_bits"] < improvement["global_fraction_bits"], "strict precision gain")
    lower, upper, counts, expected_ops = symbolic(n, 1)
    uniform = [improvement["global_q"]] * n
    l, u, products = factor(a, lower, upper, uniform)
    need(products == expected_ops == improvement["factor_products"], "matched common-grid work")
    common_x = solve(l, u, uniform, improvement["solve_q"], rhs)
    common_residual = max(abs(sum(a[i][j] * common_x[j] for j in range(n)) - rhs[i]) for i in range(n))
    need(common_residual <= F(1, 64 * (1 << 16)), "matched common-grid accuracy")
    rejected = rejection_checks()
    root = Path(__file__).resolve().parent
    entries = list(islice(root.iterdir(), 9))
    need(len(entries) <= 8, "package entry capacity")
    files = sorted(p for p in entries if p.is_file())
    need(len(files) <= 8 and all(p.stat().st_size <= 1048576 for p in files), "receipt capacity")
    hashes = {p.name: sha256(p.read_bytes()).hexdigest() for p in files}
    print(json.dumps({"status": "PASS_ROW_ADAPTIVE_BAND_PRECISION", "errors": 0,
                      "small_solves": small, "pattern_cases": pattern_cases,
                      "pattern_positions": positions, "rejections": rejected,
                      "improvement": improvement, "files": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
