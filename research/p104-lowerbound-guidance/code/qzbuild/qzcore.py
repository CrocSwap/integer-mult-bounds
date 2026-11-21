# QZBUILD core (own code). Word-level model of a Q=0 lifted caller (QZ LIFT lemma):
# data = per incidence e (contacts + idles) a rank-1 idempotent pi_e = v_e w_e^T (pulled-back +frame), per stage (a_t,b_t).
# HOST stage-t twist  V_t = I + 2ab(vs ws^T + vt wt^T) - 2a vs wt^T - 2b(1+ab) vt ws^T   (contacts s,t right after the HOST)
# -frame projections pi^-_e = L_e^{-1} pi_e L_e, L_e = prod of V over HOSTs at/before e (later on the left).
# Legal  <=>  R+(D) = R-(D) = diag(D^M)  and  prod V = -I   (R(D) = prod_e (I + (D^{S_e}-1) pi_e), later on the left).
import os
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'): os.environ[v] = '1'
import numpy as np
from scipy.optimize import least_squares

class Design:
    """events: list of ('H', t) or ('I', frozenset S); every H is followed by its two contacts (stage {t})."""
    def __init__(s, n, k, masks, events, name=''):
        s.n, s.k, s.masks, s.events, s.name = n, k, [frozenset(m) for m in masks], events, name
        s.inc = []          # (S, host_index_or_None, position)
        s.hosts = []        # stage per host in time order
        s.hostinc = []      # (inc index s, inc index t) per host
        for ev in events:
            if ev[0] == 'H':
                t = ev[1]; s.hosts.append(t)
                i0 = len(s.inc); s.inc.append((frozenset({t}), len(s.hosts)-1)); s.inc.append((frozenset({t}), len(s.hosts)-1))
                s.hostinc.append((i0, i0+1))
            else:
                s.inc.append((frozenset(ev[1]), None))
        # number of hosts before each incidence (incl. own host for contacts)
        s.nh = []; h = 0; idx = 0
        for ev in events:
            if ev[0] == 'H':
                h += 1; s.nh += [h, h]
            else: s.nh.append(h)
        s.m = len(s.inc)
        s.nv = 2*n*s.m + 2*len(s.hosts)
        assert sorted(s.hosts) == list(range(k)), 'each stage exactly one HOST'
        # stage incidence count check vs masks
        for t in range(k):
            a = sum(1 for (S, _) in s.inc if t in S); b = sum(1 for M in s.masks if t in M)
            assert a == b, ('stage incidence mismatch', t, a, b)
    def unpack(s, z):
        n, m = s.n, s.m
        V = z[:n*m].reshape(m, n); W = z[n*m:2*n*m].reshape(m, n); ab = z[2*n*m:].reshape(-1, 2)
        return V, W, ab
    def twists(s, V, W, ab):
        n = s.n; out = []
        for h, (i, j) in enumerate(s.hostinc):
            a, b = ab[h]
            X = np.eye(n) + 2*a*b*(np.outer(V[i], W[i]) + np.outer(V[j], W[j])) - 2*a*np.outer(V[i], W[j]) - 2*b*(1+a*b)*np.outer(V[j], W[i])
            out.append(X)
        return out
    def frames(s, z):
        V, W, ab = s.unpack(z); n = s.n
        Tw = s.twists(V, W, ab)
        L = [np.eye(n)]
        for X in Tw: L.append(X @ L[-1])
        Vm = np.zeros_like(V); Wm = np.zeros_like(W)
        for e in range(s.m):
            Le = L[s.nh[e]]
            Vm[e] = np.linalg.solve(Le, V[e]); Wm[e] = Le.T @ W[e]
        return V, W, Vm, Wm, Tw, L[-1], ab

def make_samples(k, ns, rng):
    return rng.uniform(0.4, 1.8, size=(ns, k))

def residual(d, z, Ds, wD=1.0):
    n, m = d.n, d.m
    V, W, Vm, Wm, Tw, P, ab = d.frames(z)
    res = []
    res.append(np.einsum('ij,ij->i', V, W) - 1)
    res.append((P + np.eye(n)).ravel())
    for (VV, WW) in ((V, W), (Vm, Wm)):
        # per stage: sum pi = E_t, biorth
        for t in range(d.k):
            idx = [e for e in range(m) if t in d.inc[e][0]]
            Et = np.diag([1.0 if t in M else 0.0 for M in d.masks])
            res.append((VV[idx].T @ WW[idx] - Et).ravel())
            G = WW[idx] @ VV[idx].T
            res.append((G - np.eye(len(idx))).ravel())
        for D in Ds:
            R = np.eye(n)
            for e in range(m):
                x = np.prod([D[t] for t in d.inc[e][0]])
                R = R + (x-1)*np.outer(VV[e], WW[e] @ R)
            T = np.diag([np.prod([D[t] for t in M]) for M in d.masks])
            res.append(wD*(R - T).ravel())
    return np.concatenate(res)

def solve(d, seed=0, ns=12, tries=1, maxfev=4000, z0=None, scale=1.0, verbose=False):
    rng = np.random.default_rng(seed)
    Ds = make_samples(d.k, ns, rng)
    best = None
    for tr in range(tries):
        z = z0.copy() if (z0 is not None and tr == 0) else rng.normal(size=d.nv)*scale
        r = least_squares(lambda zz: residual(d, zz, Ds), z, method='lm', max_nfev=maxfev, xtol=1e-15, ftol=1e-15, gtol=1e-15)
        nr = np.linalg.norm(r.fun)
        if verbose: print('  try', tr, 'res %.2e' % nr, flush=True)
        if best is None or nr < best[0]: best = (nr, r.x)
        if nr < 1e-10: break
    return best

def check_nondeg(d, z):
    V, W, ab = d.unpack(z)
    return [(float(a), float(b), float(a*b)) for a, b in ab]

S = 0.99
def chat(d):
    inv = sum((8*len(M)+1)**S for M in d.masks) - sum((8*len(Sx))**S for (Sx, _) in d.inc)
    return 104*inv/d.k
def HP(k):
    return 208/k*((k-2)*(17**S-16**S) + (8*k+1)**S - 8**S*k)
