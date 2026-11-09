#!/usr/bin/env python3
"""Root checker for the two-chain root (standard library).  python3 -I -B root_check.py [data/root.json]
The root is literally two copies of the #6833 chain-nested root on orthogonal coordinates (n = 20 each), one stage variable per stage, units interleaved
(chain A, chain B).  This checker (1) regenerates the chain root from its closed form (L site i: x = A + f_i + 2 sum_{j<i} f_j, y = A* - f_i*;
R site m: x = -A + h_m + 2 sum_{l>m} h_l, y = A* + h_m*; three thin queries) and requires all 21 units of EACH chain to equal the file, requires the cross Gram between
the chains to vanish and each chain's Gram to be sgn(i-j); (2) re-proves the SPEC-level identities for the whole root in exact Fractions: isotropy, product -I,
stage order, units inside masks, masks commuting with the prefix before and after the stage, the symbolic whole-job identity M(D) = -diag(prod D^eps) with each D once and affine,
full mask credit, dyadic x,y.
DECLARED: the lines of the predecessor family checks that this root does not satisfy, and why they are not requirements of the outer theorem:
  hosted t != 0 (The hosted family's root check line 'hosted t not 0, not -1'): here t = 0 by construction (no coupled plane; two separate planes per stage);
  hosted alpha, beta dyadic units: here alpha = beta = 0 (same reason);
  Gram digraph strongly connected (added by the #6883 root_check.py itself, not a SPEC line): here the Gram digraph has two components.
  The theorem's requirement is on the unit identity and the whole-job credit, not on connectivity (see README)."""
import json, os, sys
from fractions import Fraction as Q

def chain_sites():
    """The (9|9) chain-nested sites of #6833: list of (x, y, mask or None) in time order, n = 20 (field 19 is the empty field E)."""
    n = 20; A = 0; f = list(range(1, 10)); h = list(range(10, 19)); E = 19
    def vec(*pairs):
        v = [Q(0)] * n
        for i, c in pairs: v[i] += Q(c)
        return v
    out = []
    for i in range(9):
        out.append((vec((A, 1), (f[i], 1), *[(f[j], 2) for j in range(i)]), vec((A, 1), (f[i], -1)), {A, *f[:i + 1]}))
    def thin(a, u, p=0, q=0):
        x = [Q(0)] * n; y = [Q(0)] * n
        x[A] = Q(a); y[A] = Q(u)
        for i, j in enumerate(f): x[j] = Q(a + 1); y[j] = Q((1 - u) * (-1) ** i)
        for r, j in enumerate(reversed(h)): x[j] = Q(1 - a); y[j] = Q((u - 1) * (-1) ** r)
        x[E] = Q(q); y[E] = Q(p)
        return x, y, None
    out += [thin(0, 1, 0, 1), thin(-1, 2, 1, 0), thin(-1, 3, 1, -1)]
    for m in range(9):
        out.append((vec((A, -1), (h[m], 1), *[(h[l], 2) for l in range(m + 1, 9)]), vec((A, 1), (h[m], 1)), {A, *h[m:]}))
    return out

def blocks(R):
    """Regeneration and block identities; returns a list of failure names (empty = all hold)."""
    n, N = R['n'], R['N']; bad = []
    X = [[Q(v) for v in r] for r in R['X']]; Y = [[Q(v) for v in r] for r in R['Y']]
    S = chain_sites()
    if n != 40 or N != 42 or len(S) != 21: return ['shape']
    for c, off in (('A', 0), ('B', 20)):
        for k, (x, y, m) in enumerate(S):
            u = 2 * k + (0 if c == 'A' else 1)
            ex = [Q(0)] * 40; ey = [Q(0)] * 40
            for i in range(20): ex[off + i] = x[i]; ey[off + i] = y[i]
            if X[u] != ex or Y[u] != ey: bad.append('regeneration chain %s unit %d' % (c, k))
    dot = lambda a, b: sum(u * v for u, v in zip(a, b) if u and v)
    ua = [2 * k for k in range(21)]; ub = [2 * k + 1 for k in range(21)]
    if any(dot(Y[i], X[j]) != 0 or dot(Y[j], X[i]) != 0 for i in ua for j in ub): bad.append('cross Gram between the chains')
    for nm, us in (('A', ua), ('B', ub)):
        if any(dot(Y[i], X[j]) != ((a > b) - (a < b)) for a, i in enumerate(us) for b, j in enumerate(us)): bad.append('Gram of chain %s is not sgn(i-j)' % nm)
    return bad

def run(R, out=None):
    """All requirements; returns the list of failures."""
    pr = out or (lambda s: None)
    n, N = R['n'], R['N']; ST = R['stages']
    X = [[Q(v) for v in r] for r in R['X']]; Y = [[Q(v) for v in r] for r in R['Y']]
    bad = []
    def req(name, ok, info=''):
        pr(('PASS ' if ok else 'FAIL ') + name + (' ' + str(info) if info != '' else ''))
        if not ok: bad.append(name)
    dot = lambda a, b: sum(u * v for u, v in zip(a, b) if u and v)
    bb = blocks(R)
    req('two #6833 chain roots: all 21 units of each chain regenerate from the closed form, cross Gram 0, each Gram sgn(i-j)', not bb, bb[:3])
    if bb: return bad
    I = [[Q(int(i == j)) for j in range(n)] for i in range(n)]
    def lmul(M, x, y, c):
        d = [sum(y[i] * M[i][j] for i in range(n) if y[i]) for j in range(n)]
        return [[M[i][j] + c * x[i] * d[j] for j in range(n)] if x[i] else M[i][:] for i in range(n)]
    req('isotropy y_k.x_k=0 all k', all(dot(Y[k], X[k]) == 0 for k in range(N)))
    W = I; prefix = []
    for k in range(N):
        prefix.append(W); W = lmul(W, X[k], Y[k], Q(-2))
    prefix.append(W)
    req('T_{N-1}..T_0 = -I (I - 2xy)', W == [[-v for v in r] for r in I])
    us = [u for s in ST for u in s['units']]; L = len(ST)
    req('stage units disjoint, consecutive, in time order, one unit of each chain per stage', len(us) == len(set(us)) and all(s['units'] == [s['units'][0], s['units'][0] + 1] for s in ST) and all(max(ST[i]['units']) < min(ST[i + 1]['units']) for i in range(L - 1)) and all(set(s['mask']) == {c for c in range(40) if any(X[u][c] or Y[u][c] for u in s['units'])} or set(s['mask']) >= {c for c in range(40) if any(X[u][c] or Y[u][c] for u in s['units'])} for s in ST))
    pr('  N n L tau %d %d %d %d thin units %s; mask ranks %s' % (N, n, L, N - len(us), [k for k in range(N) if k not in set(us)], [len(s['mask']) for s in ST]))
    inside = lambda s: all(all(X[u][c] == 0 and Y[u][c] == 0 for c in range(n) if c not in set(s['mask'])) for u in s['units'])
    req('stage units inside their coordinate mask', all(inside(s) for s in ST))
    def comm(mask, M):
        m = set(mask); return all(M[i][j] == 0 for i in range(n) for j in range(n) if (i in m) != (j in m))
    req('mask commutes with the prefix before and after the stage', all(comm(s['mask'], prefix[min(s['units'])]) and comm(s['mask'], prefix[max(s['units']) + 1]) for s in ST))
    rows = [{i: {0: Q(1)}} for i in range(n)]; at = {max(s['units']): i for i, s in enumerate(ST)}; peak = 0
    for k in range(N):
        dual = {}
        for f, c in enumerate(Y[k]):
            if c:
                for col, p in rows[f].items():
                    e = dual.setdefault(col, {})
                    for m, v in p.items(): e[m] = e.get(m, 0) + c * v
        for r, c in enumerate(X[k]):
            if c:
                for col, p in dual.items():
                    e = rows[r].setdefault(col, {})
                    for m, v in p.items():
                        w = e.get(m, 0) - 2 * c * v
                        if w: e[m] = w
                        else: e.pop(m, None)
                    if not e: rows[r].pop(col)
        if k in at:
            b = 1 << at[k]
            for r in ST[at[k]]['mask']:
                new = {}
                for col, p in rows[r].items():
                    q = {}
                    for m, v in p.items():
                        if m & b: bad.append('stage variable twice'); return bad
                        q[m | b] = v
                    new[col] = q
                rows[r] = new
        peak = max(peak, sum(len(p) for r in rows for p in r.values()))
    tgt = [sum(1 << i for i, s in enumerate(ST) if r in set(s['mask'])) for r in range(n)]
    req('symbolic M(D) = -diag(prod D^eps), eps = mask incidence, each of the 18 stage variables once and affine', all(rows[r] == {r: {tgt[r]: Q(-1)}} for r in range(n)), 'peak monomials %d' % peak)
    req('every stage variable credited on all of its mask', all(bin(sum(1 << r for r in range(n) if tgt[r] >> i & 1)).count('1') == len(ST[i]['mask']) for i in range(L)))
    dy = lambda v: v.denominator & (v.denominator - 1) == 0
    req('x, y dyadic', all(dy(v) for r in X + Y for v in r))
    pr('  declared family lines not met: t = alpha*beta = 0 for every stage pair (alpha = %s, beta = %s); Gram digraph has 2 components (cross Gram 0); max |entry| %s' % (dot(Y[0], X[1]), dot(Y[1], X[0]), max(abs(v) for r in X + Y for v in r)))
    return bad

if __name__ == '__main__':
    R = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'root.json')))
    bad = run(R, print)
    print('PASS_ROOT_TWO_CHAINS' if not bad else 'FAILED ' + '; '.join(bad))
    sys.exit(1 if bad else 0)
