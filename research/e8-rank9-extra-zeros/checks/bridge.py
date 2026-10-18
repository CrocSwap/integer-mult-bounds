# R1 bridge CHECK (exact): B-form members (any supp c / supp beta, singular D on A∩B, dependent supports, A = C(f))
# and A2 members are philippeVV lifts: normalise N = D_M^{-1} M (N_aa = 1); the side/S chosen by the proof (THEORY §1)
# has rank N[V\S,:] = 8 (or N[:,V\S]), N[T,T] = diag(d) G diag(d') with d,d' nonzero, tested entrywise by exact propagation (no sampling).
import sys, random, itertools
sys.path.insert(0, sys.argv[1])           # path to #2819 checks/
from fractions import Fraction as Fr
from e8lib import E, N as NL, G, O, dot
from modrank import rkp
from a2e8 import build_a2, TRI
R = [[Fr(x) for x in r] for r in E]
NB = [frozenset(s for s in range(NL) if s != u and G[u][s] != 0) for u in range(NL)]
def C(Aset):  # lines non-orthogonal to all of Aset (or in it)
    return [s for s in range(NL) if all(G[s][a] != 0 for a in Aset)]
def mat(X, Y): return [[dot(X[i], Y[j]) for j in range(NL)] for i in range(NL)]
def bform(rnd, A, B, sing=()):
    A, B = set(A), set(B); assert all(G[a][b] != 0 for a in A for b in B)
    q = lambda: Fr(rnd.choice([-1, 1]) * rnd.randint(1, 9), rnd.randint(1, 5))
    d1 = {u: q() for u in range(NL)}; d2 = {u: q() for u in range(NL)}
    c = {u: (q() if u in A else Fr(0)) for u in range(NL)}; be = {u: (q() if u in B else Fr(0)) for u in range(NL)}
    for u in sing: assert u in A and u in B; d1[u] = Fr(0)        # singular D1 on A∩B (diag stays c_u beta_u != 0)
    X = [[d1[u] * x for x in R[u]] + [c[u]] for u in range(NL)]; Y = [[d2[u] * x for x in R[u]] + [be[u]] for u in range(NL)]
    return X, Y
def normalise(X, Y):
    M = mat(X, Y); assert all(M[a][a] != 0 for a in range(NL))
    X = [[x / M[a][a] for x in X[a]] for a in range(NL)]; return X, Y, mat(X, Y)
def lift_side(Nm, A, B):
    # THEORY §1 Lemma L: A has no orthogonal pair -> X side, S = A ; else Y side, S = B
    if all(G[a][b] != 0 for a, b in itertools.combinations(A, 2)): return 'X', set(A)
    return 'Y', set(B)
def check(X, Y, A, B, label, a2=None):
    X, Y, Nm = normalise(X, Y)
    forced = all(Nm[a][b] == 0 for a in range(NL) for b in O[a]) and all(Nm[a][a] == 1 for a in range(NL))
    r9 = rkp(X) == 9 and rkp(Y) == 9
    extra = sum(1 for a in range(NL) for b in NB[a] if Nm[a][b] == 0)
    if a2 is None: side, S = lift_side(Nm, A, B)
    else: side, S = 'X', set(a2)
    T = [t for t in range(NL) if t not in S]
    rows = [Nm[t] for t in T] if side == 'X' else [[Nm[a][t] for a in range(NL)] for t in T]
    r8 = rkp(rows) == 8
    # N[T,T] is a root realisation: N_ts = d_t d'_s G_ts for all t,s in T with d, d' nonzero.  Exact test: on the bipartite graph of
    # non-orthogonal pairs (t,s) put K_ts = N_ts/G_ts, propagate d_t, d'_s from d_t0 = 1 (BFS over T x T), then verify EVERY entry.
    ok = True
    for t in T:
        for s in T:
            if G[t][s] == 0: ok &= Nm[t][s] == 0
    d = {T[0]: Fr(1)}; dp = {}; queue = [('r', T[0])]
    while queue:
        kind, i = queue.pop()
        for j in T:
            if G[i][j] == 0: continue
            if kind == 'r' and j not in dp and Nm[i][j] != 0: dp[j] = (Nm[i][j] / G[i][j]) / d[i]; queue.append(('c', j))
            if kind == 'c' and j not in d and Nm[j][i] != 0: d[j] = (Nm[j][i] / G[j][i]) / dp[i]; queue.append(('r', j))
    ok &= len(d) == len(T) and len(dp) == len(T)
    ok &= all(Nm[t][s] == d[t] * dp[s] * G[t][s] for t in T for s in T if t in d and s in dp)
    ok &= all(d[t] != 0 and dp[t] != 0 for t in T if t in d and t in dp)
    print('%-34s forced+diag %s rank9 %s extra_zeros %4d | side %s |S|=%2d rank8 off S %s, N[T,T] root realisation %s' % (label, forced, r9, extra, side, len(S), r8, ok))
    return forced and r9 and r8 and ok
rnd = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 1); allok = True
f = 0; Cf = C([f])
# (i) A={f}, B=C(f) (57)        (ii) A=C(f), B={f}, singular D1 at f      (iii) clique A, B=C(A), singular D on A∩B
allok &= check(*bform(rnd, [f], Cf), [f], Cf, 'B: A={f}, B=C(f)')
allok &= check(*bform(rnd, Cf, [f], sing=[f]), Cf, [f], 'B: A=C(f) (57), B={f}, d1_f=0')
for k in range(3):
    A = [rnd.randrange(NL)]
    for u in rnd.sample(range(NL), NL):
        if len(A) < 3 + 2 * k and u not in A and all(G[u][a] != 0 for a in A) and len(C(A + [u])) > len(A) + 1: A.append(u)
    B = C(A); sing = [a for a in A if a in B][:2]
    allok &= check(*bform(rnd, A, B, sing=sing), A, B, 'B: clique |A|=%d, B=C(A) |B|=%d, sing %d' % (len(A), len(B), len(sing)))
# (iv) dependent, non-clique supports on both sides (R3 region): A ∋ orthogonal pair, rank deficient; B likewise
def dependent(Sx): return rkp([R[s] for s in Sx]) < len(Sx)
found = 0
for trial in range(20000):
    s = rnd.randrange(NL); t = rnd.choice(sorted(O[s])); C2 = C([s, t])
    A = [s, t] + rnd.sample(C2, rnd.randint(0, 3)); A = sorted(set(A)); B = C(A)
    if len(B) < 3: continue
    Bs = rnd.sample(B, min(len(B), rnd.randint(3, 8)))
    if dependent(A) and dependent(Bs) and any(G[a][b] == 0 for a, b in itertools.combinations(Bs, 2)):
        allok &= check(*bform(rnd, A, Bs), A, Bs, 'B: dependent A |%d|, dependent B |%d|' % (len(A), len(Bs))); found += 1
        if found == 2: break
print('dependent non-clique pairs found:', found)
# (v) A = B = an A2 triangle (concurrent), d1 = 0 on one vertex
tri = list(TRI[5]); allok &= check(*bform(rnd, tri, tri, sing=[tri[0]]), tri, tri, 'B: A=B=A2 triangle, d1=0 at a vertex')
# (vi) A2 members (a2lib normal form = a2e8.build_a2), several triangles/seeds
for sd, tr in [(1, 0), (2, 17), (3, 400), (4, 1119)]:
    u, X, Y = build_a2(sd, tr); allok &= check(X, Y, None, None, 'A2 member seed %d tri %d' % (sd, tr), a2=u)
print('PASS bridge' if allok else 'FAIL bridge')
