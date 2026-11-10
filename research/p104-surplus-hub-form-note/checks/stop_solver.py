"""Numeric solver: multilinear stop model, Levenberg-Marquardt on the dual (J J^T) system.
Word = ordered stops; each stop applies a free matrix M_i (superset of ADD/SCALE) to the registers at one common frame.
Owned regs init 0, dropped at end (dirty clear). Public finals must equal the target exactly.
Skeleton: v independent ports e_r in F_2^v, N = diag (r.t = 0 for r != t).
Frame paths are monotone for public regs and are checked by assert_frames.
Unsolved is NOT a proof. Every table row is preceded by same-size planted and known-feasible controls.
usage: stop_solver.py v kd ku target restarts [seed] [family]"""
import sys, numpy as np

def skeleton(v, kd, ku, helpers=True, ee=None, family='onepass'):
    """returns names, npub, stops (list of (frame, reglist)).
    frames: frozenset of port indices = span of those e_r; pp(t) = all ports except t; V = all."""
    V = frozenset(range(v)); Z = frozenset()
    X = ['X%d' % r for r in range(v)]; Y = ['Y%d' % t for t in range(v)]
    K = ['h%d_%d' % (r, t) for r in range(v) for t in range(v) if r != t] if helpers else []
    B = ['B%d' % i for i in range(kd)]      # down rows V -> Z
    A = ['A%d' % i for i in range(ku)]      # up rows Z -> V (read at Z, landing at V1)
    A2 = []
    E = ['E%d' % i for i in range(v if ee is None else ee)]  # owned erasure at frame 0, never moves
    OV = ['O%d' % i for i in range(v if ee is None else ee)]  # owned scratch at V, never moves
    OL = ['Ol%d' % r for r in range(v)]     # one owned scratch per line stop
    OP = ['Op%d' % t for t in range(v)]     # one owned scratch per pp stop
    if family == 'twoup':                   # half of the up rows land only after a second read at Z2
        A2 = A[ku // 2:]; A = A[:ku // 2]
    G = ['g%d' % t for t in range(v)] if family in ('land', 'landdual', 'landboth') else []   # public helpers that stay at 0 through Z2, then climb to pp_t, then V
    if family in ('landdual', 'landboth'): K2 = ['u%d' % r for r in range(v)]                 # public helpers: 0 -> line r -> V, late to the line (dual role)
    else: K2 = []
    K = K + G + K2
    pub = X + Y + K; own = B + A + A2 + E + OV + OL + OP
    names = pub + own; idx = {n: i for i, n in enumerate(names)}
    st = []
    st.append((Z, Y + K + A + A2 + E))
    for r in range(v):
        st.append((frozenset([r]), [X[r], OL[r]] + [k for k in K if k.startswith('h%d_' % r)] + ([K2[r]] if K2 else [])))
    st.append((V, X + A + B + OV))
    st.append((Z, Y + B + E + A2 + G))
    if family == 'pingpong':                # one more X-top / Y-bottom exchange: rows are the only link
        st.append((V, X + A + B + OV)); st.append((Z, Y + B + E + A2))
    for t in range(v):
        st.append((frozenset(p for p in V if p != t), [Y[t], OP[t]] + [k for k in K if k.endswith('_%d' % t)] + ([G[t]] if G else [])))
    st.append((V, X + K + A + A2 + OV))   # B rows are NOT here: a down row that returned to V would be an uncounted up crossing
    return names, idx, len(pub), [(f, [idx[n] for n in regs]) for f, regs in st], (X, Y, K)

def assert_frames(names, npub, stops, v):
    """public regs must ascend, and X_r / Y_t must respect the pins; owned are free."""
    seen = {}
    for f, regs in stops:
        for i in regs:
            n = names[i]
            if i < npub:
                if n in seen: assert seen[n] <= f, ('descent', n)
                seen[n] = f
            if n[0] == 'X': assert int(n[1:]) in f, ('X pin', n)
            if n[0] == 'Y': assert int(n[1:]) not in f, ('Y pin', n)

def target(v, g, nk):
    a, b, c, d = g; n = 2 * v + nk; T = np.eye(n)
    T[:v, :v] = a * np.eye(v); T[:v, v:2 * v] = b * np.eye(v)
    T[v:2 * v, :v] = c * np.eye(v); T[v:2 * v, v:2 * v] = d * np.eye(v)
    return T

def forward(Ms, stops, nreg, npub):
    S = np.zeros((nreg, npub)); S[:npub, :npub] = np.eye(npub); pres = []
    for M, (f, r) in zip(Ms, stops):
        pres.append(S[r].copy()); S[r] = M @ S[r]
    return S, pres

def backward(Ms, stops, nreg, npub):
    P = np.zeros((npub, nreg)); P[:npub, :npub] = np.eye(npub); posts = [None] * len(stops)
    for i in range(len(stops) - 1, -1, -1):
        r = stops[i][1]; posts[i] = P[:, r].copy(); P[:, r] = P[:, r] @ Ms[i]
    return posts

def solve(T, stops, nreg, npub, rng, iters=400, sigma=.4, tol=1e-10, verbose=False):
    Ms = [np.eye(len(r)) + rng.normal(0, sigma, (len(r), len(r))) for f, r in stops]
    lam = 1e-1; S, pres = forward(Ms, stops, nreg, npub); R = S[:npub] - T; c = np.sum(R * R)
    n2 = npub * npub
    for it in range(iters):
        if c < tol * tol: break
        posts = backward(Ms, stops, nreg, npub)
        G = np.zeros((n2, n2))
        for P, Q in zip(posts, pres):
            G += np.kron(P @ P.T, Q.T @ Q)
        rhs = R.ravel()
        while True:
            W = np.linalg.solve(G + lam * np.eye(n2), rhs).reshape(npub, npub)
            new = [M - P.T @ W @ Q.T for M, P, Q in zip(Ms, posts, pres)]
            S2, pres2 = forward(new, stops, nreg, npub); R2 = S2[:npub] - T; c2 = np.sum(R2 * R2)
            if c2 < c:
                Ms, pres, R, c = new, pres2, R2, c2; lam = max(lam / 3, 1e-13); break
            lam *= 4
            if lam > 1e8: return Ms, np.sqrt(c), it
        if verbose and it % 20 == 0: print(it, np.sqrt(c), lam, flush=True)
    return Ms, np.sqrt(c), it

def legal(Ms, stops, nreg, npub):
    """Each stop must keep the rank of the content it touches (else it would erase public content without an owned home)."""
    S = np.zeros((nreg, npub)); S[:npub, :npub] = np.eye(npub); worst = 0
    for M, (f, r) in zip(Ms, stops):
        a = np.linalg.matrix_rank(S[r], tol=1e-7); S[r] = M @ S[r]; b = np.linalg.matrix_rank(S[r], tol=1e-7)
        worst = max(worst, a - b)
    return worst == 0, max(np.abs(M).max() for M in Ms)

GS = {'J': (0, -1, 1, 0), 'W': (1, -1, 1, 0), 'Wd': (0, -1, 1, 1), 'F': (1, 0, 1, 1), 'FB': (1, -1, 1, 0.5), 'I': (1, 0, 0, 1)}

def run(v, kd, ku, tg, restarts, seed=0, family='onepass', helpers=True, planted=False, iters=600):
    names, idx, npub, stops, (X, Y, K) = skeleton(v, kd, ku, helpers, family=family)
    assert_frames(names, npub, stops, v); nreg = len(names); rng = np.random.default_rng(seed)
    if planted:
        Ms = [np.eye(len(r)) + rng.normal(0, .5, (len(r), len(r))) for f, r in stops]
        T = forward(Ms, stops, nreg, npub)[0][:npub]
    else:
        T = target(v, GS[tg], len(K))
    hits = 0; best = 1e9; legalhits = 0; bm = None
    for i in range(restarts):
        Ms, res, it = solve(T, stops, nreg, npub, rng, iters=iters)
        best = min(best, res)
        if res < 1e-8:
            hits += 1; ok, mx = legal(Ms, stops, nreg, npub); legalhits += ok
            if ok and bm is None: bm = Ms
    return dict(v=v, kd=kd, ku=ku, tg='planted' if planted else tg, fam=family, helpers=helpers, npub=npub, nreg=nreg, hits=hits, legal=legalhits, restarts=restarts, best=best), bm, stops, names

if __name__ == '__main__':
    v, kd, ku = map(int, sys.argv[1:4]); tg = sys.argv[4]; rs = int(sys.argv[5])
    seed = int(sys.argv[6]) if len(sys.argv) > 6 else 0; fam = sys.argv[7] if len(sys.argv) > 7 else 'onepass'
    print(run(v, kd, ku, tg, rs, seed, fam, planted=(tg == 'planted'))[0], flush=True)
