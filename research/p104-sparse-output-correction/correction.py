"""Construct a literal rank-two correction with restored public accumulators.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The source construction and its original authors keep their credit.
"""
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(dst, src, q):
    for k, v in tuple(src.items()):
        z = dst.get(k, 0) + q*v
        if z:
            dst[k] = z
        else:
            dst.pop(k, None)


def matrix(program, n):
    rows = [{i: Q(1)} for i in range(n)]
    peak = Q(1)
    for e in program:
        need(e[0] in ('ADD', 'SCALE') and e[-1] == 127, 'Correction scalar and frame')
        if e[0] == 'ADD':
            need(e[1] != e[2], 'Distinct operands')
            add(rows[e[1]], rows[e[2]], Q(e[3]))
        else:
            rows[e[1]] = {j: Q(e[2])*x for j, x in rows[e[1]].items()}
        peak = max(peak, sum(abs(x) for x in rows[e[1]].values()))
    return rows, peak


def data(program):
    rows, _ = matrix(program, 770)
    delta = {}
    for i, row in enumerate(rows):
        d = dict(row)
        add(d, {i: Q(1)}, -1)
        if d:
            delta[i] = d
    a = delta[3]
    b = {j: 4*x for j, x in delta[151].items()}
    u = {i: d.get(3, Q(0)) for i, d in delta.items()}
    v = {i: d.get(1, Q(0)) for i, d in delta.items()}
    need(not set(a) & set(b) and len(a) == len(b) == 12, 'Disjoint forms')
    for i, d in delta.items():
        want = {}
        add(want, a, u[i])
        add(want, b, v[i])
        need(want == d, 'Complete rank-two factorization')
    need(all(sum(f.get(i, 0)*g[i] for i in delta) == 0
             for f in (a, b) for g in (u, v)), 'Four invariant pairings')
    need(all(not u[i] or not v[i] or abs(u[i]) == abs(v[i]) for i in delta), 'Four output directions')
    return a, b, u, v


def construct(d, p=3, q=1, x=Q(1), y=Q(1), order=1):
    a, b, u, v = d
    need(p in a and q in b and abs(a[p]) == abs(b[q]) == 1, 'Unit pivots')
    need(order in (-1, 1), 'Direction order')
    need(x and y, 'Nonzero accumulator scales')
    out = []
    def gate(r, s, c):
        if c:
            out.append(['ADD', r, s, str(c), 127])
    def scale(r, c):
        if c != 1:
            out.append(['SCALE', r, str(c), 127])
    for r, f, c in ((p, a, x), (q, b, y)):
        scale(r, c*f[r])
        for j in sorted(f):
            if j != r:
                gate(r, j, c*f[j])
    for i in sorted(u):
        if i in (p, q):
            continue
        if not v[i]:
            gate(i, p, u[i]/x)
        elif not u[i]:
            gate(i, q, v[i]/y)
    gate(p, q, order*x/y)
    for i in sorted(u):
        if u[i] and v[i] == order*u[i]:
            gate(i, p, u[i]/x)
    gate(p, q, -2*order*x/y)
    for i in sorted(u):
        if u[i] and v[i] == -order*u[i]:
            gate(i, p, u[i]/x)
    gate(p, q, order*x/y)
    for r, f, c in ((q, b, y), (p, a, x)):
        for j in sorted(f, reverse=True):
            if j != r:
                gate(r, j, -c*f[j])
        scale(r, 1/(c*f[r]))
    return out


def allowance(program):
    total = 0
    for e in program:
        c = Q(e[-2]); n, d = abs(c.numerator), c.denominator
        need(c and d & (d-1) == 0 and n+d < 65536*d, 'Bounded dyadic coefficient')
        if e[0] == 'SCALE':
            need(n & (n-1) == 0, 'Unit SCALE')
            total += 2*(abs(n.bit_length()-d.bit_length()) + int(c < 0))
        else:
            total += 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
    return total
