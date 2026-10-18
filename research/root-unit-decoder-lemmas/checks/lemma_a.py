"""Lemma A (T <= 2) -- two checks.  usage: lemma_a.py   (reads ../lib only)

Part 1 (port of the T <= 2 table).  Per unit: budget c = largest cst with cst/v < x*(h0), h0 = max(omega, 5) (omega = size of a
largest clique of mutually non-orthogonal lines, w = Gram rank of that clique); under the per-total premise beta_j >= w a decoder
that beats the E8 ceiling has at most floor(c/w) totals.  If that is <= 2, Lemma A (cost >= v, i.e. x >= 1 > x*) closes the unit.

Part 2 (instances).  For random exact decoders with T <= 2 totals on several root units, and random admissible pairings B (unit
diagonal, ones only on orthogonal pairs where M_ts = 0, a random subset or all of them), recompute
    r_1 + r_2 >= v,   r_j >= |P_j| + rank B[X,X],   rank B[X,X] >= max(|X_<|, |X_>|)
with X, P_j, X_<, X_> as in the proof (README).  An instance can only fail if the proof is wrong; this is a sanity check of the
proof's three inequalities, not a substitute for it.  Seeds are fixed."""
import io, contextlib, math, os, random, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
with contextlib.redirect_stdout(io.StringIO()):
    import ade
import fx

E8ref = fx.best(9, 0.6)[0]
def xstar(h):
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if fx.best(h, mid)[0] >= E8ref: lo = mid
        else: hi = mid
    return lo

units = [(f"A{n}", ade.A(n)) for n in range(3, 9)] + [(f"D{n}", ade.D(n)) for n in range(4, 9)] + [("E6", ade.E6b()), ("E7", ade.E7())]
for nm, L in units:
    G = np.rint(L @ L.T).astype(int); v = len(L); off = ~np.eye(v, dtype=bool)
    K = ade.maxclique((G != 0) & off); w = int(np.linalg.matrix_rank(G[np.ix_(K, K)])); h0 = max(len(K), 5)
    c = math.ceil(v * xstar(h0)) - 1; Tm = c // w
    print(f"{nm} v={v} w={w} h0={h0} budget cst<={c} Tmax={Tm} {'CLOSED by T<=2 lemma' if Tm <= 2 else 'OPEN (T>=3 needed)'}")

def rank_f2(B, R, A):
    if len(R) == 0 or len(A) == 0: return 0
    return ade.f2rank(B[np.ix_(R, A)])

def instance(G, rng, mode):
    v = len(G); orth = (G == 0) & ~np.eye(v, dtype=bool)
    while True:
        if mode == 0:   # generic small integers
            p = [[rng.choice((-2, -1, 0, 1, 1, 2)) for _ in range(2)] for _ in range(v)]
            q = [[rng.choice((-2, -1, 0, 1, 1, 2)) for _ in range(2)] for _ in range(v)]
        else:           # alpha/beta structure: p = (1, a), q = (1, -b), zero iff a_t = b_s; some private lines
            a = [rng.choice((0, 1, 2, 3)) for _ in range(v)]; b = [rng.choice((0, 1, 2, 3)) for _ in range(v)]
            p = [[1, a[t]] for t in range(v)]; q = [[1, -b[t]] for t in range(v)]
            for t in range(v):
                u = rng.random()
                if u < 0.15: p[t][1] = 0
                elif u < 0.3: q[t][1] = 0
                sc = rng.choice((1, 1, 2, -1, 3)); p[t] = [sc * x for x in p[t]]
            if rng.random() < 0.1:
                for t in range(v): p[t][1] = q[t][1] = 0     # T = 1
        P = np.array(p); Q = np.array(q); M = P @ Q.T
        if all(M[t, t] != 0 for t in range(v)): break
    keep = 1.0 if rng.random() < 0.5 else rng.choice((0.3, 0.6, 0.9))
    B = np.eye(v, dtype=np.uint8)
    for t in range(v):
        for s in range(v):
            if orth[t, s] and M[t, s] == 0 and rng.random() < keep: B[t, s] = 1
    return P, Q, M, B

def check(G, P, Q, M, B):
    v = len(G); R = [np.nonzero(P[:, j])[0] for j in range(2)]; A = [np.nonzero(Q[:, j])[0] for j in range(2)]
    D = [sorted(set(R[j]) & set(A[j])) for j in range(2)]
    assert set(D[0]) | set(D[1]) == set(range(v))
    X = sorted(set(D[0]) & set(D[1])); Pj = [sorted(set(D[j]) - set(X)) for j in range(2)]
    r = [rank_f2(B, R[j], A[j]) for j in range(2)]
    rX = rank_f2(B, X, X)
    ok = r[0] + r[1] >= v and r[0] >= len(Pj[0]) + rX and r[1] >= len(Pj[1]) + rX
    if X:
        al = {t: P[t, 0] / P[t, 1] for t in X}; be = {t: -Q[t, 1] / Q[t, 0] for t in X}
        lt = sum(1 for t in X if al[t] < be[t]); gt = sum(1 for t in X if al[t] > be[t])
        ok = ok and lt + gt == len(X) and rX >= max(lt, gt)
    return ok, r[0] + r[1] - v

rng = random.Random(20261013)
tot = bad = tight = 0; minslack = 10 ** 9
for nm, L in [("A3", ade.A(3)), ("A4", ade.A(4)), ("D4", ade.D(4)), ("D5", ade.D(5)), ("A5", ade.A(5)), ("D6", ade.D(6)), ("E6", ade.E6b())]:
    G = np.rint(L @ L.T).astype(int); n = nb = nt = 0
    for it in range(300):
        P, Q, M, B = instance(G, rng, it % 2)
        ok, slack = check(G, P, Q, M, B)
        n += 1; nb += (not ok); nt += (slack == 0); minslack = min(minslack, slack)
    print(f"{nm} v={len(G)} instances {n} violations {nb} tight(r1+r2=v) {nt}")
    tot += n; bad += nb; tight += nt
print(f"TOTAL instances {tot} violations {bad} tight {tight} min(r1+r2-v) {minslack}")
