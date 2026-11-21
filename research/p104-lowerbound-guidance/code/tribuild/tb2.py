# TRIBUILD tb2: EXACT (Fractions) checks of LEAF-CHANNEL [P].
# Host-only product P_h = V_{k-1}..V_0, V_t = I + A_t B_t^T (A_t,B_t: n x 2, rows on E_t).  U = leaf coordinates (roles on one stage).
# Claims checked: (i) dim S := dim(ker(P_h+I) cap U) = dim(ker K_hh cap ker Acal_nonleaf)   [reduction]
#                 (ii) dim S <= min(sum_t a_t, sum_t z_t), a_t = dim ker(2I + B_Lt^T A_Lt), z_t = dim ker(K_tt + X_tt)
#                 (iii) a_t + z_t <= 2 when K_tt invertible  =>  dim S <= k + #(K_tt singular)
import sys, random
from fractions import Fraction as F
def rank(M):
    M = [r[:] for r in M]; rk = 0; cols = len(M[0]) if M else 0
    for c in range(cols):
        p = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]
        for i in range(len(M)):
            if i != rk and M[i][c] != 0:
                f = M[i][c]/M[rk][c]; M[i] = [x - f*y for x, y in zip(M[i], M[rk])]
        rk += 1
    return rk
def mm(X, Y): return [[sum(X[i][l]*Y[l][j] for l in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]
def T(X): return [list(r) for r in zip(*X)]
def eye(n): return [[F(int(i == j)) for j in range(n)] for i in range(n)]
def add(X, Y): return [[a+b for a, b in zip(r, s)] for r, s in zip(X, Y)]
def analyse(n, stages, leaves):
    """stages: list of (A,B) n x 2 Fraction matrices. leaves: list of leaf role indices (each nonzero on one stage only)."""
    k = len(stages); I = eye(n); P = eye(n)
    for A, B in stages: P = mm(add(I, mm(A, T(B))), P)
    PI = add(P, I); dimS = len(leaves) - rank([[PI[i][j] for j in leaves] for i in range(n)])
    nonleaf = [r for r in range(n) if r not in leaves]
    # host-only K (2k x 2k): K = 2I + Gdiag + Gup - Glow, G_{st} = B_s^T A_t
    K = [[F(0)]*(2*k) for _ in range(2*k)]
    for s in range(k):
        for t in range(k):
            G = mm(T(stages[s][1]), stages[t][0])
            sg = 1 if s <= t else -1
            for i in range(2):
                for j in range(2): K[2*s+i][2*t+j] = sg*G[i][j] + (2 if (s == t and i == j) else 0)
    Acal = [[stages[t][0][r][j] for t in range(k) for j in range(2)] for r in nonleaf]
    dimC = 2*k - rank(K + Acal)
    a = []; z = []; sing = 0
    for t, (A, B) in enumerate(stages):
        L = [r for r in leaves if any(A[r][j] != 0 or B[r][j] != 0 for j in range(2))]
        H = [r for r in nonleaf]
        Y = mm(T([B[r] for r in L]), [A[r] for r in L]) if L else [[F(0)]*2 for _ in range(2)]
        X = mm(T([B[r] for r in H]), [A[r] for r in H])
        N = add(add(eye(2), eye(2)), Y); Ktt = add(N, X); M = add(Ktt, X)
        a.append(2 - rank(N)); z.append(2 - rank(M)); sing += (rank(Ktt) < 2)
        detV = (1 + (Y[0][0]+X[0][0]))*(1 + (Y[1][1]+X[1][1])) - (Y[0][1]+X[0][1])*(Y[1][0]+X[1][0])
    ok = (dimS == dimC) and dimS <= min(sum(a), sum(z)) and dimS <= k + sing and all(ai + zi <= 2 for ai, zi, in zip(a, z)) if sing == 0 else (dimS == dimC and dimS <= min(sum(a), sum(z)) and dimS <= k + sing)
    return dict(k=k, d1=len(leaves), dimS=dimS, dimC=dimC, suma=sum(a), sumz=sum(z), sing=sing, ok=ok)
def put(M, r, v): M[r] = [F(x) for x in v]
def tight_hub_chart(k):
    """2 hubs on every stage, 2 leaves/stage; alternating injector (Y=-2I, X=[[2,1],[0,2]]) / absorber (Y=2I, X=-2I); det V_t = 1."""
    n = 2 + 2*k; st = []
    for t in range(k):
        A = [[F(0)]*2 for _ in range(n)]; B = [[F(0)]*2 for _ in range(n)]
        l1, l2 = 2+2*t, 3+2*t
        if t % 2 == 0: put(A, l1, (1, 0)); put(A, l2, (0, 1)); put(B, l1, (-2, 0)); put(B, l2, (0, -2)); put(A, 0, (1, 0)); put(A, 1, (0, 1)); put(B, 0, (2, 0)); put(B, 1, (1, 2))
        else: put(A, l1, (1, 0)); put(A, l2, (0, 1)); put(B, l1, (2, 0)); put(B, l2, (0, 2)); put(A, 0, (1, 0)); put(A, 1, (0, 1)); put(B, 0, (-2, 0)); put(B, 1, (0, -2))
        st.append((A, B))
    return n, st, list(range(2, n))
def tri_chart_random(g, f, rng, mode):
    """triangle chart: 3 hubs, stage t of class t%3 on the two hubs != class; f leaves per stage. mode: 'gen' random,
    'struct' random with forced leaf blocks (Y = -2I injector or det-4 absorber-type), 'sing' allows K_tt singular."""
    k = 3*g; n = 3 + f*k; st = []
    R = lambda: F(rng.randint(-3, 3), rng.choice([1, 1, 2]))
    for t in range(k):
        A = [[F(0)]*2 for _ in range(n)]; B = [[F(0)]*2 for _ in range(n)]
        hubs = [j for j in range(3) if j != t % 3]; L = [3+f*t+i for i in range(f)]
        for r in hubs + L: A[r] = [R(), R()]; B[r] = [R(), R()]
        if mode == 'struct' and f >= 2:
            c = rng.choice(['inj', 'abs', 'gen'])
            if c == 'inj': put(A, L[0], (1, 0)); put(A, L[1], (0, 1)); put(B, L[0], (-2, 0)); put(B, L[1], (0, -2)); [put(A, r, (0, 0)) or put(B, r, (0, 0)) for r in L[2:]]
            if c == 'abs':
                put(A, L[0], (1, 0)); put(A, L[1], (0, 1)); put(B, L[0], (2, 0)); put(B, L[1], (0, 2)); [put(A, r, (0, 0)) or put(B, r, (0, 0)) for r in L[2:]]
                put(A, hubs[0], (1, 0)); put(A, hubs[1], (0, 1)); put(B, hubs[0], (-2, 0)); put(B, hubs[1], (0, -2))
        st.append((A, B))
    return n, st, list(range(3, n))
if __name__ == '__main__':
    out = []
    for k in (2, 4, 6, 8):
        n, st, L = tight_hub_chart(k); out.append(('tight hub chart', analyse(n, st, L)))
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
    for mode in ('gen', 'struct'):
        for g in (1, 2):
            for _ in range(int(sys.argv[2]) if len(sys.argv) > 2 else 20):
                n, st, L = tri_chart_random(g, 2, rng, mode); out.append((f'tri {mode} g{g}', analyse(n, st, L)))
    bad = [o for o in out if not o[1]['ok']]
    for name, r in out[:4]: print(name, r)
    from collections import Counter
    print('random/struct dimS histogram:', Counter((nm, r['dimS'], r['sing']) for nm, r in out[4:]))
    print('violations:', len(bad), bad[:3])
