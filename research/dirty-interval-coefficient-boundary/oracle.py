"""Separate recursive prefix oracle; Arham Tahir + Codex, Apache-2.0.
No polynomial engine or expanded-word emitter is imported.
"""
import ast
from fractions import Fraction
from types import SimpleNamespace


def need(condition, message):
    if not condition:
        raise ValueError(message)


def eye(d):
    return [[int(i == j) for j in range(d)] for i in range(d)]


def multiply(a, b):
    columns = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, col)) for col in columns] for row in a]


def inverse(a):
    d = len(a)
    rows = [[Fraction(v) for v in row] + other for row, other in zip(a, eye(d))]
    for j in range(d):
        pivot = next(i for i in range(j, d) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        divisor = rows[j][j]
        rows[j] = [v/divisor for v in rows[j]]
        for i in range(d):
            if i != j:
                q = rows[i][j]
                rows[i] = [v-q*w for v, w in zip(rows[i], rows[j])]
    return [row[d:] for row in rows]


def leaf_count(n):
    q = 1 << (n.bit_length()-1)
    return 3*q*n-2*q*q


def prefix(n, cut, factors):
    d = (n-1).bit_length()+2
    products = [1]
    for v in factors:
        products.append(products[-1]*v)
    need(all(v in (-1, 1) for v in factors), 'oracle scalar isometries')
    def shear(x, y, coefficient):
        result = eye(d); result[y][x] += coefficient
        return result
    def rec(lo, count, x, y, level, boundary):
        need(0 <= boundary <= leaf_count(count), 'prefix cut range')
        full = products[lo+count]*products[lo]
        if boundary == 0:
            return eye(d)
        if boundary == leaf_count(count):
            return shear(x, y, full)
        left = count//2; right = count-left; z = level+2
        lu, lv = leaf_count(left), leaf_count(right)
        b = products[lo+left]*products[lo]
        a = products[lo+count]*products[lo+left]
        u, v = shear(x, z, b), shear(z, y, a)
        if boundary <= lu:
            return rec(lo, left, x, z, level+1, boundary)
        if boundary <= lu+lv:
            return multiply(rec(lo+left, right, z, y, level+1, boundary-lu), u)
        if boundary <= 2*lu+lv:
            child = rec(lo, left, x, z, level+1, lu-(boundary-lu-lv))
            return multiply(child, multiply(shear(x, z, -b), multiply(v, u)))
        child = rec(lo+left, right, z, y, level+1, lv-(boundary-2*lu-lv))
        return multiply(child, shear(x, y, a*b))
    return rec(0, n, 0, 1, 0, cut)


def two_cut(n, factors, a, b, sign=1):
    if sign == -1:
        total = leaf_count(n)
        a, b = total-a, total-b
    return multiply(prefix(n, b, factors), inverse(prefix(n, a, factors)))


def wrong_order(n, factors, a, b):
    return multiply(inverse(prefix(n, a, factors)), prefix(n, b, factors))


def source_events(path, n, sign, alias=False):
    tree = ast.parse(path.read_text())
    functions = [f for f in tree.body if isinstance(f, ast.FunctionDef) and f.name == 'compose']
    need(len(functions) == 1, 'literal compose function')
    ports = [[0] for _ in range((n-1).bit_length()+2)]
    ids = {id(p): i for i, p in enumerate(ports)}
    events = []
    def leaf(x, y, factor, phases, beta, bits, direction, sgn, stats):
        events.append((ids[id(x)], ids[id(y)], factor, sgn))
    environment = {'c': SimpleNamespace(need=need, norm2=lambda x: x*x), 'leaf': leaf}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), 'exec'), environment)
    scratch = ports[2:] if not alias else [ports[0], *ports[3:]]
    environment['compose'](ports[0], ports[1], list(range(n)), scratch, [1], Fraction(1, 2), 64, 1, sign)
    return events
