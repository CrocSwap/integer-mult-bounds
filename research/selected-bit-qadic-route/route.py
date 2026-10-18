"""Exact q-adic row-chart updates, not a physical address compiler.

Apache-2.0. Rational geometry follows Zhihao Chen's retained PR386/PR370
construction, selected through DreamingOfClouds' PR545 and PR589 pipeline.
"""
from fractions import Fraction as F
from math import gcd


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    n = len(a)
    require(1 <= n <= 64 and len(b) == n, "matrix dimension")
    require(all(len(r) == n for r in a + b), "square matrices")
    return [[sum(a[i][k] * b[k][j] for k in range(n))
             for j in range(n)] for i in range(n)]


def selected_reflection(lines, target):
    """Reconstruct the source's first-discovery BFS, stopping at this port."""
    require(len(lines) == 120 and 0 <= target < 120, "root inventory")
    require(all(len(r) == 8 for r in lines), "root dimension")
    maps = {0: identity(8)}
    frontier = [0]
    for _ in range(120):
        if target in maps:
            g = maps[target]
            q = lines[target]
            p = [[F(x * y, 4) for y in q] for x in q]
            a = [r[1:] for r in g]
            return [p[i] + a[i] for i in range(8)] + [
                [a[i][j] for i in range(8)] + [F(0)] * 7
                for j in range(7)]
        following = []
        for i in frontier:
            for j in range(120):
                dot = sum(x * y for x, y in zip(lines[i], lines[j]))
                if j in maps or abs(dot) != 2:
                    continue
                sign = 1 if dot == 2 else -1
                d = [x - sign * y for x, y in zip(lines[i], lines[j])]
                norm = sum(x * x for x in d)
                r = [[F(x == y) - F(2 * d[x] * d[y], norm)
                      for y in range(8)] for x in range(8)]
                maps[j] = multiply(r, maps[i])
                following.append(j)
        frontier = following
    raise ValueError("unreachable root")


def column_program(matrix):
    """If E_k ... E_1 R = I, right multiplication uses E_1^-1 ... E_k^-1."""
    n = len(matrix)
    require(1 <= n <= 15 and all(len(r) == n for r in matrix), "route size")
    z = [list(map(F, r)) for r in matrix]
    ops = []
    for j in range(n):
        pivots = [i for i in range(j, n) if z[i][j]]
        require(bool(pivots), "singular route")
        p = pivots[0]
        if p != j:
            z[p], z[j] = z[j], z[p]
            ops.append(("swap", p, j, F(1)))
        if z[j][j] != 1:
            c = 1 / z[j][j]
            z[j] = [c * x for x in z[j]]
            ops.append(("scale", j, j, 1 / c))
        for i in range(n):
            if i != j and z[i][j]:
                c = -z[i][j]
                z[i] = [x + c * y for x, y in zip(z[i], z[j])]
                ops.append(("add", j, i, -c))
    require(z == identity(n), "elimination endpoint")
    require(len(ops) <= n * (n + 1), "factor capacity")
    return ops


def carry_update(low, high, source_low, source_high, coefficient, q, width, scale):
    """Compute y <- c*y or y <- y+c*x using separate residue and high fields."""
    require(2 <= q < 2**127 and 1 <= width <= 16, "radix/width capacity")
    require(isinstance(coefficient, F), "rational coefficient")
    a, d = coefficient.numerator, coefficient.denominator
    require(max(abs(a).bit_length(), d.bit_length()) <= 16, "coefficient capacity")
    require(gcd(d, q) == 1 and (not scale or gcd(a, q) == 1), "nonunit factor")
    modulus = q ** (width - 1)
    require(0 <= low < q and 0 <= source_low < q, "low field range")
    require(0 <= high < modulus and 0 <= source_high < modulus, "high field range")
    low_numerator = a * low if scale else d * low + a * source_low
    high_numerator = a * high if scale else d * high + a * source_high
    new_low = low_numerator * pow(d, -1, q) % q
    carry, remainder = divmod(low_numerator - d * new_low, q)
    require(remainder == 0, "integral carry")
    new_high = (high_numerator + carry) * pow(d, -1, modulus) % modulus
    return new_low, new_high


def route_fields(fields, program, axes, q, width):
    """Only current_low/current_high are replaced; all other fields are retained."""
    require(1 <= len(axes) <= 15 and len(set(axes)) == len(axes), "route axes")
    require(all(type(i) is int and 0 <= i < 64 for i in axes), "ambient axes")
    require(len(program) <= 240 and len(fields) <= 16, "program/field capacity")
    low, high = fields["current_low"], fields["current_high"]
    require(len(low) == len(high) == 64, "ambient rows")
    require(all(len(r) == 64 for r in low + high), "ambient columns")
    require(2 <= q < 2**127 and 1 <= width <= 16, "radix/width capacity")
    require(all(type(x) is int and 0 <= x < q for r in low for x in r), "low matrix range")
    cap = q ** (width - 1)
    require(all(type(x) is int and 0 <= x < cap for r in high for x in r), "high matrix range")
    low, high = [list(r) for r in low], [list(r) for r in high]
    for kind, dest, src, c in program:
        require(kind in ("swap", "scale", "add"), "unknown operation")
        require(0 <= dest < len(axes) and 0 <= src < len(axes), "operation axes")
        i, j = axes[dest], axes[src]
        require(kind == "scale" or i != j, "aliased operation")
        for row in range(64):
            if kind == "swap":
                low[row][i], low[row][j] = low[row][j], low[row][i]
                high[row][i], high[row][j] = high[row][j], high[row][i]
            else:
                low[row][i], high[row][i] = carry_update(
                    low[row][i], high[row][i], low[row][j], high[row][j],
                    c, q, width, kind == "scale")
    return {**fields, "current_low": low, "current_high": high}


def inverse_program(program):
    require(len(program) <= 240, "program capacity")
    return [(kind, i, j, 1 / c if kind == "scale" else -c if kind == "add" else c)
            for kind, i, j, c in reversed(program)]
