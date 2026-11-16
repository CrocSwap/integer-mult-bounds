# LOANBUILD engine (own code). SYLforge's lifetime device as an exact, solver-backed builder.
# A candidate = path edit (r drops X; partner p inserts B after X [side B] or A before X [side A]) + template ops whose
# coefficients are partly enumerated and partly unknown; the unknowns enter linearly, so the window replay (mod 2^61-1,
# k-dim random projection) is affine in them and is solved exactly, then rationalised and verified by full replay.
# Equality targets: full register state at window end + every pre-existing owned observation (src/dst content at each
# owned-touching op) + every pre-existing CLEAR content inside the window.
import sys, math, bisect, collections, itertools
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
from fractions import Fraction as Q
import pricekit as pk  # vendored in this directory
PM = 2 ** 61 - 1; K = 4

def spanmask(b):
    S = {0}
    for v in b: S |= {x ^ v for x in S}
    m = 0
    for x in S: m |= 1 << x
    return m

_qc = {}
def qmod(s):
    c = _qc.get(s)
    if c is None:
        q = Q(s); c = _qc[s] = q.numerator % PM * pow(q.denominator % PM, -1, PM) % PM
    return c

def ratrec(a, bound=1 << 28):
    """rational reconstruction of a mod PM"""
    r0, r1, s0, s1 = PM, a % PM, 0, 1
    while r1 >= bound:
        qq = r0 // r1; r0, r1 = r1, r0 - qq * r1; s0, s1 = s1, s0 - qq * s1
    if s1 == 0 or abs(s1) >= bound: return None
    q = Q(r1, s1)
    if (q.numerator - a * q.denominator) % PM: return None
    return q

class Word:
    def __init__(s, W, ck=500, seed=1):
        s.W = W; s.n = n = W['public']; s.NO = W['owned_fields']; s.N = n + s.NO; P = W['program']; s.T = len(P)
        s.sp = [spanmask(b) for b in W['frames']]; s.dim = [len(b) for b in W['frames']]
        import random; rng = random.Random(seed)
        s.R = [[rng.randrange(1, PM) for _ in range(K)] for _ in range(n)]
        # residences of public regs: list of (chart, tin, tout)
        s.seg = collections.defaultdict(list); cur = list(W['initial']); tin = [-1] * n
        for i, e in enumerate(P):
            if e[0] == 'MOVE' and e[1] < n:
                r = e[1]; s.seg[r].append((cur[r], tin[r], i)); cur[r] = e[3]; tin[r] = i
        for r in range(n): s.seg[r].append((cur[r], tin[r], s.T))
        # ops per register (non-MOVE, public involvement), with chart
        s.ops = collections.defaultdict(list)
        for i, e in enumerate(P):
            if e[0] in ('ADD', 'COPY'):
                s.ops[e[1]].append(i); s.ops[e[2]].append(i)
            elif e[0] == 'SCALE': s.ops[e[1]].append(i)
        # owned live intervals
        s.olive = collections.defaultdict(list); st = {}
        for i, e in enumerate(P):
            if e[0] == 'INIT': st[e[1]] = i
            elif e[0] == 'CLEAR': s.olive[e[1]].append((st.pop(e[1]), i))
        s.prof = [0] * (s.T + 1); live = 0
        for i, e in enumerate(P):
            if e[0] == 'INIT': live += 1
            elif e[0] == 'CLEAR': live -= 1
            s.prof[i] = live
        # checkpoints of the projected state
        s.ck = ck; s.cks = []
        M = s.init_state()
        for i, e in enumerate(P):
            if i % ck == 0: s.cks.append([list(x) for x in M])
            s.step(M, e)
    def init_state(s):
        return [list(s.R[r]) for r in range(s.n)] + [[0] * K for _ in range(s.NO)]
    @staticmethod
    def step(M, e, vals=None):
        op = e[0]
        if op == 'MOVE': return
        if op in ('INIT', 'CLEAR'): M[e[1]] = [0] * K; return
        if op == 'SCALE':
            q = qmod(e[2]) if not str(e[2]).startswith('$') else vals[e[2]]
            M[e[1]] = [x * q % PM for x in M[e[1]]]; return
        c = e[3]; q = vals[c] if str(c).startswith('$') else qmod(c)
        if op == 'COPY': M[e[1]] = [0] * K
        if q: M[e[1]] = [(x + q * y) % PM for x, y in zip(M[e[1]], M[e[2]])]
    def state_at(s, i):
        j = i // s.ck; M = [list(x) for x in s.cks[j]]
        for t in range(j * s.ck, i): s.step(M, s.W['program'][t])
        return M
    def where(s, r, t):
        """chart of public r at original time t (between events: just before event t)"""
        for c, a, b in s.seg[r]:
            if a < t <= b: return c
        return None
    def segidx(s, r, X):
        return [k for k, (c, a, b) in enumerate(s.seg[r]) if c == X]
    def ops_at(s, r, lo, hi):
        L = s.ops[r]; i = bisect.bisect_right(L, lo); out = []
        while i < len(L) and L[i] < hi:
            out.append(L[i]); i += 1
        return out
    def lt(s, a, b): return (s.sp[a] & ~s.sp[b]) == 0 and s.sp[a] != s.sp[b]

def run_window(Wd, events, s0, vals, track_owned):
    """events: list of (key, ev, oi) sorted; replay from original state at s0. Returns (state, obs)."""
    M = Wd.state_at(s0); obs = {}; n = Wd.n
    for key, e, oi in events:
        if oi is not None and oi in track_owned:
            op = e[0]
            if op == 'CLEAR': obs[(oi, 'c')] = tuple(M[e[1]])
            elif op in ('ADD', 'COPY'):
                obs[(oi, 'd')] = tuple(M[e[1]]); obs[(oi, 's')] = tuple(M[e[2]])
            elif op == 'SCALE': obs[(oi, 'd')] = tuple(M[e[1]])
        Wd.step(M, e, vals)
    return M, obs

def owned_track(Wd, s0, e0):
    n = Wd.n; P = Wd.W['program']; out = set()
    for i in range(s0, e0):
        e = P[i]
        if e[0] in ('CLEAR',) or (e[0] in ('ADD', 'COPY') and (e[1] >= n or e[2] >= n)) or (e[0] == 'SCALE' and e[1] >= n):
            out.add(i)
    return out

def solve_mod(cols, rhs):
    """least-squares-free exact solve over GF(PM): find u with sum u_k cols[k] = rhs (all equations). None if inconsistent."""
    nv = len(cols); rows = []
    keys = set(rhs)
    for c in cols: keys |= set(c)
    for kk in keys:
        r = [c.get(kk, 0) % PM for c in cols] + [rhs.get(kk, 0) % PM]
        if any(r): rows.append(r)
    # gaussian elimination
    piv = []; R = rows; ri = 0
    for col in range(nv):
        p = None
        for j in range(ri, len(R)):
            if R[j][col]: p = j; break
        if p is None: continue
        R[ri], R[p] = R[p], R[ri]
        inv = pow(R[ri][col], -1, PM); R[ri] = [x * inv % PM for x in R[ri]]
        for j in range(len(R)):
            if j != ri and R[j][col]:
                f = R[j][col]; R[j] = [(x - f * y) % PM for x, y in zip(R[j], R[ri])]
        piv.append(col); ri += 1
        if ri == len(R): break
    for j in range(ri, len(R)):
        if R[j][nv]: return None
    u = [0] * nv
    for j, col in enumerate(piv): u[col] = R[j][nv]
    return u

def flat(M, obs, regs=None):
    d = {}
    for r in range(len(M)):
        for k in range(K):
            if M[r][k]: d[('s', r, k)] = M[r][k]
    for kk, v in obs.items():
        for k in range(K):
            if v[k]: d[('o',) + kk + (k,)] = v[k]
    return d

def diffd(a, b):
    out = {}
    for k in set(a) | set(b):
        v = (a.get(k, 0) - b.get(k, 0)) % PM
        if v: out[k] = v
    return out

class Cand:
    """new program = original with deletions (orig indices), replacements, insertions (key, ev)."""
    def __init__(s, Wd):
        s.Wd = Wd; s.dele = set(); s.ins = []; s.vars = []
    def add(s, key, ev): s.ins.append((key, list(ev)))
    def var(s, name): s.vars.append(name); return name
    def events(s, s0, e0):
        P = s.Wd.W['program']
        ev = [(float(i), P[i], i) for i in range(s0, e0) if i not in s.dele]
        ev += [(k, e, None) for k, e in s.ins]
        ev.sort(key=lambda x: x[0])
        return ev
    def window(s):
        ks = [k for k, e in s.ins] + list(s.dele)
        return max(0, int(math.floor(min(ks)))), min(s.Wd.T, int(math.floor(max(ks))) + 2)
    def solve(s, fixed=None):
        """returns dict var->Fraction or None"""
        s0, e0 = s.window(); Wd = s.Wd; tr = owned_track(Wd, s0, e0)
        tr -= s.dele
        orig = [(float(i), Wd.W['program'][i], i) for i in range(s0, e0)]
        Mt, ot = run_window(Wd, orig, s0, {}, tr); target = flat(Mt, ot)
        ev = s.events(s0, e0)
        vs = list(dict.fromkeys(s.vars))
        z = {v: 0 for v in vs}
        M0, o0 = run_window(Wd, ev, s0, z, tr); F0 = flat(M0, o0)
        rhs = diffd(target, F0)
        if not rhs: return {v: Q(0) for v in vs}
        cols = []
        for v in vs:
            z1 = dict(z); z1[v] = 1
            M1, o1 = run_window(Wd, ev, s0, z1, tr); cols.append(diffd(flat(M1, o1), F0))
        u = solve_mod(cols, rhs)
        if u is None: return None
        sol = {}
        for v, x in zip(vs, u):
            q = ratrec(x)
            if q is None: return None
            sol[v] = q
        # affine check
        vals = {v: qmod(str(q)) for v, q in sol.items()}
        M2, o2 = run_window(Wd, ev, s0, vals, tr)
        if diffd(flat(M2, o2), target): return None
        return sol
    def instantiate(s, sol):
        P = s.Wd.W['program']
        ev = [(float(i), list(P[i])) for i in range(len(P)) if i not in s.dele]
        for k, e in s.ins:
            e = list(e)
            if e[0] in ('ADD', 'COPY') and str(e[3]).startswith('$'):
                q = sol[e[3]]
                if q == 0: continue
                e[3] = str(q)
            ev.append((k, e))
        ev.sort(key=lambda x: x[0])
        # drop snapshot lifetimes that became empty (INIT, CLEAR only)
        W2 = dict(s.Wd.W); W2['program'] = prune_empty([e for k, e in ev])
        return W2

def prune_empty(P):
    idx = collections.defaultdict(list); st = {}
    for i, e in enumerate(P):
        if e[0] == 'INIT': st[e[1]] = [i]
        elif e[0] == 'CLEAR': st[e[1]].append(i); idx[e[1]].append(st.pop(e[1]))
        elif e[0] != 'MOVE':
            for r in ([e[1], e[2]] if e[0] in ('ADD', 'COPY') else [e[1]]):
                if r in st: st[r].append(i)
    drop = set()
    for o, L in idx.items():
        for ix in L:
            if len(ix) == 2: drop |= set(ix)
    return [e for i, e in enumerate(P) if i not in drop]

def free_label(Wd, lo, hi, used):
    """owned label not live in [lo,hi] (orig keys) and not already used by this candidate in an overlapping way"""
    n = Wd.n
    if max(Wd.prof[int(lo):int(hi) + 1] + [0]) + 1 + len(used) > 50: return None
    for o in range(n, n + Wd.NO):
        if o in used: continue
        if all(b < lo or a > hi for a, b in Wd.olive.get(o, [])): return o
    return None
