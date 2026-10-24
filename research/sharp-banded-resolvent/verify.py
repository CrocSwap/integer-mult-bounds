#!/usr/bin/env python3
"""Check the support envelope. Ali Romman / OpenAI Codex. Apache-2.0."""
from fractions import Fraction as F
from itertools import product
import json
import random


def require(value, message):
    if not value:
        raise ValueError(message)


def inverse(a):
    n = len(a)
    t = [[F(x) for x in row] + [F(i == j) for j in range(n)] for i, row in enumerate(a)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if t[i][j])
        t[j], t[pivot] = t[pivot], t[j]
        c = t[j][j]
        t[j] = [x / c for x in t[j]]
        for i in range(n):
            if i != j:
                c = t[i][j]
                t[i] = [x - c*y for x, y in zip(t[i], t[j])]
    return [row[n:] for row in t]


def distances(edges, root):
    n = len(edges)
    d = [None] * n
    d[root] = 0
    queue = [root]
    for j in queue:
        for i in range(n):
            if edges[i][j] and d[i] is None:
                d[i] = d[j] + 1
                queue.append(i)
    return d


def envelope(edges, rho):
    require(F(0) < rho < F(1), "rho must be in (0,1)")
    require(all(edges[i][i] for i in range(len(edges))), "diagonal support is required")
    return [sum((rho**d for d in distances(edges, j) if d is not None), F(0)) / (1-rho)
            for j in range(len(edges))]


def route(edges, root, rho):
    d = distances(edges, root)
    n = len(edges)
    e = [[F(0)] * n for _ in range(n)]
    e[root][root] = rho
    for i in range(n):
        if i != root and d[i] is not None:
            j = next(j for j in range(n) if edges[i][j] and d[j] == d[i] - 1)
            e[i][j] = rho
    return e


def resolvent(e):
    return inverse([[F(i == j)-x for j, x in enumerate(row)] for i, row in enumerate(e)])


def check_matrix(edges, e, rho):
    require(all(sum(map(abs, row)) <= rho for row in e), "row budget")
    require(all(not e[i][j] or edges[i][j] for i in range(len(e)) for j in range(len(e))), "support")
    r = resolvent(e)
    for j, bound in enumerate(envelope(edges, rho)):
        require(sum(abs(row[j]) for row in r) <= bound, "column bound")
    return r


def main():
    graph_roots = 0
    for n in range(1, 4):
        off = [(i, j) for i in range(n) for j in range(n) if i != j]
        for bits in product((0, 1), repeat=len(off)):
            edges = [[i == j for j in range(n)] for i in range(n)]
            for (i, j), bit in zip(off, bits):
                edges[i][j] = bool(bit)
            for rho in (F(1, 3), F(2, 3)):
                for root, bound in enumerate(envelope(edges, rho)):
                    r = check_matrix(edges, route(edges, root, rho), rho)
                    require(sum(row[root] for row in r) == bound, "attainment")
                    d = distances(edges, root)
                    require(all(r[i][root] == (0 if d[i] is None else rho**d[i]/(1-rho))
                                for i in range(n)), "individual entries")
                    graph_roots += 1
    rng = random.Random(104100)
    for _ in range(120):
        n = rng.randrange(2, 9)
        edges = [[i == j or rng.choice((False, True)) for j in range(n)] for i in range(n)]
        raw = [[F(rng.randrange(-3, 4) if edges[i][j] else 0) for j in range(n)] for i in range(n)]
        rho = F(3, 4)
        e = [[rho*x/max(F(1), sum(map(abs, row))) for x in row] for row in raw]
        check_matrix(edges, e, rho)
    banded = 0
    for b, m, rho in product(range(1, 4), range(1, 5), (F(1, 2), F(3, 4))):
        n = 2*b*m+1
        edges = [[abs(i-j) <= b for j in range(n)] for i in range(n)]
        r = check_matrix(edges, route(edges, b*m, rho), rho)
        column = [row[b*m] for row in r]
        finite = (1 + 2*b*sum((rho**k for k in range(1, m+1)), F(0)))/(1-rho)
        require(sum(column) == finite, "finite line formula")
        infinite = 1/(1-rho) + 2*b*rho/(1-rho)**2
        require(infinite-finite == 2*b*rho**(m+1)/(1-rho)**2, "exact deficit")
        require(sum(x*x for x in column) == (1+2*b*sum((rho**(2*k) for k in range(1,m+1)),F(0)))/(1-rho)**2,
                "spectral lower certificate")
        banded += 1
    controls = 0
    for rho in (F(0), F(1), F(-1)):
        try:
            envelope([[True]], rho)
        except ValueError:
            controls += 1
        else:
            raise ValueError("bad rho accepted")
    try:
        envelope([[False]], F(1, 2))
    except ValueError:
        controls += 1
    else:
        raise ValueError("missing loop accepted")
    e = [[F(1, 2), F(0), F(0)], [F(1, 2), F(0), F(0)], [F(1, 2), F(0), F(0)]]
    r = resolvent(e)
    require(sum(row[0] for row in r) > 2, "row-only inverse-1 shortcut must fail")
    require(sum(row[0]**2 for row in r) > 4, "row-only inverse-2 shortcut must fail")
    controls += 2
    print("PASS_SHARP_BANDED_RESOLVENT " + json.dumps({"directed_graph_roots": graph_roots,
          "signed_matrices": 120, "banded_instances": banded, "controls": controls,
          "kappa_changed": False}, sort_keys=True))


if __name__ == "__main__":
    main()
