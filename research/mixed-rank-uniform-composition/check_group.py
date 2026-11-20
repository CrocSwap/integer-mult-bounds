"""Finite, independent controls for GROUPED-GAUSSIAN.md. Standard library only."""

from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
from math import prod


def require(condition, message):
    if not condition:
        raise ValueError(message)


def charge():
    k = F(".00387992803556")
    gap = F(1, 10**14)
    eps, beta = 1 - gap, 1 - 3 * gap
    bit, hadamard = k + 4 * gap, k + 3 * gap
    xi = eps * (1 + hadamard) - F(3, 32) + gap
    exponents = {
        "hadamard": eps - hadamard * beta,
        "support": eps - bit * beta,
        "group_scan": eps - beta,
        "boundary": eps + F(29, 32) - xi,
        "union": eps + F(1, 2) - xi,
        "shrinking_halo": eps + beta + 54 - 128,
        "physical_crt_if_admitted": 1 - bit + 2 * (1 - eps),
    }
    margins = {name: 1 - k - power for name, power in exponents.items()}
    require(min(margins.values()) > 0, "power outside budget")
    require(beta > 1 - eps and beta + 2 * (1 - eps) < 1, "archive/dense guard")
    require(F(1, 2) < xi < 1 and beta < eps, "carve/precision")
    naive = F(".003879928035646")
    require(naive / (1 + naive) < k, "unfused transfer negative control")
    require(eps + beta + 3 * 48 - 128 > 1 - k, "old cubic halo tariff negative")
    return {name: str(value) for name, value in margins.items()}


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    cols = tuple(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in cols] for row in a]


def apply(a, x):
    return [sum(w * v for w, v in zip(row, x)) for row in a]


def inverse(a):
    n = len(a)
    aug = [row[:] + right for row, right in zip(a, identity(n))]
    for i in range(n):
        j = next(j for j in range(i, n) if aug[j][i])
        aug[i], aug[j] = aug[j], aug[i]
        divisor = aug[i][i]
        aug[i] = [v / divisor for v in aug[i]]
        for j in range(n):
            if i != j:
                multiplier = aug[j][i]
                aug[j] = [v - multiplier * q for v, q in zip(aug[j], aug[i])]
    return [row[n:] for row in aug]


def sub(a, rows, columns):
    return [[a[i][j] for j in columns] for i in rows]


def ref(r, t):
    """Make two exact dyadic test bands. Decimal chooses finite test data only."""
    q = [(2 * t * j + r) // (2 * r) for j in range(r)]
    selected = set(q)
    h, u = identity(t), identity(t)
    pi = Decimal("3.14159265358979323846264338327950288419716939937510582097")
    alpha = Decimal(2)
    scale = 1 << 17
    with localcontext() as ctx:
        ctx.prec = 65
        rho = Decimal(t) / r
        for j, col in enumerate(q):
            b = rho * j - col
            for v in range(t):
                h[v][col] = F(0)
                u[v][col] = F(0)
                for period in (-1, 0, 1):
                    offset = col + period * t - v
                    if abs(offset) > 1:
                        continue
                    arg = Decimal(offset) + b
                    broad = (-pi * (arg / rho / alpha) ** 2).exp() / alpha
                    u[v][col] += F(int(scale * broad), scale)
                    if v in selected:
                        narrow = (-pi * alpha ** 2 * (arg**2 - b**2)).exp()
                        h[v][col] += F(int(scale * narrow), scale)
                if v == col:
                    h[v][col] = F(1)
    require(q[0] == 0 and all(a < b for a, b in zip(q, q[1:])), "q image")
    require(u[0][-1] > 0 and u[-1][0] > 0, "cross-period columns lost")
    require(any(i not in selected for i in range(t)), "holes empty")
    return h, u, selected


def five(q, interior, x, inv):
    """Evaluate the five suboperators, rightmost first, including dirty fields."""
    boundary = [i for i in range(len(q)) if i not in interior]
    a = sub(q, interior, interior)
    ai = inverse(a)
    b = sub(q, interior, boundary)
    c = sub(q, boundary, interior)
    d = sub(q, boundary, boundary)
    fill = multiply(multiply(c, ai), b)
    f = [[u - v for u, v in zip(row, term)] for row, term in zip(d, fill)]
    u = [x[i] for i in interior]
    v = [x[i] for i in boundary]
    if inv:
        u = apply(ai, u)
        v = [w - z for w, z in zip(v, apply(c, u))]
        u, v = apply(a, u), apply(inverse(f), v)
        u = [w - z for w, z in zip(u, apply(b, v))]
        u = apply(ai, u)
    else:
        u = apply(a, u)
        u = [w + z for w, z in zip(u, apply(b, v))]
        u, v = apply(ai, u), apply(f, v)
        v = [w + z for w, z in zip(v, apply(c, u))]
        u = apply(a, u)
    out = [F(0)] * len(q)
    for indices, values in ((interior, u), (boundary, v)):
        for i, value in zip(indices, values):
            out[i] = value
    return out


def infinity(q):
    return max(sum(abs(v) for v in row) for row in q)


def splice(h, u, selected):
    n, side, halo, terms = len(h), 16, 3, 3
    require(n == 32, "fixture shape")
    x = [F(2 * ((i * i + 7 * i + 1) % 19) - 17, 27) for i in range(n)]
    require(any(x[i] != 0 for i in range(n) if i not in selected), "dirty holes")
    e = [[F(i == j) - h[i][j] for j in range(n)] for i in range(n)]
    rho = infinity(e)
    require(0 < rho < 1, "strict row gap")
    neumann = x[:]
    for _ in range(terms - 1):
        neumann = [v + q for v, q in zip(x, apply(e, neumann))]
    direct_inverse, direct_broad = apply(inverse(h), x), apply(u, x)
    checked, kept, faces = 0, 0, 0
    largest_error = F(0)
    for start in range(0, n, side):
        rows = list(range(start, start + side))
        interior = [i for i in range(2, side - 2)
                    if i % 6 in (2, 3) and start + i in selected]
        for matrix, inv in ((h, True), (u, False)):
            section = sub(matrix, rows, rows)
            computed = five(section, interior, x[start:start + side], inv)
            oracle = apply(inverse(section) if inv else section, x[start:start + side])
            require(computed == oracle, "five factors changed sectional endpoint")
            checked += len(computed)
            for i, actual in enumerate(computed):
                global_i = start + i
                face = min(i, side - 1 - i) < halo
                if inv:
                    result = neumann[global_i] if face else actual
                    error = abs(result - direct_inverse[global_i])
                    limit = (1 if face else 2) * max(map(abs, x)) * rho**terms / (1 - rho)
                    require(error <= limit, "global inverse error above Neumann proof")
                    largest_error = max(largest_error, error)
                    kept += int(not face)
                    faces += int(face)
                else:
                    result = direct_broad[global_i] if face else actual
                    require(result == direct_broad[global_i], "forward halo splice")
    require(any(neumann[i] != direct_inverse[i] for i in range(n)), "Neumann control vacuous")
    return checked, kept, faces, str(float(largest_error))


def flags():
    masks = [{1, 3}, {0, 1, 5}, {2, 3}, {2, 4, 5}]
    radices = (7, 6, 5, 7)
    classes = {}
    visits = 0
    for point in product(*(range(n) for n in radices)):
        active = [i for i, v in enumerate(point) if v in masks[i]]
        for visit, i in enumerate(active):
            key = (visit, i)
            classes.setdefault(key, set()).add(point[:i] + point[i+1:])
            visits += 1
    for (_, i), lines in classes.items():
        require(len(lines) >= prod(min(len(masks[j]), radices[j] - len(masks[j]))
                                   for j in range(len(masks)) if j != i),
                "rare tag lacks full RHS set")
    expected = sum(len(masks[i]) * prod(radices[:i] + radices[i+1:])
                   for i in range(len(masks)))
    require(visits == expected, "union tariff")
    return len(classes), min(map(len, classes.values())), visits


if __name__ == "__main__":
    print("exact power margins", charge())
    print("finite structural axis test reports", splice(*ref(29, 32)), splice(*ref(31, 32)))
    print("sparse tag classes, smallest RHS count, total visits", flags())
