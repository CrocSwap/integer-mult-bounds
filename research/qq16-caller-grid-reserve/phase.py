"""Exact quadratic phase kernels over binary addresses; ywz65 + OpenAI Codex.

Apache-2.0. Rank and Gaussian sums use integer arithmetic, not dense payloads.
"""
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def polynomial(terms, n):
    a, edges = [0]*n, [0]*n
    for vector, coefficient in terms:
        need(type(vector) is int and 0 <= vector < 1 << n, 'phase vector domain')
        bits = [i for i in range(n) if vector >> i & 1]
        for i in bits:
            a[i] = (a[i]+coefficient) % 4
        if coefficient % 2:
            for i in bits:
                for j in bits:
                    if j > i:
                        edges[i] ^= 1 << j
                        edges[j] ^= 1 << i
    return tuple(a), tuple(edges)


def evaluate(a, edges, x):
    value = sum(ai for i, ai in enumerate(a) if x >> i & 1)
    for i in range(len(a)):
        if x >> i & 1:
            value += 2*((edges[i] & x) >> (i+1)).bit_count()
    return value % 4


def rref(rows, n):
    rows = list(rows)
    pivots = []
    for j in range(n):
        k = next((k for k in range(len(pivots), len(rows)) if rows[k] >> j & 1), None)
        if k is None:
            continue
        at = len(pivots)
        rows[k], rows[at] = rows[at], rows[k]
        for k in range(len(rows)):
            if k != at and rows[k] >> j & 1:
                rows[k] ^= rows[at]
        pivots.append(j)
    return rows, pivots


def polarization(a, edges):
    return tuple(row | ((a[i] % 2) << i) for i, row in enumerate(edges))


def rank(a, edges):
    return len(rref(polarization(a, edges), len(a))[1])


def support_character(a, edges):
    """One nonzero Fourier coefficient, found from the radical character."""
    n = len(a)
    rows, pivots = rref(polarization(a, edges), n)
    radical = []
    for j in range(n):
        if j not in pivots:
            h = 1 << j
            for row, p in zip(rows, pivots):
                if row >> j & 1:
                    h |= 1 << p
            radical.append(h)
    equations = []
    for h in radical:
        q = evaluate(a, edges, h)
        need(q % 2 == 0, 'quadratic phase is even on its radical')
        equations.append(h | ((q//2) << n))
    equations, pivots = rref(equations, n)
    need(all(row != 1 << n for row in equations), 'inconsistent radical character')
    return sum(((row >> n) & 1) << p for row, p in zip(equations, pivots))


def gaussian(a, edges, character=0):
    """Normalized exact Fourier coefficient by one/two-variable elimination."""
    n = len(a)
    a = [(v-2*((character >> i) & 1)) % 4 for i, v in enumerate(a)]
    edges = list(edges)
    active = set(range(n))
    factor = (1, 0)

    def times(z):
        nonlocal factor
        factor = (factor[0]*z[0]-factor[1]*z[1], factor[0]*z[1]+factor[1]*z[0])

    def remove(i):
        active.remove(i)
        for j in active:
            edges[j] &= ~(1 << i)

    while active:
        odd = next((i for i in sorted(active) if a[i] % 2), None)
        if odd is not None:
            ai = a[odd]
            neighbors = [j for j in sorted(active) if edges[odd] >> j & 1]
            times((1, 1 if ai == 1 else -1))
            for j in neighbors:
                a[j] = (a[j]-ai) % 4
            for j in neighbors:
                for k in neighbors:
                    if j < k:
                        edges[j] ^= 1 << k
                        edges[k] ^= 1 << j
            remove(odd)
            continue
        pair = next(((i, j) for i in sorted(active) for j in sorted(active)
                     if i < j and edges[i] >> j & 1), None)
        if pair is None:
            if any(a[i] for i in active):
                return Q(0), Q(0)
            times((1 << len(active), 0))
            break
        i, j = pair
        alpha, beta = a[i]//2, a[j]//2
        left = [k for k in active if k != j and edges[i] >> k & 1]
        right = [k for k in active if k != i and edges[j] >> k & 1]
        times((-2 if alpha*beta else 2, 0))
        for k in left:
            a[k] = (a[k]+2*beta) % 4
        for k in right:
            a[k] = (a[k]+2*alpha) % 4
        for k in left:
            for ell in right:
                if k == ell:
                    a[k] = (a[k]+2) % 4
                else:
                    edges[k] ^= 1 << ell
                    edges[ell] ^= 1 << k
        remove(i)
        remove(j)
    return Q(factor[0], 1 << n), Q(factor[1], 1 << n)


def witness(a, edges):
    r = rank(a, edges)
    character = support_character(a, edges)
    real, imag = gaussian(a, edges, character)
    need(real*real+imag*imag == Q(1, 1 << r), 'Gaussian amplitude does not match phase rank')
    bits = max(real.denominator.bit_length(), imag.denominator.bit_length())-1
    need(bits == (r+1)//2, 'Gaussian dyadic exponent')
    return {'rank': r, 'bits': bits, 'character': character, 'real': str(real), 'imag': str(imag)}
