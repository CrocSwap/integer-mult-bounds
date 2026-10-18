"""Frame-universal char-2 realisation (written for this package).

Given a configuration over Q in frame coordinates (points P[i], lines L[k], primitive integer vectors), search GF(2^k)
for X[i], Y[k] (projective, first nonzero coordinate 1) with
    supp X[i] <= supp P[i],  supp Y[k] <= supp L[k],
    X[i].Y[k] = 0 whenever P[i].L[k] = 0,   X[i].Y[k] != 0 whenever P[i].L[k] != 0.
Such an (X, Y) gives, for EVERY decoder configuration whose pairs are (P[i], L[k]) with P[i].L[k] != 0 (any v, repetitions
allowed), the assignment P~(t) = X[point(t)], Q~(t) = Y[line(t)], which satisfies the hypotheses of Lemma CR2 of #2162
(supports, every in-block incidence, nonzero diagonal); hence cost(B) >= v for every admissible B (conditional on CR2).
Exhaustive MRV depth-first search with forward checking; returns a dict, None (exhausted: no realisation), or 'timeout'.
"""
import itertools

IRR = {1: 0b11, 2: 0b111, 3: 0b1011, 4: 0b10011, 5: 0b100101}


def gf_tables(k):
    q = 1 << k; m = IRR[k]
    mul = [[0] * q for _ in range(q)]
    for a in range(q):
        for b in range(q):
            r = 0; x = a; y = b
            while y:
                if y & 1:
                    r ^= x
                y >>= 1; x <<= 1
                if x & q:
                    x ^= m
            mul[a][b] = r
    return mul


def gdot(mul, a, b):
    return mul[a[0]][b[0]] ^ mul[a[1]][b[1]] ^ mul[a[2]][b[2]]


def domain(q, supp):
    out = []
    for v in itertools.product(range(q), repeat=3):
        if not any(v) or any(v[j] and j not in supp for j in range(3)):
            continue
        if next(x for x in v if x) != 1:
            continue
        out.append(v)
    return out


def universal_realise(P, L, k, limit=10 ** 6, relax=()):
    """relax: (point, line) index pairs left unconstrained (used only for the obstruction analysis)."""
    q = 1 << k; mul = gf_tables(k)
    n_p, n_l = len(P), len(L)
    var = [('p', i) for i in range(n_p)] + [('l', j) for j in range(n_l)]
    supp = {('p', i): {j for j in range(3) if P[i][j]} for i in range(n_p)}
    supp.update({('l', j): {c for c in range(3) if L[j][c]} for j in range(n_l)})
    dom = {x: domain(q, supp[x]) for x in var}
    zero = {}
    for i in range(n_p):
        for j in range(n_l):
            z = sum(a * b for a, b in zip(P[i], L[j])) == 0
            if (i, j) in relax:
                z = None
            zero[(('p', i), ('l', j))] = z; zero[(('l', j), ('p', i))] = z
    nbrs = {x: [y for y in var if y[0] != x[0]] for x in var}
    asg = {}; nodes = [0]

    def dfs(doms):
        nodes[0] += 1
        if nodes[0] > limit:
            raise TimeoutError
        free = [x for x in var if x not in asg]
        if not free:
            return True
        best = min(free, key=lambda x: len(doms[x]))
        for val in doms[best]:
            new = dict(doms); ok = True
            for y in nbrs[best]:
                if y in asg:
                    continue
                z = zero[(best, y)]
                if z is None:
                    continue
                c = [w for w in doms[y] if (gdot(mul, val, w) == 0) == z]
                if not c:
                    ok = False; break
                new[y] = c
            if not ok:
                continue
            asg[best] = val
            if dfs(new):
                return True
            del asg[best]
        return False
    try:
        ok = dfs(dom)
    except TimeoutError:
        return 'timeout'
    if not ok:
        return None
    return dict(X=[list(asg[('p', i)]) for i in range(n_p)], Y=[list(asg[('l', j)]) for j in range(n_l)], nodes=nodes[0])


def check_universal(P, L, k, X, Y):
    """Exact, search-free verification of a stored frame-universal realisation."""
    q = 1 << k; mul = gf_tables(k)
    for V, W in ((X, P), (Y, L)):
        if len(V) != len(W):
            return False
        for a, b in zip(V, W):
            if len(a) != 3 or not any(a) or any(not (0 <= x < q) for x in a):
                return False
            if any(a[j] and not b[j] for j in range(3)):
                return False
    for i in range(len(P)):
        for j in range(len(L)):
            z = sum(a * b for a, b in zip(P[i], L[j])) == 0
            if z != (gdot(mul, X[i], Y[j]) == 0):
                return False
    return True
