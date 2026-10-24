"""Exact corroboration of the new centralizer formula; standard library only."""

import hashlib
import itertools
import json
import platform
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Matrix:
    n: int
    m: int
    rows: tuple

    def __post_init__(self):
        require(0 <= self.n <= 8 and 0 <= self.m <= 8, "matrix capacity")
        require(len(self.rows) == self.n, "row count")
        require(all(len(row) == self.m for row in self.rows), "column count")


def matrix(n, m, entries):
    values = tuple(entries)
    require(len(values) == n * m, "entry count")
    return Matrix(n, m, tuple(values[i*m:(i+1)*m] for i in range(n)))


def identity(n):
    return matrix(n, n, (int(i == j) for i in range(n) for j in range(n)))


def multiply(a, b, q):
    require(a.m == b.n, "product dimensions")
    return matrix(a.n, b.m, (
        sum(a.rows[i][k] * b.rows[k][j] for k in range(a.m)) % q
        for i in range(a.n) for j in range(b.m)))


def transpose(a):
    return matrix(a.m, a.n, (a.rows[i][j] for j in range(a.m) for i in range(a.n)))


def horizontal(a, b):
    require(a.n == b.n, "horizontal dimensions")
    return Matrix(a.n, a.m+b.m, tuple(x+y for x, y in zip(a.rows, b.rows)))


def vertical(a, b):
    require(a.m == b.m, "vertical dimensions")
    return Matrix(a.n+b.n, a.m, a.rows+b.rows)


def block_diagonal(a, b):
    rows = tuple(row+(0,)*b.m for row in a.rows)
    rows += tuple((0,)*a.m+row for row in b.rows)
    return Matrix(a.n+b.n, a.m+b.m, rows)


def reduce_rows(a, q):
    rows = [list(row) for row in a.rows]
    pivots = []
    for col in range(a.m):
        if len(pivots) == a.n:
            break
        candidates = [i for i in range(len(pivots), a.n) if rows[i][col]]
        if not candidates:
            continue
        pos = len(pivots)
        selected = candidates[0]
        rows[pos], rows[selected] = rows[selected], rows[pos]
        scale = pow(rows[pos][col], -1, q)
        rows[pos] = [x * scale % q for x in rows[pos]]
        for i in range(a.n):
            if i != pos:
                factor = rows[i][col]
                rows[i] = [(x-factor*y) % q for x, y in zip(rows[i], rows[pos])]
        pivots.append(col)
    return Matrix(a.n, a.m, tuple(tuple(row) for row in rows)), tuple(pivots)


def rank(a, q):
    return len(reduce_rows(a, q)[1])


def inverse(a, q):
    require(a.n == a.m, "inverse dimensions")
    reduced, pivots = reduce_rows(horizontal(a, identity(a.n)), q)
    require(pivots == tuple(range(a.n)), "singular inverse")
    return Matrix(a.n, a.n, tuple(row[a.n:] for row in reduced.rows))


def factor(projector, q):
    n = projector.n
    pivots = reduce_rows(projector, q)[1]
    r = len(pivots)
    x = matrix(n, r, (projector.rows[i][j] for i in range(n) for j in pivots))
    chosen = reduce_rows(transpose(x), q)[1]
    square = Matrix(r, r, tuple(x.rows[i] for i in chosen))
    selected = Matrix(r, n, tuple(projector.rows[i] for i in chosen))
    y = multiply(inverse(square, q), selected, q)
    require(multiply(x, y, q) == projector, "factor reconstruction")
    require(multiply(y, x, q) == identity(r), "projector factor identity")
    return x, y


def gl_order(n, q):
    value = 1
    for i in range(n):
        value *= q**n - q**i
    return value


@lru_cache(maxsize=20)
def general_linear(n, q):
    require(q in (2, 3, 5) and q**(n*n) <= 65536, "enumeration capacity")
    result = tuple(a for entries in itertools.product(range(q), repeat=n*n)
                   if rank(a := matrix(n, n, entries), q) == n)
    require(len(result) == gl_order(n, q), "GL enumeration")
    return result


def data(p, t, q):
    x, y = factor(p, q)
    z, w = factor(t, q)
    c_map, d_map = horizontal(x, z), vertical(y, w)
    m_map = multiply(d_map, c_map, q)
    a, b, c = rank(c_map, q), rank(d_map, q), rank(m_map, q)
    return c_map, d_map, m_map, a-c, b-c, p.n-a-b+c, x.m, z.m


def factor_stabilizer(c_map, d_map, m_map, r, s, q):
    a, b = rank(c_map, q), rank(d_map, q)
    count = 0
    for left in general_linear(r, q):
        for right in general_linear(s, q):
            g = block_diagonal(left, right)
            if multiply(m_map, g, q) != multiply(g, m_map, q):
                continue
            if rank(vertical(c_map, multiply(c_map, g, q)), q) != a:
                continue
            if rank(horizontal(d_map, multiply(g, d_map, q)), q) != b:
                continue
            count += 1
    require(count > 0, "identity missing from factor stabilizer")
    return count


def predicted(p, t, q):
    c_map, d_map, m_map, h, j, z, r, s = data(p, t, q)
    require(min(h, j, z) >= 0, "negative decomposition dimension")
    stabilizer = factor_stabilizer(c_map, d_map, m_map, r, s, q)
    value = stabilizer * gl_order(z, q) * q**(h*j + h*z + j*z)
    return value, (h, j, z, stabilizer)


def fixed_first_centralizer(n, r, q):
    return tuple(block_diagonal(a, b) for a in general_linear(r, q)
                 for b in general_linear(n-r, q))


def census(n, r, s, q):
    require(n <= 4 and q**(n*n) <= 65536, "projector domain capacity")
    p = matrix(n, n, (int(i == j and i < r) for i in range(n) for j in range(n)))
    ambient = fixed_first_centralizer(n, r, q)
    count, histogram, mutations = 0, {}, {}
    for entries in itertools.product(range(q), repeat=n*n):
        t = matrix(n, n, entries)
        if multiply(t, t, q) != t or rank(t, q) != s:
            continue
        expected, (h, j, z, stabilizer) = predicted(p, t, q)
        actual = sum(multiply(f, t, q) == multiply(t, f, q) for f in ambient)
        require(actual == expected, f"centralizer mismatch: {(n,r,s,q,t)}")
        require(gl_order(n, q) % actual == 0, "nonintegral orbit")
        divisors = {"omit_hj": q**(h*j), "omit_hz": q**(h*z),
                    "omit_jz": q**(j*z), "omit_GLz": gl_order(z, q),
                    "omit_factor_stabilizer": stabilizer}
        for name, divisor in divisors.items():
            if divisor > 1 and name not in mutations:
                require(actual != expected // divisor, "omission survived direct count")
                mutations[name] = {"actual": actual, "mutant": expected // divisor,
                                   "h": h, "j": j, "z": z}
        histogram[actual] = histogram.get(actual, 0) + 1
        count += 1
    total = gl_order(n, q) // (gl_order(s, q)*gl_order(n-s, q))
    require(count == total, "incomplete projector census")
    return {"q": q, "n": n, "r": r, "s": s, "pairs": count,
            "centralizer_histogram": histogram, "omission_controls": mutations}


def fixture_checks():
    fixtures = []
    p0 = matrix(3, 3, (1, 1, 0, 0, 0, 0, 0, 0, 0))
    t0 = matrix(3, 3, (0, 0, 0, 1, 1, 1, 0, 0, 0))
    for q in (2, 3, 5):
        for z in (0, 1):
            zero = matrix(z, z, (0 for _ in range(z*z)))
            p, t = block_diagonal(p0, zero), block_diagonal(t0, zero)
            actual, (h, j, padding, stabilizer) = predicted(p, t, q)
            require((h, j, padding, stabilizer) == (1, 1, z, q-1), "sharp fixture")
            expected = (q-1)*gl_order(z, q)*q**(1+2*z)
            require(actual == expected, "sharp fixture order")
            fixtures.append({"q": q, "z": z, "centralizer": actual})
    require(gl_order(0, 2) == 1, "zero-dimensional GL")
    try:
        general_linear(4, 3)
    except ValueError:
        pass
    else:
        raise ValueError("oversized enumeration admitted")
    return fixtures


def main():
    domains = ((4, 1, 1, 2), (4, 2, 2, 2), (3, 1, 2, 3),
               (2, 0, 1, 5), (2, 1, 0, 5), (2, 1, 2, 5), (2, 2, 1, 5))
    checks = [census(*domain) for domain in domains]
    fixtures = fixture_checks()
    omitted = {name for check in checks for name in check["omission_controls"]}
    require(omitted == {"omit_hj", "omit_hz", "omit_jz", "omit_GLz",
                        "omit_factor_stabilizer"}, "missing omission control")
    package = Path(__file__).resolve().parent
    hashes = {name: hashlib.sha256((package/name).read_bytes()).hexdigest()
              for name in ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")}
    print(json.dumps({"status": "PASS_IDEMPOTENT_STABILIZER_MULTIPLICITY",
                      "python": platform.python_version(), "checks": checks,
                      "fixtures": fixtures, "distinct_omissions_rejected": len(omitted),
                      "oversized_domain_rejected": True,
                      "source_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
