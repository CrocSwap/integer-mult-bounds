"""Rigidity modulo trivial motions and the #2162 section-5 order-2 test, on unit-world configurations.
Uses implementation A (lib/jet.py).
Order-2 test (as #2162 group e): for an immovable harmonic line t with flow c (sum_e c_e A_e = delta'_t), the
order-2 diagonal coefficient under order-2 incidence vanishing (A_e(X2, Y2) = b_e := X1(t_e).Y1(s_e)) is the
quadratic Q_t(X1, Y1) = X1(t).Y1(t) + sum_e c_e b_e on the first-order solution space V. If Q_t is identically zero
as a polynomial on V, the order-2 diagonal of t vanishes for every jet over every field of characteristic 2.
Written for this package (thakrarsagar, with AI assistance from Claude Opus 5.5). Apache-2.0."""
from jet import Jet, rank_of, supp


def nullspace(rows, n):
    piv = {}  # pivot column -> fully reduced row
    for m in rows:
        for c, r in piv.items():
            if m >> c & 1:
                m ^= r
        if not m:
            continue
        c = m.bit_length() - 1
        for c2 in list(piv):
            if piv[c2] >> c & 1:
                piv[c2] ^= m
        piv[c] = m
    basis = []
    for f in range(n):
        if f in piv:
            continue
        v = 1 << f
        for c, r in piv.items():
            if r >> f & 1:
                v |= 1 << c
        basis.append(v)
    return basis


def rigid(J):
    """True iff the (J1) solution space equals the span of the explicit gauge + torus motions."""
    return J.n - J.eliminate() == rank_of(J.gauge_torus())


def beta(J, u, w, t, flow):
    """Bilinear form whose quadratic is Q_t: u^X(t).w^Y(t) + sum over flow edges (a, b) of u^X(a).w^Y(b)."""
    def d(a, b):
        s = 0
        for i in supp(J.lines[a][0]) & supp(J.lines[b][1]):
            s ^= (u >> J.var[('X', a, i)] & 1) & (w >> J.var[('Y', b, i)] & 1)
        return s
    r = d(t, t)
    for k in flow:
        a, b, _ = J.inc[k]
        r ^= d(a, b)
    return r


def order2_vanishes(J, t, V=None, drop_diagonal=False):
    """Q_t identically zero as a polynomial on V (diagonal and symmetrised off-diagonal coefficients all zero).
    drop_diagonal=True removes the X1(t).Y1(t) term (negative control: the test must then see a nonzero form)."""
    if V is None:
        V = nullspace(J.rows(), J.n)
    fl = J.flow(t)
    assert fl is not None
    if drop_diagonal:
        B = [[beta(J, u, w, t, fl) ^ beta(J, u, w, t, []) for w in V] for u in V]
    else:
        B = [[beta(J, u, w, t, fl) for w in V] for u in V]
    return all(B[k][k] == 0 for k in range(len(V))) and all(
        B[k][l] == B[l][k] for k in range(len(V)) for l in range(k + 1, len(V))), len(V)
