# CALLERWORD cw1: exact [C] checks of the CallerWord bridge on the #7113 caller (own code; JSON is data).
# Per type: macro-expand J, evaluate at q=+-1, D=1 (LAMBDA=1 there), build A,B columns as in CallerWord.lean,
# check prod V = -I, column count, rank K, 2x2 diagonal blocks of K, stage incidence, V/W support + biorth.
import json, sys
from fractions import Fraction as F
C = json.load(open(sys.argv[1]))
k = C['stages']
def expand(ty):
    T = C['types'][ty]; off = T['offset']; n = T['roles']; ev = []
    a2 = F(C['types']['A'].get('alpha2', 0))
    for e in C['events']:
        if e[0] == 'J':
            t = e[1] - 1
            if ty == 'A':
                x, y, u, v = [r - off for r in e[2]]
                ev += [('host', x, y, F(0), F(1)), ('host', u, v, a2, F(0))] + [('idle', z, {t}, 0) for z in (x, y, u, v)]
            else:
                s, tt = e[3][0] - off, e[3][1] - off; al, be = F(e[3][2]), F(e[3][3])
                ev += [('host', s, tt, al, be), ('idle', s, {t}, 0), ('idle', tt, {t}, 0)]
        elif e[0] == ty:
            op = e[1]; r = e[2] - off
            if op == 'ADD': ev.append(('add', r, e[3] - off, F(e[4])))
            elif op == 'SCALE': ev.append(('scale', r, F(e[3])))
            elif op == 'SWAP': ev.append(('swap', r, e[3] - off))
            elif op == 'QUERY': ev.append(('query', r, e[3] - off, e[4]))
            elif op == 'LAMBDA': ev.append(('lam', r, e[3]))
            elif op == 'IDLE_ONE': ev.append(('idle', r, {s - 1 for s in e[3]}, 0))
            elif op == 'IDLE_ODD': ev.append(('idle', r, {s - 1 for s in e[3]}, e[4]))
            else: raise ValueError(op)
    masks = [{s for s, b in enumerate(dg[2:]) if b} for dg in T['diagonal']]
    exs = [dg[0] for dg in T['diagonal']]
    return n, ev, masks, exs
def qp(q, s): return q ** (s % 4)
def apply(M, e, q):  # rows update: M <- E M  (M list of rows)
    op = e[0]
    if op == 'add': r, s, c = e[1:]; M[r] = [a + c * b for a, b in zip(M[r], M[s])]
    elif op == 'scale': r, c = e[1:]; M[r] = [c * a for a in M[r]]
    elif op == 'swap': r, s = e[1:]; M[r], M[s] = M[s], M[r]
    elif op == 'query': r, s, sg = e[1:]; c = qp(q, sg); M[r] = [a + c * b for a, b in zip(M[r], M[s])]
    elif op == 'lam': pass  # = 1 at q^2 = 1
    elif op == 'idle': r, S, sg = e[1:]; c = qp(q, sg); M[r] = [c * a for a in M[r]]
    elif op == 'host':
        s, t, a, b = e[1:]
        rs = [x + a * q * y for x, y in zip(M[s], M[t])]
        rt = [b * q ** 3 * x + (1 + a * b) * y for x, y in zip(M[s], M[t])]
        M[s], M[t] = rs, rt
def inv_apply_right(Minv, e):  # Minv <- Minv * E^{-1}  (base point q=1): columns update
    op = e[0]; n = len(Minv)
    def colop(f):
        for row in Minv: f(row)
    if op == 'add':
        r, s, c = e[1:]
        if r == s:
            colop(lambda R: R.__setitem__(r, R[r] / (1 + c)))
        else:  # E = 1 + c E_rs ; E^-1 = 1 - c E_rs ; X E^-1: col s -= c col r
            colop(lambda R: R.__setitem__(s, R[s] - c * R[r]))
    elif op == 'scale': r, c = e[1:]; colop(lambda R: R.__setitem__(r, R[r] / c))
    elif op == 'swap': r, s = e[1:]; colop(lambda R: (R.__setitem__(r, R[s]), R.__setitem__(s, R[r])) if False else R.__setitem__(slice(None), [R[s] if i == r else R[r] if i == s else R[i] for i in range(len(R))]))
    elif op == 'query':
        r, s, sg = e[1:]; colop(lambda R: R.__setitem__(s, R[s] - R[r]))
    elif op in ('lam', 'idle'): pass
    elif op == 'host':  # H = [[1,a],[b,1+ab]] on (s,t); H^-1 = [[1+ab,-a],[-b,1]]; X H^-1 cols
        s, t, a, b = e[1:]
        def f(R):
            cs, ct = R[s], R[t]
            R[s] = cs * (1 + a * b) + ct * (-b); R[t] = cs * (-a) + ct * 1
        colop(f)
def terms(e):
    op = e[0]
    if op == 'query': return [(e[1], e[2], F(-2))] if e[3] % 2 else []
    if op == 'idle': return [(e[1], e[1], F(-2))] if e[3] % 2 else []
    if op == 'host':
        s, t, a, b = e[1:]; out = []
        if a: out.append((s, t, -2 * a))
        if b: out.append((t, s, -2 * b))
        return out
    return []
def rank(M):
    M = [row[:] for row in M]; r = 0; cols = len(M[0]) if M else 0
    for c in range(cols):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c] / M[r][c]; M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        r += 1
    return r
def matmul(X, Y): return [[sum(X[i][l] * Y[l][j] for l in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]
for ty in ('A', 'B'):
    n, ev, masks, exs = expand(ty)
    I = lambda: [[F(int(i == j)) for j in range(n)] for i in range(n)]
    for q in (1, -1):
        M = I()
        for e in ev: apply(M, e, F(q))
        ok = all(M[i][j] == (F(qp(q, exs[i])) if i == j else 0) for i in range(n) for j in range(n))
        print(ty, 'replay q=%d D=1 = target:' % q, ok)
    # columns
    P = I(); Pinv = I(); Acols = []; Bcols = []; blk = []; incV = {}; incW = {}
    for j, e in enumerate(ev):
        Pj = [row[:] for row in P]
        apply(P, e, F(1)); inv_apply_right(Pinv, e)
        for (x, y, c) in terms(e):
            Acols.append([c * Pinv[r][x] for r in range(n)]); Bcols.append([Pj[y][r] for r in range(n)]); blk.append(j)
        if e[0] == 'idle':
            for t in e[2]:
                incV.setdefault(t, []).append([Pinv[r][e[1]] for r in range(n)])
                incW.setdefault(t, []).append([P[e[1]][r] for r in range(n)])
    m = len(Acols)
    print(ty, 'n =', n, 'columns =', m, '(2k =', 2 * k, ')', 'thin =', m - sum(1 for e in ev if e[0] == 'host' for _ in terms(e)))
    # product of V_j = I + sum_{cols in block j} a b^T, in event order
    W = I(); cur = None
    for idx in range(m):
        a, b = Acols[idx], Bcols[idx]
    # group by block in order
    from itertools import groupby
    W = I()
    for jb, grp in groupby(range(m), key=lambda i: blk[i]):
        grp = list(grp)
        V = I()
        for i in grp:
            for r in range(n):
                if Acols[i][r]:
                    V[r] = [V[r][c] + Acols[i][r] * Bcols[i][c] for c in range(n)]
        W = matmul(V, W)
    print(ty, 'prod V = -I:', all(W[i][j] == (-1 if i == j else 0) for i in range(n) for j in range(n)))
    G = [[sum(Bcols[i][r] * Acols[j][r] for r in range(n)) for j in range(m)] for i in range(m)]
    K = [[(2 if i == j else 0) + (G[i][j] if blk[i] <= blk[j] else -G[i][j]) for j in range(m)] for i in range(m)]
    print(ty, 'rank G =', rank(G), 'rank K =', rank(K), ' rank K + n =', rank(K) + n, '<= cols', m)
    # 2x2 principal minors on host blocks with 2 columns (lambda != -1 test) and on column pairs
    nz = 0; tot = 0
    for i in range(m):
        for j in range(i + 1, m):
            if blk[i] == blk[j]:
                tot += 1; nz += (K[i][i] * K[j][j] - K[i][j] * K[j][i]) != 0
    print(ty, 'same-event 2x2 diagonal blocks of K invertible:', nz, '/', tot)
    anyminor = any((K[i][i] * K[j][j] - K[i][j] * K[j][i]) != 0 for i in range(m) for j in range(i + 1, m))
    print(ty, 'some 2x2 principal minor of K nonzero (role_count_lam hypothesis):', anyminor)
    # stage incidence, biorth, support
    bad = 0
    for t in range(k):
        E = [r for r in range(n) if t in masks[r]]; Vt = incV[t]; Wt = incW[t]
        if len(E) != len(Vt): bad += 1
        WV = [[sum(Wt[a][r] * Vt[b][r] for r in range(n)) for b in range(len(Vt))] for a in range(len(Wt))]
        if any(WV[a][b] != (1 if a == b else 0) for a in range(len(Vt)) for b in range(len(Vt))): bad += 1
        if any(v[r] != 0 for v in Vt + Wt for r in range(n) if r not in E): bad += 1
    print(ty, 'stage incidence / biorth / support violations over', k, 'stages:', bad)
    # host column support: columns of host events at stage t vanish outside E_t
    stage_of = {}
    for j, e in enumerate(ev):
        if e[0] == 'host':
            t = next(iter(ev[j + (2 if ty == 'A' else 1)][2]))
            stage_of[j] = t
    hb = sum(1 for i in range(m) if blk[i] in stage_of for r in range(n)
             if stage_of[blk[i]] not in masks[r] and (Acols[i][r] != 0 or Bcols[i][r] != 0))
    print(ty, 'host-column support violations:', hb)
    deg1 = sum(1 for r in range(n) if len(masks[r]) == 1); deg0 = sum(1 for r in range(n) if len(masks[r]) == 0)
    print(ty, 'roles with |mask| = 1:', deg1, ' |mask| = 0:', deg0)
