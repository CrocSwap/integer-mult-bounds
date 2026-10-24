"""Retiming / descent on a gcert/1 complex program: move gate frames inside
[span(LB_g + prev frames of participants), AND of next frames] with the source-span rule (the x-content support of every
non-y operand, and of a slot destination after the gate, lies in the gate frame). Pins: start, scatter (y at 0, retained
slots at their ret frame), final. Greedy best-improvement with the chi ledger at m = (2K+1)h.
usage: cxretime.py CERT.json.gz GXDIR OUT.json.gz [K] [sweeps]"""
import sys, os, gzip, json, math, random, copy
from fractions import Fraction as Fr
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cxkernel import reduce, inside, echelon, rehist, price


def regs_of(g):
    if g[0] == 'neg': return [g[2]]
    if g[0] == 'out': return [g[2]] + [t for t, _, _ in g[3]] + list(g[4])
    return [g[2]] + [s for s, _, _ in g[3]]


class CX:
    def __init__(self, c):
        self.c = c; v = c['v']; self.v = v; n = 2 * v + c['R']; self.n = n
        self.fr = [tuple(f) for f in c['frames']]; self.key = {f: i for i, f in enumerate(self.fr)}
        self.gates = [['A', g] for g in c['A']] + [['B', g] for g in c['B']]
        self.gf = [g[1] for _, g in self.gates]
        nA = len(c['A'])
        occ = [[('p', c['start'][r])] for r in range(n)]
        retf = {s: f for _, s, f in c['ret']}
        for gi, (ph, g) in enumerate(self.gates):
            if gi == nA:
                for t in range(v): occ[v + t].append(('p', 0))
                for s, f in retf.items(): occ[s].append(('p', f))
            for r in regs_of(g): occ[r].append(('g', gi))
        for r in range(n): occ[r].append(('p', c['final'][r]))
        self.occ = occ; self.where = [dict() for _ in self.gates]
        for r in range(n):
            for i, (k, x) in enumerate(occ[r]):
                if k == 'g': self.where[x][r] = i
        self.lb = self._lb()

    def _lb(self):
        c = self.c; v = self.v; ports = c['ports']
        sup = [{r} if r < v else set() for r in range(self.n)]
        lb = []
        for ph, g in self.gates:
            need = set()
            if g[0] == 'out':
                for t, _, _ in g[3]: sup[t] |= sup[g[2]]
                if g[2] < v or g[2] >= 2 * v: need |= sup[g[2]]
                for t, _, _ in g[3]:
                    if t >= 2 * v: need |= sup[t]
            elif g[0] == 'in':
                for s, _, _ in g[3]:
                    sup[g[2]] |= sup[s]
                    if s < v or s >= 2 * v: need |= sup[s]
                if g[2] >= 2 * v: need |= sup[g[2]]
            lb.append(tuple(echelon([ports[x] for x in need])))
        return lb

    def fid(self, f):
        f = tuple(f)
        if f not in self.key: self.key[f] = len(self.fr); self.fr.append(f)
        return self.key[f]

    def F(self, r, i):
        k, x = self.occ[r][i]; return x if k == 'p' else self.gf[x]

    def span_ok(self):
        return sum(1 for gi in range(len(self.gates)) if not inside(self.lb[gi], self.fr[self.gf[gi]]))


_sv = {}
def span_vecs(B):
    B = tuple(B)
    if B not in _sv:
        out = {0}
        for b in B: out |= {x ^ b for x in out}
        _sv[B] = frozenset(out)
    return _sv[B]


def block_of(M, gi):
    f = M.gf[gi]; S = {gi}; stack = [gi]
    while stack:
        g = stack.pop()
        for r, i in M.where[g].items():
            for j in (i - 1, i + 1):
                k, x = M.occ[r][j]
                if k == 'g' and x not in S and M.gf[x] == f: S.add(x); stack.append(x)
    return S


def try_move(M, S, chi, d, temp=0.0, rng=None):
    """move gate set S (all at one frame) to the best feasible frame; returns gain or None"""
    old = M.gf[next(iter(S))]; regs = {}
    for g in S:
        for r, i in M.where[g].items(): regs.setdefault(r, []).append(i)
    parts = []
    for r, ii in regs.items():
        lo_i, hi_i = min(ii), max(ii)
        if len(ii) != hi_i - lo_i + 1: return None
        parts.append((M.F(r, lo_i - 1), M.F(r, hi_i + 1)))
    loE = echelon([u for g in S for u in M.lb[g]] + [u for p, _ in parts for u in M.fr[p]])
    hiV = None
    for _, q in parts:
        vs = span_vecs(M.fr[q]); hiV = vs if hiV is None else hiV & vs
    if not all(u in hiV for u in loE): return None
    cands = {M.fid(loE), M.fid(echelon(sorted(hiV)))} | {p for p, _ in parts} | {q for _, q in parts}
    for u in sorted(hiV - span_vecs(loE)): cands.add(M.fid(echelon(loE + [u])))
    def ok(F):
        return all(inside(M.fr[p], M.fr[F]) and inside(M.fr[F], M.fr[q]) for p, q in parts) and inside(loE, M.fr[F])
    def score(F): return sum(chi(d(F) - d(p)) + chi(d(q) - d(F)) for p, q in parts)
    base = score(old); opts = [(score(F), F) for F in cands if F != old and ok(F)]
    if not opts: return None
    if temp > 0:
        sc, F = rng.choice(opts)
        if sc < base - 1e-12 or rng.random() < math.exp(-(sc - base) / temp):
            for g in S: M.gf[g] = F
            return base - sc
        return None
    sc, F = min(opts)
    if sc < base - 1e-12:
        for g in S: M.gf[g] = F
        return base - sc
    return None


def subblocks(M, S):
    T = sorted(S); out = [S]
    for k in range(1, len(T)): out.append(set(T[:k])); out.append(set(T[k:]))
    out += [{g} for g in T] if len(T) > 1 else []
    return out


def sweep(M, a, m, rng, temp=0.0):
    d = lambda f: len(M.fr[f]); chi = lambda r: 0.0 if r <= 0 else r * (math.exp(a * math.log(m / r)) - 1)
    moved = 0; gain = 0.0; idx = list(range(len(M.gates))); rng.shuffle(idx); done = set()
    for gi in idx:
        if gi in done: continue
        S = block_of(M, gi); done |= S
        subs = subblocks(M, S) if len(S) <= 12 else [S]
        if temp > 0: subs = [rng.choice(subs)]
        for sub in subs:
            g = try_move(M, sub, chi, d, temp, rng)
            if g is not None: moved += 1; gain += g; break
    return moved, gain


def to_cert(M):
    c = copy.deepcopy(M.c); c['frames'] = [list(f) for f in M.fr]
    A = []; B = []
    for gi, (ph, g) in enumerate(M.gates):
        g2 = copy.deepcopy(g); g2[1] = M.gf[gi]; (A if ph == 'A' else B).append(g2)
    c['A'] = A; c['B'] = B
    return rehist(c)


if __name__ == '__main__':
    c = json.load(gzip.open(sys.argv[1])); sys.path.insert(0, sys.argv[2]); import gx
    K = int(sys.argv[4]) if len(sys.argv) > 4 else 3; sw = int(sys.argv[5]) if len(sys.argv) > 5 else 20
    h = c['h']; m = (2 * K + 1) * h
    M = CX(c); print('span violations on input', M.span_ok())
    b0 = price(c, K); print('start b', b0, float(b0)); rng = random.Random(1)
    for s in range(sw):
        mv, g = sweep(M, float(b0), m, rng); print('sweep', s, 'moved', mv, 'chi/a %.4f' % (g / float(b0)), flush=True)
        if not mv: break
    w = to_cert(M); print('span violations', M.span_ok())
    st = {}; gx.check1(w, scalar=True, stats=st); print('gx.check1 PASS')
    for K2 in (2, 3): b = price(w, K2); print('b(B_%d) =' % K2, b, float(b))
    json.dump(w, gzip.open(sys.argv[3], 'wt'))
