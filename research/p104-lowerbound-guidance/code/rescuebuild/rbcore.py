"""RESCUEBUILD rbcore: design model, exact invoice, numeric frame+piece solver (scout only; claims need rbexact).
Design: k stages (call positions 0..k-1), roles = list of (mask, pieces); pieces = idle pieces (frozensets, singletons allowed);
mains = mask minus union(pieces).  Frame (hat / zero-sum gauge, BL.md 1):
  walk Q_0=I, Q_1..Q_{k-1} in SL2, Q_k=-I;  alpha_s = Q_{s+1}^-1 - Q_s^-1, beta_t = Q_{t+1} - Q_t  (0-based stage s uses Q_{s+1})
  Ghat_st = 1/4 eps_st alpha_s beta_t (s!=t), eps=+1 if s<=t else -1;  diagonal by zero block sums.
  roles: bh_r, ah_r in R^{2k}, supported on mask blocks, zero block sum;  sum_r bh_r ah_r^T = Ghat.
  pieces q: x_q, y_q in R^{E(q)} (E(q) = roles whose mask contains q); sum_r x_q[r] bh_r[t] = 0, sum_r y_q[r] ah_r[t] = 0 (t in q);
  y_q . x_q' = delta for q,q' sharing a stage.
"""
import numpy as np, itertools
from decimal import Decimal as Dm, getcontext
getcontext().prec = 50

def check_design(k, roles):
    mains = [0]*k
    for M, P in roles:
        U = set()
        for p in P:
            assert p <= M and not (p & U), (M, P); U |= p
        for t in M - U: mains[t] += 1
    return mains

def value(D, P, s=Dm('0.99')):
    return (Dm(8*D+1))**s - sum((Dm(8*L))**s for L in P)

def chat(k, roles, s=Dm('0.99')):
    tot = Dm(0)
    for M, P in roles:
        U = set().union(*P) if P else set()
        L = [len(p) for p in P] + [1]*len(M - U)
        tot += value(len(M), L, s)
    return Dm(104)/k*tot

def pieces_of(roles):
    """list of (owner, piece)"""
    return [(r, p) for r, (M, P) in enumerate(roles) for p in P]

def E_of(roles, q):
    return [r for r, (M, P) in enumerate(roles) if q <= M]

# ---------- walk ----------
def walk_mats(qpar, k):
    """qpar: (k-1)*3 params -> Q_1..Q_{k-1} in SL2 via [[a,b],[c,(1+bc)/a]]"""
    Q = [np.eye(2)]
    for i in range(k-1):
        a, b, c = qpar[3*i:3*i+3]
        Q.append(np.array([[a, b], [c, (1+b*c)/a]]))
    Q.append(-np.eye(2))
    return Q

def ghat(Q, k):
    inv = [np.linalg.inv(q) for q in Q]
    al = [inv[s+1]-inv[s] for s in range(k)]
    be = [Q[t+1]-Q[t] for t in range(k)]
    G = np.zeros((2*k, 2*k))
    for s in range(k):
        for t in range(k):
            if s != t:
                G[2*s:2*s+2, 2*t:2*t+2] = 0.25*(1 if s <= t else -1)*al[s]@be[t]
    for s in range(k):
        G[2*s:2*s+2, 2*s:2*s+2] = -sum(G[2*s:2*s+2, 2*t:2*t+2] for t in range(k) if t != s)
    return G

class Sys:
    def __init__(s_, k, roles, walk=None):
        s_.k, s_.roles = k, roles; n = len(roles); s_.n = n
        s_.pc = pieces_of(roles); s_.E = [E_of(roles, q) for _, q in s_.pc]
        s_.walk = walk
        # variable layout
        s_.idx = {}; off = 0
        if walk is None: s_.idx['Q'] = (off, 3*(k-1)); off += 3*(k-1)
        for r, (M, P) in enumerate(roles):
            for t in sorted(M):
                s_.idx[('b', r, t)] = off; off += 2
                s_.idx[('a', r, t)] = off; off += 2
        for i, q in enumerate(s_.pc):
            s_.idx[('x', i)] = off; off += len(s_.E[i])
            s_.idx[('y', i)] = off; off += len(s_.E[i])
        s_.nv = off
        s_.pairs = [(i, j) for i in range(len(s_.pc)) for j in range(len(s_.pc)) if s_.pc[i][1] & s_.pc[j][1]]
    def unpack(s_, z):
        k, n = s_.k, s_.n
        Q = walk_mats(z[s_.idx['Q'][0]:s_.idx['Q'][0]+3*(k-1)], k) if s_.walk is None else s_.walk
        B = np.zeros((n, 2*k)); A = np.zeros((n, 2*k))
        for r, (M, P) in enumerate(s_.roles):
            for t in M:
                o = s_.idx[('b', r, t)]; B[r, 2*t:2*t+2] = z[o:o+2]
                o = s_.idx[('a', r, t)]; A[r, 2*t:2*t+2] = z[o:o+2]
        X = []; Y = []
        for i in range(len(s_.pc)):
            o = s_.idx[('x', i)]; L = len(s_.E[i])
            x = np.zeros(n); x[s_.E[i]] = z[o:o+L]; X.append(x)
            o = s_.idx[('y', i)]; y = np.zeros(n); y[s_.E[i]] = z[o:o+L]; Y.append(y)
        return Q, B, A, X, Y
    def res(s_, z):
        k = s_.k
        Q, B, A, X, Y = s_.unpack(z)
        G = ghat(Q, k)
        out = [(B.T@A - G).ravel()]
        out.append((B.reshape(s_.n, k, 2).sum(1)).ravel()); out.append((A.reshape(s_.n, k, 2).sum(1)).ravel())
        for i, (_, q) in enumerate(s_.pc):
            for t in q:
                out.append(X[i]@B[:, 2*t:2*t+2]); out.append(Y[i]@A[:, 2*t:2*t+2])
        out.append(np.array([Y[i]@X[j] - (i == j) for i, j in s_.pairs]))
        return np.concatenate(out)
    def solve(s_, seed, tries=20, tol=1e-11, maxfev=4000):
        from scipy.optimize import least_squares
        rng = np.random.default_rng(seed); best = None
        for _ in range(tries):
            z0 = rng.normal(size=s_.nv)
            if s_.walk is None:
                o = s_.idx['Q'][0]
                for i in range(k_ := s_.k - 1):
                    z0[o+3*i] = rng.uniform(0.6, 1.6)*rng.choice([-1, 1])
            r = least_squares(s_.res, z0, method='trf', xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=maxfev)
            nr = np.abs(s_.res(r.x)).max()
            if best is None or nr < best[0]: best = (nr, r.x)
            if nr < tol: break
        return best
    def diag(s_, z):
        """genericity diagnostics of a solution"""
        k = s_.k; Q, B, A, X, Y = s_.unpack(z)
        W = [-Q[t+1]@np.linalg.inv(Q[t]) for t in range(k)]
        tr = [float(np.trace(w)) for w in W]
        eff = []
        for r, (M, P) in enumerate(s_.roles):
            eff.append({t: (round(float(np.abs(B[r, 2*t:2*t+2]).max()), 4), round(float(np.abs(A[r, 2*t:2*t+2]).max()), 4)) for t in sorted(M)})
        own = [(round(float(X[i][o]), 4), round(float(Y[i][o]), 4)) for i, (o, q) in enumerate(s_.pc)]
        return dict(tr=[round(x, 4) for x in tr], svB=float(np.linalg.svd(B, compute_uv=False).min()),
                    svA=float(np.linalg.svd(A, compute_uv=False).min()), eff=eff, own=own)

def to_real(Q, B, A, k):
    """hat frame -> real twists V_t = I + A_t B_t^T (SK normal form, G = Etil diag(W+I) - 2I)."""
    W = [-Q[t+1]@np.linalg.inv(Q[t]) for t in range(k)]
    T = [None]*k; T[k-1] = np.eye(2)
    for t in range(k-1, 0, -1): T[t-1] = -T[t]@W[t]
    lamT = [0.5*T[t]@(W[t]+np.eye(2)) for t in range(k)]           # lam_t^T
    kap = [0.5*(W[t]+np.eye(2))@Q[t] for t in range(k)]
    n = B.shape[0]; Br = np.zeros_like(B); Ar = np.zeros_like(A)
    for t in range(k):
        Br[:, 2*t:2*t+2] = B[:, 2*t:2*t+2]@np.linalg.inv(lamT[t]).T   # b = lam^{-T} bh  (row form: bh^T lam^{-1}... )
        Ar[:, 2*t:2*t+2] = A[:, 2*t:2*t+2]@np.linalg.inv(kap[t])@(W[t]+np.eye(2))
    P = np.eye(n)
    for t in range(k):
        V = np.eye(n) + Ar[:, 2*t:2*t+2]@Br[:, 2*t:2*t+2].T
        P = V@P
    return P, W

class FSys(Sys):
    """fixed-walk system with analytic Jacobian (all equations bilinear)."""
    def __init__(s_, k, roles, walk):
        super().__init__(k, roles, walk=walk); s_.G = ghat(walk, k)
        n = s_.n; s_.bi = -np.ones((n, 2*k), int); s_.ai = -np.ones((n, 2*k), int)
        for r, (M, P) in enumerate(roles):
            for t in M:
                o = s_.idx[('b', r, t)]; s_.bi[r, 2*t:2*t+2] = [o, o+1]
                o = s_.idx[('a', r, t)]; s_.ai[r, 2*t:2*t+2] = [o, o+1]
        s_.xi = [{r: s_.idx[('x', i)]+j for j, r in enumerate(s_.E[i])} for i in range(len(s_.pc))]
        s_.yi = [{r: s_.idx[('y', i)]+j for j, r in enumerate(s_.E[i])} for i in range(len(s_.pc))]
    def jac(s_, z):
        k, n = s_.k, s_.n; Q, B, A, X, Y = s_.unpack(z); K = 2*k
        rows = []
        J1 = np.zeros((K*K, s_.nv))
        for r in range(n):
            for i in range(K):
                if s_.bi[r, i] >= 0: J1[i*K:(i+1)*K, s_.bi[r, i]] += A[r, :]
                if s_.ai[r, i] >= 0: J1[i::K, s_.ai[r, i]] += B[r, :]
        rows.append(J1)
        Jz = np.zeros((2*n*2, s_.nv))
        for r in range(n):
            for c in range(2):
                for t in range(k):
                    if s_.bi[r, 2*t+c] >= 0: Jz[2*r+c, s_.bi[r, 2*t+c]] = 1
                    if s_.ai[r, 2*t+c] >= 0: Jz[2*n+2*r+c, s_.ai[r, 2*t+c]] = 1
        rows.append(Jz)
        for i, (_, q) in enumerate(s_.pc):
            for t in q:
                Jb = np.zeros((2, s_.nv)); Ja = np.zeros((2, s_.nv))
                for r in s_.E[i]:
                    for c in range(2):
                        Jb[c, s_.xi[i][r]] = B[r, 2*t+c]; Jb[c, s_.bi[r, 2*t+c]] += X[i][r]
                        Ja[c, s_.yi[i][r]] = A[r, 2*t+c]; Ja[c, s_.ai[r, 2*t+c]] += Y[i][r]
                rows += [Jb, Ja]
        Jp = np.zeros((len(s_.pairs), s_.nv))
        for m, (i, j) in enumerate(s_.pairs):
            for r in s_.E[i]:
                if r in s_.xi[j]: Jp[m, s_.yi[i][r]] += X[j][r]; Jp[m, s_.xi[j][r]] += Y[i][r]
        rows.append(Jp)
        return np.vstack(rows)
    def res(s_, z):
        Q, B, A, X, Y = s_.unpack(z); k = s_.k
        out = [(B.T@A - s_.G).ravel(), (B.reshape(s_.n, k, 2).sum(1)).ravel(), (A.reshape(s_.n, k, 2).sum(1)).ravel()]
        for i, (_, q) in enumerate(s_.pc):
            for t in q: out += [X[i]@B[:, 2*t:2*t+2], Y[i]@A[:, 2*t:2*t+2]]
        out.append(np.array([Y[i]@X[j] - (i == j) for i, j in s_.pairs]))
        return np.concatenate(out)
    def lm(s_, z, it=400, tol=1e-12):
        mu = 1e-3; f = s_.res(z); c = f@f
        for _ in range(it):
            J = s_.jac(z); g = J.T@f; H = J.T@J
            while True:
                dz = -np.linalg.solve(H + mu*np.diag(np.diag(H) + 1e-9), g)
                f2 = s_.res(z+dz); c2 = f2@f2
                if c2 < c: z, f, c = z+dz, f2, c2; mu = max(mu/3, 1e-12); break
                mu *= 4
                if mu > 1e12: return z, np.abs(f).max()
            if np.abs(f).max() < tol: break
        return z, np.abs(f).max()
    def solve(s_, seed, tries=20, tol=1e-11, maxfev=400):
        rng = np.random.default_rng(seed); best = None
        for _ in range(tries):
            z, nr = s_.lm(rng.normal(size=s_.nv), it=maxfev, tol=tol)
            if best is None or nr < best[0]: best = (nr, z)
            if nr < tol: break
        return best

class WSys(FSys):
    """free walk: variables = [qpar (3(k-1)) | FSys vars]; walk Jacobian by central differences.
    pen: soft genericity rows  pen/ (1 + (tr W_t +- 2)^2)  pushing traces away from +-2."""
    def __init__(s_, k, roles, pen=0.0):
        s_.nq = 3*(k-1); s_.pen = pen
        s_.tau = np.random.default_rng(int(pen*1000)+7).uniform(-1.6, 1.6, size=k)
        super().__init__(k, roles, walk_mats(np.ones(3*(k-1)), k))
    def split(s_, z):
        return z[:s_.nq], z[s_.nq:]
    def setw(s_, qp):
        s_.walk = walk_mats(qp, s_.k); s_.G = ghat(s_.walk, s_.k)
    def penrows(s_, qp):
        Q = walk_mats(qp, s_.k); out = []
        for t in range(s_.k):
            W = -Q[t+1]@np.linalg.inv(Q[t]); tr = np.trace(W)
            out += [10.0*(tr - s_.tau[t])]
        return np.array(out)
    def resw(s_, z):
        qp, w = s_.split(z); s_.setw(qp)
        return np.concatenate([FSys.res(s_, w), s_.penrows(qp)])
    def jacw(s_, z):
        qp, w = s_.split(z); s_.setw(qp); Jw = FSys.jac(s_, w)
        f0 = s_.resw(z); Jq = np.zeros((len(f0), s_.nq))
        for i in range(s_.nq):
            h = 1e-6*max(1, abs(qp[i])); e = np.zeros(len(z)); e[i] = h
            Jq[:, i] = (s_.resw(z+e) - s_.resw(z-e))/(2*h)
        s_.setw(qp)
        Jfull = np.zeros((len(f0), len(z))); Jfull[:, :s_.nq] = Jq; Jfull[:Jw.shape[0], s_.nq:] = Jw
        return Jfull
    def lm(s_, z, it=400, tol=1e-12):
        mu = 1e-3; f = s_.resw(z); c = f@f; m = len(f)
        for _ in range(it):
            J = s_.jacw(z); g = J.T@f; H = J.T@J
            while True:
                try: dz = -np.linalg.solve(H + mu*np.diag(np.diag(H) + 1e-9), g)
                except np.linalg.LinAlgError: mu *= 4; continue
                z2 = z+dz
                try: f2 = s_.resw(z2)
                except np.linalg.LinAlgError: f2 = None
                if f2 is not None and np.all(np.isfinite(f2)) and f2@f2 < c: z, f, c = z2, f2, f2@f2; mu = max(mu/3, 1e-12); break
                mu *= 4
                if mu > 1e12: return z, np.abs(f[:m]).max()
            if np.abs(f[:m]).max() < tol: break
        return z, np.abs(f[:m]).max()
    def solve(s_, seed, tries=20, tol=1e-11, maxfev=400):
        rng = np.random.default_rng(seed); best = None
        for _ in range(tries):
            qp = np.concatenate([[rng.uniform(.7, 1.5)*rng.choice([-1, 1]), rng.normal(), rng.normal()] for _ in range(s_.k-1)])
            z, nr = s_.lm(np.concatenate([qp, rng.normal(size=s_.nv)]), it=maxfev, tol=tol)
            if best is None or nr < best[0]: best = (nr, z)
            if nr < tol: break
        return best
    def wdiag(s_, z):
        qp, w = s_.split(z); s_.setw(qp); Q = s_.walk
        tr = [float(np.trace(-Q[t+1]@np.linalg.inv(Q[t]))) for t in range(s_.k)]
        Qs, B, A, X, Y = s_.unpack(w); P, W = to_real(Q, B, A, s_.k)
        return dict(tr=[round(x, 4) for x in tr], prod=float(np.abs(P+np.eye(s_.n)).max()), svB=float(np.linalg.svd(B, compute_uv=False).min()), svA=float(np.linalg.svd(A, compute_uv=False).min()))

def walk_gen(qp, k):
    """Q_1..Q_{k-1} general 2x2 (4 params each); det enforced by residual."""
    return [np.eye(2)] + [qp[4*i:4*i+4].reshape(2, 2) for i in range(k-1)] + [-np.eye(2)]

class WSys2(FSys):
    """free walk (general 2x2 Q, det=1 residual) + barrier w/(tr W_t +- 2); then polish with fixed walk."""
    def __init__(s_, k, roles, bw=1e-3):
        s_.nq = 4*(k-1); s_.bw = bw
        super().__init__(k, roles, walk_mats(np.ones(3*(k-1)), k))
    def setw(s_, qp):
        s_.walk = walk_gen(qp, s_.k); s_.G = ghat(s_.walk, s_.k)
    def extra(s_, qp):
        Q = walk_gen(qp, s_.k); out = [np.linalg.det(Q[i]) - 1 for i in range(1, s_.k)]
        for t in range(s_.k):
            W = -Q[t+1]@np.linalg.inv(Q[t]); tr = np.trace(W)
            out += [s_.bw/(tr+2), s_.bw/(tr-2)]
        return np.array(out)
    def resw(s_, z):
        qp, w = z[:s_.nq], z[s_.nq:]; s_.setw(qp)
        return np.concatenate([FSys.res(s_, w), s_.extra(qp)])
    def jacw(s_, z):
        qp, w = z[:s_.nq], z[s_.nq:]; s_.setw(qp); Jw = FSys.jac(s_, w)
        f0 = s_.resw(z); Jq = np.zeros((len(f0), s_.nq))
        for i in range(s_.nq):
            h = 1e-7; e = np.zeros(len(z)); e[i] = h
            Jq[:, i] = (s_.resw(z+e) - s_.resw(z-e))/(2*h)
        s_.setw(qp); J = np.zeros((len(f0), len(z))); J[:, :s_.nq] = Jq; J[:Jw.shape[0], s_.nq:] = Jw
        return J
    def lm(s_, z, it=400, tol=1e-10):
        mu = 1e-3; f = s_.resw(z); c = f@f; m = len(f) - 2*s_.k
        for _ in range(it):
            J = s_.jacw(z); g = J.T@f; H = J.T@J
            while True:
                try: dz = -np.linalg.solve(H + mu*np.diag(np.diag(H) + 1e-9), g)
                except np.linalg.LinAlgError: mu *= 4; continue
                try: f2 = s_.resw(z+dz)
                except np.linalg.LinAlgError: f2 = None
                if f2 is not None and np.all(np.isfinite(f2)) and f2@f2 < c: z, f, c = z+dz, f2, f2@f2; mu = max(mu/3, 1e-12); break
                mu *= 4
                if mu > 1e12: return z, np.abs(f[:m]).max()
            if np.abs(f[:m]).max() < tol: break
        return z, np.abs(f[:m]).max()
    def attempt(s_, seed, tries=10, it=600):
        rng = np.random.default_rng(seed); best = None
        for _ in range(tries):
            qp = np.concatenate([np.array([[rng.uniform(.5, 1.5), rng.normal()], [rng.normal(), 0]]).ravel() for _ in range(s_.k-1)])
            for i in range(s_.k-1):  # set det=1
                a, b, c_, _ = qp[4*i:4*i+4]; qp[4*i+3] = (1+b*c_)/a
            z, nr = s_.lm(np.concatenate([qp, rng.normal(size=s_.nv)]), it=it)
            if best is None or nr < best[0]: best = (nr, z)
            if nr < 1e-9: break
        nr, z = best; qp = z[:s_.nq]; Q = walk_gen(qp, s_.k)
        tr = [float(np.trace(-Q[t+1]@np.linalg.inv(Q[t]))) for t in range(s_.k)]
        return nr, z, tr
    def polish(s_, z):
        qp = z[:s_.nq]; Q = walk_gen(qp, s_.k); S = FSys(s_.k, s_.roles, Q)
        zz, nr = S.lm(z[s_.nq:], it=200, tol=1e-13); return nr, S, zz
