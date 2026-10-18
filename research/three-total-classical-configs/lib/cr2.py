"""Char-2 realisability (CR2) of the incidence pattern used by an admissible B.
If points P~(t), lines Q~(s) over a field K of char 2 exist with supp P~(t) <= pi(t), supp Q~(s) <= sigma(s),
P~(t).Q~(s) = 0 for every off-diagonal B_ts = 1, P~(t).Q~(t) != 0, then
sum_j D(p~_j) B D(q~_j) = diag(P~(t).Q~(t)) has rank v over K, so cost(B) >= v (Hadamard argument of Lemma B, in char 2).
Exhaustive DFS over GF(2^k)."""
import itertools, sys
IRR = {1: 0b11, 2: 0b111, 3: 0b1011, 4: 0b10011, 5: 0b100101, 6: 0b1000011, 8: 0b100011011}
class GF:
    def __init__(s, k):
        s.k = k; s.q = 1 << k; m = IRR[k]
        s.mul = [[0] * s.q for _ in range(s.q)]
        for a in range(s.q):
            for b in range(s.q):
                r = 0; x = a; y = b
                while y:
                    if y & 1: r ^= x
                    y >>= 1; x <<= 1
                    if x & s.q: x ^= m
                s.mul[a][b] = r
        s.inv = [0] * s.q
        for a in range(1, s.q):
            for b in range(1, s.q):
                if s.mul[a][b] == 1: s.inv[a] = b
    def dot(s, a, b):
        return s.mul[a[0]][b[0]] ^ s.mul[a[1]][b[1]] ^ s.mul[a[2]][b[2]]

def proj_points(F, supp):
    """normalised projective points with support inside supp (first nonzero = 1)."""
    out = []
    for v in itertools.product(range(F.q), repeat=3):
        if not any(v): continue
        if any(v[j] and j not in supp for j in range(3)): continue
        f = next(x for x in v if x)
        if f != 1: continue
        out.append(v)
    return out

def realise(pi, sig, E, k=2, limit=10**6, want_all=False):
    """pi[t], sig[s]: allowed supports; E: set of (t,s) incidences required. Returns a realisation or None (exhaustive over GF(2^k))."""
    F = GF(k); v = len(pi)
    cand = {('p', t): proj_points(F, pi[t]) for t in range(v)}
    cand.update({('l', s): proj_points(F, sig[s]) for s in range(v)})
    nb = {x: [] for x in cand}
    for (t, s) in E:
        nb[('p', t)].append(('l', s)); nb[('l', s)].append(('p', t))
    other = {('p', t): ('l', t) for t in range(v)}; other.update({('l', t): ('p', t) for t in range(v)})
    asg = {}; nodes = [0]
    def ok(x, val):
        for y in nb[x]:
            if y in asg and F.dot(val, asg[y]) != 0: return False
        y = other[x]
        if y in asg and F.dot(val, asg[y]) == 0: return False
        return True
    def pick():
        best = None; bc = None
        for x in cand:
            if x in asg: continue
            c = [val for val in cand[x] if ok(x, val)]
            if bc is None or len(c) < len(bc):
                best, bc = x, c
                if len(c) <= 1: break
        return best, bc
    sols = []
    def dfs():
        nodes[0] += 1
        if nodes[0] > limit: raise TimeoutError
        if len(asg) == len(cand):
            sols.append(dict(asg)); return not want_all
        x, c = pick()
        for val in c:
            asg[x] = val
            if dfs(): return True
            del asg[x]
        return False
    try:
        dfs()
    except TimeoutError:
        return 'timeout'
    return sols if want_all else (sols[0] if sols else None)

def cfg_data(P, Q):
    v = len(P)
    pi = [{j for j in range(3) if P[t][j]} for t in range(v)]
    sig = [{j for j in range(3) if Q[t][j]} for t in range(v)]
    return pi, sig
