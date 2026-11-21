# QZBUILD exact CB-chain construction (theory: nested coordinate J-blocks U_1 c ... c U_{k-1} = U_k = all, |U_j| = 2j).
# P_j = -I + X_j Y_j^T on U_j (rank 2), step via a rank-2 idempotent M = F G^T with det(I - G^T Bd F) = 1 solved LINEARLY.
import sys, json, random
from fractions import Fraction as Fr
from qzword import mat_inv, mm, nullspace_rows, assemble
from qzcore import Design
Z, O = Fr(0), Fr(1)
FAIL = []
def eye(n): return [[O if i == j else Z for j in range(n)] for i in range(n)]
def T(A): return [list(r) for r in zip(*A)]
def add(A, B, c=O): return [[a + c*b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]
def det(A):
    n = len(A); M = [list(r) for r in A]; d = O
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None: return Z
        if p != c: M[c], M[p] = M[p], M[c]; d = -d
        d *= M[c][c]
        for r in range(c+1, n):
            f = M[r][c]/M[c][c]
            if f: M[r] = [x - f*y for x, y in zip(M[r], M[c])]
    return d
def rank(A):
    M = [list(r) for r in A]; rk = 0; cols = len(M[0]) if M else 0
    for c in range(cols):
        p = next((r for r in range(rk, len(M)) if M[r][c] != 0), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]
        for r in range(len(M)):
            if r != rk and M[r][c] != 0:
                f = M[r][c]/M[rk][c]; M[r] = [x - f*y for x, y in zip(M[r], M[rk])]
        rk += 1
    return rk
def rnd(rng, lo=-3, hi=3):
    x = 0
    while x == 0: x = rng.randint(lo, hi)
    return Fr(x)
def blockdiag(A, B):
    if not B: return [list(r) for r in A]
    if not A: return [list(r) for r in B]
    ca, cb = len(A[0]), len(B[0])
    return [list(r) + [Z]*cb for r in A] + [[Z]*ca + list(r) for r in B]
def chain_frames(k, rng, maxtry=200):
    n = 2*k - 2
    V1 = [[Fr(2), Fr(1)], [Fr(1), Fr(1)]]
    Vs = [blockdiag(V1, eye(n-2))]
    X = add(V1, eye(2)); Y = eye(2)          # P_1 + I = X Y^T on U_1
    P = blockdiag(V1, eye(n-2))
    for j in range(2, k):
        m = 2*j
        for _ in range(maxtry):
            A = blockdiag(X, eye(2)); B = blockdiag(Y, [[Fr(2), Z], [Z, Fr(2)]])
            Bd = mm(T(B), A, Z)                      # 4x4
            F = [[rnd(rng) for _ in range(2)] for _ in range(4)]
            if rank(F) < 2: continue
            FtF = mm(T(F), F, Z); G0 = mm(F, mat_inv(FtF, Z, O), Z)
            Fp = nullspace_rows(T(F), 4, Z, O)        # rows p with p.F = 0 -> 2 rows
            Fperp = T(Fp)                               # 4x2
            Z0 = add(eye(2), mm(mm(T(G0), Bd, Z), F, Z), -O)
            Wm = mm(mm(Fp, Bd, Z), F, Z)
            if det(Wm) == 0: continue
            a_, b_, c_ = rnd(rng), rnd(rng), rnd(rng); d_ = (1 + b_*c_)/a_
            if a_ + d_ in (2, -2): continue
            Yt = [[a_, b_], [c_, d_]]
            CT = mm(add(Z0, Yt, -O), mat_inv(Wm, Z, O), Z)
            G = add(G0, mm(Fperp, T(CT), Z))
            Xn = mm(A, F, Z); Yn = mm(B, G, Z)
            Pn_U = add([[-x for x in r] for r in eye(m)], mm(Xn, T(Yn), Z))
            Pn = blockdiag(Pn_U, eye(n-m))
            try: Vn = mm(Pn, mat_inv(P, Z, O), Z)
            except ZeroDivisionError: continue
            D = add(Vn, eye(n), -O)
            if rank(D) != 2:
                M_ = mm(F, T(G), Z)
                FAIL.append(('rank', j, rank(D), rank(add(Pn, P, -O)), rank(add(M_, eye(4), -O)), rank(A), rank(B), rank(mm(T(G),F,Z)))); continue
            tau = sum(Vn[i][i] for i in range(n)) - (n-2)
            if tau in (2, -2) or det(Vn) != 1:
                FAIL.append(('tau/det', j, tau, det(Vn))); continue
            break
        else: raise RuntimeError(('no step', FAIL[-5:]))
        Vs.append(Vn); P = Pn; X, Y = Xn, Yn
    Vk = [[-x for x in r] for r in mat_inv(P, Z, O)]
    tau = sum(Vk[i][i] for i in range(n)) - (n-2)
    assert rank(add(Vk, eye(n), -O)) == 2 and tau not in (2, -2) and det(Vk) == 1, ('last', tau)
    Vs.append(Vk)
    return n, Vs
def stage_data(n, V, U):
    """contacts + idles for a coordinate J-block U with twist V (block on U)."""
    D = add(V, eye(n), -O)
    tau = sum(V[i][i] for i in range(n)) - (n-2)
    cols = [[D[i][c] for i in range(n)] for c in range(n)]
    f1 = None
    for c in cols:
        if any(c):
            Vc = [sum(V[i][l]*c[l] for l in range(n)) for i in range(n)]
            # not an eigenvector: Vc not parallel to c
            if rank([c, Vc]) == 2: f1 = c; break
    if f1 is None:
        c0 = next(c for c in cols if any(c)); c1 = next(c for c in cols if any(c) and rank([c0, c]) == 2)
        f1 = [x + y for x, y in zip(c0, c1)]
    f2 = [sum(V[i][l]*f1[l] for l in range(n)) - tau/2*f1[i] for i in range(n)]
    Uc = [x for x in range(n) if x not in U]
    # kernel of D restricted to vectors supported on U
    DU = [[D[i][c] for c in U] for i in range(n)]
    ker = nullspace_rows(DU, len(U), Z, O)     # rows p with DU p = 0  (nullspace of DU as linear map)
    cs = []
    for p in ker:
        v = [Z]*n
        for idx, x in enumerate(U): v[x] = p[idx]
        cs.append(v)
    basis = [f1, f2] + cs + [[O if i == x else Z for i in range(n)] for x in Uc]
    Bm = T(basis); Bi = mat_inv(Bm, Z, O)
    vs = basis[:len(U)]; ws = Bi[:len(U)]
    ab = (tau - 2)/4; b = -O/(2*(1+ab)); a = -(tau*tau/4 - 1)/2
    assert a*b == ab
    return vs, ws, (a, b), tau
def build_chain(k, seed=0):
    rng = random.Random(seed)
    n, Vs = chain_frames(k, rng)
    Us = [list(range(min(2*j, n))) for j in range(1, k+1)]
    masks = [set(t for t in range(k) if r in Us[t]) for r in range(n)]
    events = []; Vv = []; Ww = []; AB = []; taus = []
    for t in range(k):
        vs, ws, ab, tau = stage_data(n, Vs[t], Us[t])
        events.append(('H', t)); events += [('I', frozenset({t}))]*(len(Us[t]) - 2)
        Vv += vs; Ww += ws; AB.append(ab); taus.append(tau)
    d = Design(n, k, masks, events, 'chain%d' % k)
    C = assemble(d, Vv, Ww, AB)
    return d, C, taus
if __name__ == '__main__':
    import qzcheck
    for k in map(int, sys.argv[1:]):
        d, C, taus = build_chain(k)
        json.dump(C, open('chain_k%d.json' % k, 'w'))
        ok, wf = qzcheck.legal(C)
        print('k', k, 'n', d.n, 'taus', [str(t) for t in taus], 'LEGAL', ok, wf, 'cHat %.4f' % qzcheck.chat(C), 'HP %.4f' % qzcheck.HP(k), flush=True)
