"""Ejection-chain / cyclic-exchange search on a T16 owner map (final-state legality only).
State = (hand width, hand time). Max-plus DP over states, gains g(f)=f ln f; exact replay + seed67 audit.
argv: LIBDIR START_OWNERS OUT_PREFIX ROUNDS DEPTH"""
import sys, math, json, gzip, time, copy
sys.path.insert(0, sys.argv[1]); import lib
import numpy as np
from collections import defaultdict
start, outp, ROUNDS, L = sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
WS = [4, 5, 7, 8, 9]; WI = {w: i for i, w in enumerate(WS)}; T = 144; N = len(WS)*T
sid = lambda w, t: WI[w]*T + t
g = lib.g
NEG = np.float32(-1e9)

def build(m):
    A = np.full((N, N), NEG, np.float32); wit = {}
    absorb = np.full(N, NEG, np.float32); awit = {}
    for k in m.cap:
        f = m.free(k); mem = list(m.members[k]); fam = m.fam[k]
        for t in m.allowed[k]:
            famfree = fam not in m.occ[t]
            if famfree:
                for w in WS:
                    if f >= w:
                        s = sid(w, t); gn = g(f-w) - g(f)
                        if gn > absorb[s]: absorb[s] = gn; awit[s] = k
            for j in mem:
                z = m.roles[j]; w2, t2 = z['width'], z['time']
                if not (famfree or t2 == t): continue
                d = sid(w2, t2)
                for w in WS:
                    if f + w2 - w < 0: continue
                    s = sid(w, t); gn = g(f + w2 - w) - g(f)
                    if gn > A[s, d] + 1e-9: A[s, d] = gn; wit[s, d] = [(k, j)]
                    elif abs(gn - A[s, d]) <= 1e-9 and len(wit[s, d]) < 4: wit[s, d].append((k, j))
    return A, wit, absorb, awit

def maxplus(P, A):
    out = np.full((N, N), NEG, np.float32); arg = np.zeros((N, N), np.int16)
    for i in range(0, N, 24):
        blk = P[i:i+24, :, None] + A[None, :, :]
        arg[i:i+24] = blk.argmax(1); out[i:i+24] = blk.max(1)
    return out, arg

def paths(A):
    Ps, args = [A], [None]
    for d in range(1, L):
        P, ar = maxplus(Ps[-1], A); Ps.append(P); args.append(ar)
    return Ps, args

def recon(Ps, args, d, i, j):
    seq = [j]
    while d > 0:
        k = int(args[d][i, j]); seq.append(k); j = k; d -= 1
    seq.append(i); return seq[::-1]  # states i -> ... -> j

class Journal:
    def __init__(self, m): self.m = m; self.bins = {}; self.roles = {}; self.occ = {}
    def save(self, i):
        m = self.m; k = m.bin(i); t = m.roles[i]['time']
        if i not in self.roles: self.roles[i] = m.roles[i]
        if k not in self.bins: self.bins[k] = (set(m.members[k]), m.used[k])
        if t not in self.occ: self.occ[t] = set(m.occ[t])
    def savebin(self, k, t):
        m = self.m
        if k not in self.bins: self.bins[k] = (set(m.members[k]), m.used[k])
        if t not in self.occ: self.occ[t] = set(m.occ[t])
    def undo(self):
        m = self.m
        for i, z in self.roles.items(): m.roles[i] = z
        for k, (mem, u) in self.bins.items(): m.members[k] = mem; m.used[k] = u
        for t, o in self.occ.items(): m.occ[t] = o
        m._out = set()

def try_apply(m, X, r0, states, end, wit, awit, keep=False):
    """Exact replay with limbo on m in place (journaled). Returns (m, dE, moves, journal) or None (m restored)."""
    J = Journal(m); m._out = set(); before = {}
    def touch(k):
        if k not in before: before[k] = m.free(k)
    def lift(i): J.save(i); m.lift(i)
    def put(i, k):
        J.savebin(k, m.roles[i]['time']); return m.put(i, k)
    touch(X); lift(r0); hand = r0; moves = []
    def fail(): J.undo(); return None
    for a, b in zip(states, states[1:]):
        ok = False
        for (k, j) in wit[a, b]:
            if k in before or j in m._out or j == hand or m.bin(j) != k: continue
            touch(k); lift(j)
            if put(hand, k): moves.append((hand, k)); hand = j; ok = True; break
            put(j, k); before.pop(k)
        if not ok: return fail()
    if end == 'X':
        if not put(hand, X): return fail()
        moves.append((hand, X))
    else:
        k = awit[states[-1]]
        if k in before: return fail()
        touch(k)
        if not put(hand, k): return fail()
        moves.append((hand, k))
    assert not m._out
    dE = sum(g(m.free(k)) - g(f) for k, f in before.items())
    return m, dE, moves, J

def round_(m):
    t0 = time.time(); A, wit, absorb, awit = build(m); t1 = time.time()
    Ps, args = paths(A); t2 = time.time()
    stk = np.stack(Ps); best = np.max(stk, 0); bestd = np.argmax(stk, 0); del stk
    cands = []
    Tidx = np.arange(T)
    for X in m.cap:
        fX = m.free(X)
        if not m.members[X]: continue
        allowedX = np.zeros(T, bool); allowedX[list(m.allowed[X])] = True
        famocc = np.array([m.fam[X] in m.occ[t] for t in range(T)])
        for r0 in m.members[X]:
            z = m.roles[r0]; w0, t0_ = z['width'], z['time']; i = sid(w0, t0_)
            okT = allowedX & (~famocc | (Tidx == t0_))
            for wk in WS:
                if wk > fX + w0: continue
                row = best[i, WI[wk]*T:(WI[wk]+1)*T]
                tot = row + (g(fX + w0 - wk) - g(fX))
                tot = np.where(okT, tot, -1e9)
                for tk in np.nonzero(tot > 1e-6)[0]:
                    cands.append((float(tot[tk]), X, r0, i, sid(wk, int(tk)), 'X'))
            if absorb[i] + g(fX + w0) - g(fX) > 1e-6:
                cands.append((float(absorb[i] + g(fX + w0) - g(fX)), X, r0, i, i, 'A0'))
            # absorb endings
            tot = best[i] + absorb + (g(fX + w0) - g(fX))
            for j in np.nonzero(tot > 1e-6)[0]:
                cands.append((float(tot[j]), X, r0, i, int(j), 'A'))
    cands.sort(key=lambda c: -c[0])
    print(f'build {t1-t0:.0f}s paths {time.time()-t1:.0f}s cands {len(cands)} top {[round(c[0],3) for c in cands[:5]]}', flush=True)
    for c in cands[:5000]:
        gain, X, r0, i, j, end = c
        st = [i] if end == 'A0' else recon(Ps, args, int(bestd[i, j]), i, j)
        if end == 'A0': end = 'A'
        r = try_apply(m, X, r0, st, end, wit, awit)
        if r and r[1] > 1e-6: return r[:3]
        if r: r[3].undo()
    return None

m = lib.Limbo(lib.read(start)); m._out = set()
base = lib.selroles; log = []
print('start idle', dict(sorted(lib.idle_of(m.roles).items())), 'E', round(m.E(), 4), flush=True)
for rnd in range(ROUNDS):
    r = round_(m)
    if not r: print('no improving chain found at depth', L); break
    m, dE, moves = r
    roles = lib.compact(m.roles); au = lib.audit(roles)
    pr = lib.price(au['profile'])
    log.append(dict(round=rnd, dE=dE, moves=[(i, list(k)) for i, k in moves], idle=au['idle'], kappa=pr['kappa_decimal']))
    print('round', rnd, 'dE', round(dE, 4), 'moves', moves, 'idle', au['idle'], 'kappa', pr['kappa_decimal'], flush=True)
    m.roles = roles
    open(outp + '.OWNERS.json.gz', 'wb').write(gzip.compress(json.dumps(roles).encode(), mtime=0))
    json.dump(log, open(outp + '.log.json', 'w'), indent=1)
