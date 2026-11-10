"""Primitive-decomposition-free commutative multiplication reconstruction."""

from linear import eye, flatten, mm, mv, nullspace, prime, solve, span, transpose
from linear import vector
from model import Algebra, Module, cyclic_part


def validate_tensor(t, p):
    prime(p)
    n = len(t)
    if not 1 <= n <= 4 or any(len(row) != n for row in t):
        raise ValueError("tensor dimension must be in 1..4")
    for row in t:
        for v in row:
            vector(v, n, p)
    return n


def nucleus(t, p):
    n, equations = len(t), []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                row = [0] * (2 * n * n)
                for ell in range(n):
                    row[ell * n + i] = t[ell][j][k]
                    at = n * n + k * n + ell
                    row[at] = (row[at] - t[i][j][ell]) % p
                equations.append(row)
    basis = nullspace(equations, p, 2 * n * n)
    xs = [[v[i * n:(i + 1) * n] for i in range(n)] for v in basis]
    ys = [[v[n * n + i * n:n * n + (i + 1) * n] for i in range(n)]
          for v in basis]
    return xs, ys


def recover_algebra(t, p):
    n = len(t)
    xs, ys = nucleus(t, p)
    if len(xs) != n or any(len(span([flatten(m) for m in side], p, n * n)) != n
                           for side in (xs, ys)):
        return None, "nucleus dimensions/projections"
    if any(mm(x, y, p) != mm(y, x, p) for x in ys for y in ys):
        return None, "noncommutative nucleus"
    right = [[t[i][j][k] for j in range(n)] for i in range(n) for k in range(n)]
    if nullspace(right, p, n):
        return None, "right kernel"
    columns = transpose([flatten(m) for m in ys])
    unit = solve(columns, flatten(eye(n)), p, n)
    table = [[solve(columns, flatten(mm(x, y, p)), p, n) for y in ys] for x in ys]
    if unit is None or any(v is None for row in table for v in row):
        raise ArithmeticError("nucleus closure failed")
    return (Algebra(p, table, unit), xs, ys), None


def bilinear(t, u, v, p):
    n = len(t)
    return [sum(u[i] * v[j] * t[i][j][k] for i in range(n) for j in range(n)) % p
            for k in range(n)]


def recognize(t, p):
    n = validate_tensor(t, p)
    recovered, reason = recover_algebra(t, p)
    if recovered is None:
        return None, reason
    a, xs, ys = recovered
    u, eu, _ = cyclic_part(Module(a, xs))
    w, ew, _ = cyclic_part(Module(a, ys))
    if eu != list(a.unit) or ew != list(a.unit):
        return None, "noncyclic nucleus module"
    first = transpose([mv(x, u, p) for x in xs])
    output = transpose([mv(y, w, p) for y in ys])
    phi = transpose([bilinear(t, u, col, p) for col in eye(n)])
    second_columns = [solve(phi, col, p, n) for col in transpose(output)]
    if any(col is None for col in second_columns):
        raise ArithmeticError("cyclic input slice is not onto")
    cert = {"table": a.table, "unit": a.unit, "U": first,
            "V": transpose(second_columns), "W": output}
    if not check(t, p, cert):
        raise ArithmeticError("recovered factor maps failed")
    return cert, None


def check(t, p, cert):
    n = validate_tensor(t, p)
    a = Algebra(p, cert["table"], cert["unit"])
    if a.n != n:
        return False
    maps = [cert[key] for key in ("U", "V", "W")]
    for matrix in maps:
        if len(matrix) != n:
            return False
        for row in matrix:
            vector(row, n, p)
        if len(span(matrix, p, n)) != n:
            return False
    u, v, w = [transpose(matrix) for matrix in maps]
    return all(bilinear(t, u[i], v[j], p) == mv(cert["W"], a.table[i][j], p)
               for i in range(n) for j in range(n))
