#!/usr/bin/env python3
"""Exact checks; universal propositions are proved in the companion note.
CubeJerry with OpenAI ChatGPT assistance. Standard library only.
"""
from fractions import Fraction as F
from itertools import product
import json


def need(ok, label):
    if not ok:
        raise ValueError(label)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    return [[sum(x*y for x, y in zip(r, c)) for c in zip(*b)] for r in a]


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def inverse(a):
    n = len(a)
    a = [[F(x) for x in r]+s for r, s in zip(a, eye(n))]
    for j in range(n):
        p = next(i for i in range(j, n) if a[i][j])
        a[j], a[p] = a[p], a[j]
        q = a[j][j]
        a[j] = [x/q for x in a[j]]
        for i in range(n):
            if i != j and a[i][j]:
                q = a[i][j]
                a[i] = [x-q*y for x, y in zip(a[i], a[j])]
    return [r[n:] for r in a]


def word(qs):
    n = len(qs[0][0]); p = eye(n)
    for x, y in qs:
        need(dot(y, x) == 0, 'square-zero query')
        yp = mm([y], p)[0]
        p = [[p[i][j]-2*x[i]*yp[j] for j in range(n)] for i in range(n)]
    return p


def algebra(qs, coefficient=2):
    n = len(qs[0][0]); size = len(qs)
    x = list(map(list, zip(*(q[0] for q in qs))))
    y = [q[1] for q in qs]
    g = mm(y, x)
    a = [[F(i == j)+(coefficient*g[i][j] if i > j else 0)
          for j in range(size)] for i in range(size)]
    m = mm(x, mm(inverse(a), y))
    predicted = [[F(i == j)-2*m[i][j] for j in range(n)] for i in range(n)]
    return g, a, predicted


def canonical(n):
    need(n % 2 == 0, 'even dimension')
    xs = eye(n)+[[F(-(-1)**i) for i in range(n)]]
    ys = [[F((i > j)-(i < j)) for j in range(n)] for i in range(n+1)]
    return list(zip(xs, ys))


def conjugate(qs):
    n = len(qs[0][0]); b = eye(n)
    for i in range(n-1):
        b[i][i+1] = i+2
    bi = inverse(b); answer = []
    for i, (x, y) in enumerate(qs):
        scale = F((-1)**i*(i+2), i+1)
        xx = [r[0]*scale for r in mm(b, [[v] for v in x])]
        yy = [v/scale for v in mm([y], bi)[0]]
        answer.append((xx, yy))
    return answer


def check(qs):
    n = len(qs[0][0]); size = len(qs)
    need(size == n+1, 'shortest query count')
    p = word(qs)
    need(p == [[F(-int(i == j)) for j in range(n)] for i in range(n)],
         'complete minus-identity endpoint')
    g, a, predicted = algebra(qs)
    need(p == predicted, 'ordered rank-one product formula')
    b = [[a[i][j]-g[i][j] for j in range(size)] for i in range(size)]
    need(all(b[i][j] == b[i][0]*b[0][j] for i in range(size) for j in range(size)),
         'unit-diagonal rank-one displacement')
    need(all(g[i][j]*g[j][i] == -1 for i in range(size) for j in range(i)),
         'all cross-Gram products')
    return size*(size-1)//2


def main():
    cases = products_checked = 0
    for n in range(2, 21, 2):
        for qs in (canonical(n), conjugate(canonical(n))):
            products_checked += check(qs)
            cases += 1
    ul, vl = [F(1), F(0)], [F(1), F(-1)]
    ur, vr = [-v for v in ul], vl[:]
    grid_cases = 0
    for a, b, c, d in product(range(-2, 3), repeat=4):
        uz, vz = [F(a), F(b)], [F(c), F(d)]
        p = dot(vl, uz)*dot(vz, ul)
        q = dot(vr, uz)*dot(vz, ur)
        need(p == -q, 'aligned pair has opposite cross products')
        need(not (p == q == -1), 'three-arm shortest-root contradiction')
        grid_cases += 1
    need(dot(vl, ul)**2 == 1 and dot(vl, ul)**2 != -1,
         'same-sign aligned pair contradicts shortest cross product')
    controls = []
    base = canonical(4)
    mutated = [(x[:], y[:]) for x, y in base]
    mutated[0] = ([2*v for v in mutated[0][0]], mutated[0][1])
    for qs, label in [(mutated, 'uncompensated query scaling'),
                      (base[:-1], 'omitted query')]:
        try:
            check(qs)
        except ValueError:
            controls.append(label)
        else:
            raise ValueError('mutation control survived: '+label)
    _, _, wrong = algebra(base, coefficient=1)
    need(wrong != word(base), 'wrong lower-triangular coefficient detected')
    controls.append('incorrect product-formula coefficient')
    # The shortest hypothesis is essential. Four 2D queries give -I, but
    # repeated queries have zero cross-Gram product.
    u = ([F(1), F(0)], [F(0), F(-1)])
    v = ([F(0), F(1)], [F(1, 2), F(0)])
    longer = [u, v, u, v]
    need(word(longer) == [[F(-1), F(0)], [F(0), F(-1)]], 'longer-root endpoint')
    gl, _, _ = algebra(longer)
    need(gl[0][2]*gl[2][0] == 0, 'n+2-query counterexample to overbroad lemma')
    controls.append('shortest hypothesis is essential: n+2-query root')
    # Without carrier alignment, both third-arm cross products can be -1.
    uz, vz = [F(0), F(1)], [F(1), F(1)]
    unaligned_ur, unaligned_vr = uz, vl
    need(dot(vl, uz)*dot(vz, ul) == -1, 'unaligned left cross product')
    need(dot(unaligned_vr, uz)*dot(vz, unaligned_ur) == -1,
         'unaligned right cross product')
    controls.append('carrier-alignment hypothesis is essential')
    need(len(controls) == 5, 'all negative controls executed')
    print(json.dumps({'schema': 'shortest-root-hub-obstruction/1',
                      'status': 'PASS', 'new_kappa': False,
                      'shortest_root_cases': cases,
                      'exact_cross_products': products_checked,
                      'alignment_grid_cases': grid_cases,
                      'same_sign_alignment_checked': True,
                      'negative_controls': controls}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
