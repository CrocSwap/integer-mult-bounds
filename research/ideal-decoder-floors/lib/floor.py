"""Theorem 4 machinery (exact): for a unit with live roots R (rows, a T-dimensional span) and its dense pairing B, factor B = X Y^T over F2
(rank k+1), form the subspaces W_z = span{ r_t : t live, x_t . z = 1 } of the root span, the finitely many 'types' S (proper sums of W_z's), the
deficiency sets Def(S) = { z : W_z <= S } and the term rank  r(S_row, S_col) = dim U - dim(U cap Def_col),  U = Def_row^perp  (F2).
r_min = min over type pairs.  Everything is exact (Fractions / F2 bit operations); no floating point."""
import itertools
from exact import rank_f2, rref, in_span
from units import gram, bmasks


def par(a, b):
    return bin(a & b).count('1') & 1


def f2_factor(Brows):
    """Rank factorisation of the F2 matrix with bit rows `Brows`: returns k1, X (row labels, ints), basis (bit rows) with Brows[t] = xor of basis[i] for bits i of X[t]."""
    basis, piv = [], []
    for r in Brows:
        x = r
        for b, p in zip(basis, piv):
            if x >> p & 1:
                x ^= b
        if x:
            p = x.bit_length() - 1
            for i in range(len(basis)):
                if basis[i] >> p & 1:
                    basis[i] ^= x
            basis.append(x)
            piv.append(p)
    k1 = len(basis)
    X = []
    for r in Brows:
        c = 0
        for i, (b, p) in enumerate(zip(basis, piv)):
            if r >> p & 1:
                c |= 1 << i
        X.append(c)
    return k1, X, basis


def labels(Brows):
    k1, X, basis = f2_factor(Brows)
    n = len(Brows)
    Y = [sum(((basis[i] >> s) & 1) << i for i in range(k1)) for s in range(n)]
    # B = X Y^T over F2
    assert all((par(X[t], Y[s])) == (Brows[t] >> s & 1) for t in range(n) for s in range(n))
    return k1, X, Y


def types_and_defs(L, live, Z, k1, T):
    """Subspaces W_z (z in F2^k1 \\ 0) of the root span from the labels Z, the closure of proper W_z under proper sums, Def sets of each type."""
    W = {}
    for z in range(1, 1 << k1):
        O = [t for t in live if par(Z[t], z)]
        W[z] = rref([L[t] for t in O]) if O else ()
    proper = {z for z in W if len(W[z]) < T}
    full = {len(W[z]) for z in W if z not in proper}
    assert all(len(W[z]) == T for z in W if z not in proper)
    Ss = {()}
    for z in proper:
        Ss.add(W[z])
    changed = True
    while changed:
        changed = False
        for a, b in itertools.combinations(list(Ss), 2):
            if not a or not b:
                continue
            c = rref(list(a) + list(b))
            if len(c) < T and c not in Ss:
                Ss.add(c)
                changed = True
        assert len(Ss) < 20000
    types = sorted(Ss, key=lambda s: (len(s), s))
    defs = []
    for S in types:
        D = {0}
        for z in range(1, 1 << k1):
            w = W[z]
            if not w or all(in_span(S, row) for row in w) if S else not w:
                D.add(z)
        defs.append(D)
    return types, defs, len(proper)


def pair_rank(dx, dy, k1):
    UR = [u for u in range(1 << k1) if all(par(u, z) == 0 for z in dx)]
    dU = rank_f2(UR)
    inter = [u for u in UR if u in dy]
    return dU - rank_f2(inter)


def analyse(L, dead, T):
    """Returns dict with k1, #proper W_z (row side, col side), #types, r_min, and the full pair-rank table."""
    n = len(L)
    G = gram(L)
    Br = bmasks(G)
    live = [t for t in range(n) if t not in dead]
    k1, X, Y = labels(Br)
    tx, dx, px = types_and_defs(L, live, X, k1, T)
    ty, dy, py = types_and_defs(L, live, Y, k1, T)
    table = {}
    for i, a in enumerate(dx):
        for j, b in enumerate(dy):
            table[(i, j)] = pair_rank(a, b, k1)
    rmin = min(table.values())
    return dict(v=len(live), T=T, k1=k1, proper=(px, py), types=(len(tx), len(ty)), rmin=rmin, floor=T * rmin, table=table,
                tx=tx, ty=ty, dx=dx, dy=dy, X=X, Y=Y)


def max_orthogonal(G, live, cap):
    """Size of a largest set of pairwise orthogonal lines among `live` (stops once `cap` is reached; cap is a valid upper bound = T)."""
    best = [0]

    def rec(cur, cand):
        if len(cur) > best[0]:
            best[0] = len(cur)
        if best[0] >= cap:
            return True
        if len(cur) + len(cand) <= best[0]:
            return False
        for i, c in enumerate(cand):
            if rec(cur + [c], [d for d in cand[i + 1:] if G[c][d] == 0]):
                return True
        return False
    rec([], list(live))
    return best[0]
