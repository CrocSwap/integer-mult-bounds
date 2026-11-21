# QZBUILD multi-level chain (ML-chain): chain frame + level-j pieces (stage set = all later stages) living in the
# -1 eigenspaces of the prefix products P_j; J blocks J_t = E_{U_t} - sum of earlier-level piece projections.
import sys, json, random
from fractions import Fraction as Fr
from qzchain import *
from qzword import nullspace_rows, mat_inv, mm, assemble
from qzcore import Design
def vec_space(Mat, n, U):
    """right nullspace of Mat among vectors supported on U"""
    sub = [[Mat[i][c] for c in U] for i in range(n)]
    out = []
    for p in nullspace_rows(sub, len(U), Z, O):
        v = [Z]*n
        for idx, x in enumerate(U): v[x] = p[idx]
        out.append(v)
    return out
def dot(a, b): return sum((x*y for x, y in zip(a, b)), Z)
def build_ml(k, seed=0, levels=None, per_level=2):
    rng = random.Random(seed)
    n, Vs = chain_frames(k, rng)
    Us = [list(range(min(2*j, n))) for j in range(1, k+1)]
    Ps = []; P = eye(n)
    for V in Vs: P = mm(V, P, Z); Ps.append(P)
    levels = list(range(2, k)) if levels is None else levels
    PV, PW, PL = [], [], []   # piece v, w, level (time index j: placed after time-j block)
    for j in levels:
        Pj = Ps[j-1]; U = Us[j-1]
        Mp = add(Pj, eye(n))
        Rj = vec_space(Mp, n, U)                     # (P+I)u = 0
        Lj = vec_space(T(Mp), n, U)                  # w^T (P+I) = 0
        # restrict: v in ann(old w), w in ann(old v)
        def restrict(space, olds):
            if not olds: return space
            # coefficients c with sum c_i space_i . o = 0 for o in olds
            Mx = [[dot(s, o) for s in space] for o in olds]
            cs = nullspace_rows(Mx, len(space), Z, O)
            return [[sum((c[i]*space[i][x] for i in range(len(space))), Z) for x in range(n)] for c in cs]
        Rr = restrict(Rj, PW); Lr = restrict(Lj, PV)
        if len(Rr) < per_level or len(Lr) < per_level: raise RuntimeError(('dims', j, len(Rr), len(Lr)))
        vs = Rr[:per_level]
        # choose ws in Lr with ws.vs = I
        G = [[dot(l, v) for v in vs] for l in Lr]       # |Lr| x per_level
        # pick per_level rows of Lr combos: w = sum c_l Lr_l ; need C G = I ; take least: first per_level independent
        sel = None
        import itertools
        for comb in itertools.combinations(range(len(Lr)), per_level):
            Gs = [G[i] for i in comb]
            if det(Gs) != 0: sel = comb; break
        if sel is None: raise RuntimeError(('pairing', j))
        Gi = mat_inv([G[i] for i in sel], Z, O)   # Gs^-1 ; ws = Gs^-T rows
        ws = []
        for a in range(per_level):
            # w_a = sum_b (Gs^{-1})_{b a}?  we need w_a . v_c = delta: W = C L, (C Gs) = I => C = Gs^{-1}
            w = [sum((Gi[a][b]*Lr[sel[b]][x] for b in range(per_level)), Z) for x in range(n)]
            ws.append(w)
        for a in range(per_level):
            PV.append(vs[a]); PW.append(ws[a]); PL.append(j)
    # J blocks
    events = []; Vv = []; Ww = []; AB = []; taus = []; stage_inc = {}
    for t in range(1, k+1):     # time t, stage t-1
        V = Vs[t-1]; U = Us[t-1]
        Jt = [[O if (i == jj and i in U) else Z for jj in range(n)] for i in range(n)]
        for v, w, l in zip(PV, PW, PL):
            if l < t:
                for i in range(n):
                    for jj in range(n): Jt[i][jj] -= v[i]*w[jj]
        D = add(V, eye(n), -O); tau = sum(V[i][i] for i in range(n)) - (n-2)
        # contacts f1,f2 in Im D
        cols = [[D[i][c] for i in range(n)] for c in range(n)]
        f1 = None
        for c in cols:
            if any(c):
                Vc = [dot(V[i], c) for i in range(n)]
                if rank([c, Vc]) == 2: f1 = c; break
        f2 = [dot(V[i], f1) - tau/2*f1[i] for i in range(n)]
        # C_t = ker D cap Im J_t ; Im J_t = column space ; ker J_t basis
        imJ = [list(r) for r in T(Jt)]
        # basis of Im J
        basisJ = []
        for c in imJ:
            if any(c) and rank(basisJ + [c]) > len(basisJ): basisJ.append(c)
        # vectors u in Im J with D u = 0: u = sum a_i basisJ_i, D u = 0
        DB = [[dot(D[i], b) for b in basisJ] for i in range(n)]
        cs = nullspace_rows(DB, len(basisJ), Z, O)
        Cvecs = [[sum((c[i]*basisJ[i][x] for i in range(len(basisJ))), Z) for x in range(n)] for c in cs]
        kerJ = vec_space(Jt, n, list(range(n)))
        basis = [f1, f2] + Cvecs + kerJ
        assert len(basis) == n and rank(basis) == n, ('basis', t, len(basis), len(Cvecs), len(kerJ), len(basisJ))
        Bi = mat_inv(T(basis), Z, O)
        r = 2 + len(Cvecs)
        ab = (tau - 2)/4; b = -O/(2*(1+ab)); a = -(tau*tau/4 - 1)/2
        events.append(('H', t-1)); events += [('I', frozenset({t-1}))]*len(Cvecs)
        Vv += basis[:r]; Ww += Bi[:r]; AB.append((a, b)); taus.append(tau)
        for v, w, l in zip(PV, PW, PL):
            if l == t:
                events.append(('I', frozenset(range(t, k)))); Vv.append(v); Ww.append(w)
    masks = [set(t for t in range(k) if r in Us[t]) for r in range(n)]
    d = Design(n, k, masks, events, 'ml%d' % k)
    C = assemble(d, Vv, Ww, AB)
    build_ml.data = (Vv, Ww, AB)
    return d, C, taus
if __name__ == '__main__':
    import qzcheck
    for k in map(int, sys.argv[1:]):
        d, C, taus = build_ml(k)
        json.dump(C, open('ml_k%d.json' % k, 'w'))
        ok, wf = qzcheck.legal(C)
        print('k', k, 'n', d.n, 'LEGAL', ok, wf, 'cHat %.4f' % qzcheck.chat(C), 'HP %.4f' % qzcheck.HP(k), 'taus', [str(x) for x in taus], flush=True)
