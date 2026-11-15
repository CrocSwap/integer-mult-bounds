"""walls.py -- exact toy checks for the t=-1 'walls' (Rank lemma / Clone, Lock Lemma / Theorem W, Commutation Theorem,
lift law, Zone lemma, Gram-lift Theorem M).  Standard library only; run as `python3 -I -B walls.py` from any cwd.
Ported from the lane toys under cards/WILD/{CLONEAUDIT,YCHAN,NEWMOVE,TOPLBUILD,MULTIHELP,GRAMLIFT} with their controls kept;
all arithmetic is exact (Fractions, ints mod a prime, F2 bitmasks); all randomness is seeded.
Every section asserts the lane claim and prints `ok ...` lines; the last line is PASS_WALL_TOYS iff every assertion held.
NOT ported (need data/libraries absent from stdlib): CLONEAUDIT ctrl7546 (word json + numpy), DECZERO (E8 104-port labelled
geometry from numpy/G104.npy), PARALLEL/KSLOT (scipy MILP), EARLYCAP (LEMMAA2 rhok), MULTIHELP p104.py (YYMIX data)."""
import itertools, random, sys, time, collections
from fractions import Fraction as Q
Fr = Q
T0 = time.time()
def ok(msg): print('ok', msg, flush=True)
def check(cond, msg):
    if not cond: raise AssertionError(msg)

# =====================================================================================================================
# 1. CLONEAUDIT: Rank lemma + Clone.  (Run/rank/kernel copied from CLONEAUDIT/toy.py)
# =====================================================================================================================
def span(basis):
    s = {0}
    for v in basis:
        if v not in s: s |= {x ^ v for x in s}
    return frozenset(s)

def rank(rows, ncols):
    M = [[r.get(j, Q(0)) for j in range(ncols)] for r in rows]
    rk = 0
    for c in range(ncols):
        p = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]
        for i in range(len(M)):
            if i != rk and M[i][c] != 0:
                f = M[i][c] / M[rk][c]; M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        rk += 1
    return rk

def kernel(rows, ncols):
    M = [[r.get(j, Q(0)) for j in range(ncols)] for r in rows]; piv = []; rk = 0
    for c in range(ncols):
        p = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[rk], M[p] = M[p], M[rk]; M[rk] = [a / M[rk][c] for a in M[rk]]
        for i in range(len(M)):
            if i != rk and M[i][c] != 0:
                f = M[i][c]; M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        piv.append(c); rk += 1
    out = []
    for fcol in [c for c in range(ncols) if c not in piv]:
        v = [Q(0)] * ncols; v[fcol] = Q(1)
        for i, c in enumerate(piv): v[c] = -M[i][fcol]
        out.append(v)
    return out

class Run:
    """Replay mirroring the verifier rules: public MOVE strictly ascending, owned MOVE strictly descending (flagged),
    ADD/COPY at a common frame, COPY into empty owned, CLEAR content NOT checked.  Tracks the full-state rank."""
    def __init__(s, names, init_frames):
        s.names = list(names); s.n = len(names); s.rows = [{i: Q(1)} for i in range(s.n)]
        s.cur = list(init_frames); s.owned = {}; s.bad = []; s.mass = 0; s.ownmove_up = 0; s.peak = 0; s.log = []
    def idx(s, r): return s.names.index(r) if isinstance(r, str) else r
    def state_rank(s):
        return rank(s.rows + [v[0] for v in s.owned.values()], s.n)
    def MOVE(s, r, b):
        if r in s.owned:
            a = s.owned[r][1]
            if not (span(b) < span(a)): s.ownmove_up += 1
            s.mass += abs(len(b) - len(a)); s.owned[r][1] = b
        else:
            i = s.idx(r)
            if not (span(s.cur[i]) < span(b)): s.bad.append(('public-move-not-ascending', r))
            s.cur[i] = b
    def fr(s, r): return s.owned[r][1] if r in s.owned else s.cur[s.idx(r)]
    def row(s, r): return s.owned[r][0] if r in s.owned else s.rows[s.idx(r)]
    def setrow(s, r, v):
        if r in s.owned: s.owned[r][0] = v
        else: s.rows[s.idx(r)] = v
    def INIT(s, o, f):
        s.owned[o] = [{}, f]; s.peak = max(s.peak, len(s.owned))
    def CLEAR(s, o, tag=''):
        before = s.state_rank(); dirty = bool(s.owned[o][0]); del s.owned[o]; after = s.state_rank()
        s.log.append((tag or o, dirty, before, after))
    def ADD(s, r, src, q=1, copy=False):
        if span(s.fr(r)) != span(s.fr(src)): s.bad.append(('add-frame', r, src))
        if copy and s.row(r): s.bad.append(('copy-nonzero', r))
        R = {} if copy else dict(s.row(r))
        for k, v in s.row(src).items():
            nv = R.get(k, 0) + Q(q) * v
            if nv: R[k] = nv
            else: R.pop(k, None)
        s.setrow(r, R)
    def SCALE(s, r, q): s.setrow(r, {k: v * Q(q) for k, v in s.row(r).items()})

h = 4; ports = range(4); q = [1 << r for r in ports]; sig = {0: 1, 1: 0, 2: 3, 3: 2}
ZERO = []; L = lambda r: [q[r]]; HYP = lambda r: [q[s] for s in ports if s != r]; V = [q[r] for r in ports]
cells = [(s, r) for r in ports for s in ports if s != r]

def build(mode, skip=None):
    names = ['X%d' % r for r in ports] + ['Y%d' % r for r in ports]
    inits = [L(r) for r in ports] + [ZERO for r in ports]
    if mode == 'real': names += ['h%d%d' % c for c in cells]; inits += [ZERO for c in cells]
    R = Run(names, inits); x = lambda r: r; y = lambda r: 4 + r
    for a, b in [(0, 1), (2, 3)]:
        A, B_ = 'Y%d' % a, 'Y%d' % b
        R.ADD(A, B_); R.ADD(B_, A, -1); R.ADD(A, B_); R.SCALE(A, -1)
    for (s, r) in cells:
        c = 'h%d%d' % (s, r) if mode == 'real' else 'O%d%d' % (s, r)
        if mode == 'real': R.MOVE(c, L(s)); R.ADD(c, 'X%d' % s)
        else: R.INIT(c, L(s)); R.ADD(c, 'X%d' % s, copy=True)
    for r in ports:
        Y = 'Y%d' % r; R.MOVE(Y, L(sig[r])); R.ADD('X%d' % sig[r], Y)
        R.INIT('S', L(sig[r])); R.ADD('S', Y, copy=True); R.ADD(Y, 'S', -1); R.CLEAR('S', 'snapshot Y%d' % r)
    for r in ports:
        Y = 'Y%d' % r; R.MOVE(Y, HYP(r))
        for s in ports:
            if s == r or (s, r) == skip: continue
            c = 'h%d%d' % (s, r) if mode == 'real' else 'O%d%d' % (s, r)
            R.MOVE(c, HYP(r)); R.ADD(Y, c)
            if mode != 'real': R.CLEAR(c, 'carrier O%d%d' % (s, r))
    if skip and mode != 'real':
        c = 'O%d%d' % skip; R.MOVE(c, HYP(skip[1])); R.CLEAR(c, 'carrier O%d%d(skipped)' % skip)
    for r in ports: R.MOVE('X%d' % r, V)
    tgt = {}
    for r in ports:
        tgt['X%d' % r] = {x(r): Q(1), y(r): Q(-1)}
        tgt['Y%d' % r] = {x(s): Q(1) for s in ports if s != r}
    if mode == 'real':
        for i, nm in enumerate(R.names):
            if nm[0] == 'h': tgt[nm] = {i: Q(1)}
    wrong = [nm for nm in R.names if R.rows[R.idx(nm)] != tgt[nm]]
    return R, wrong, rank(R.rows, R.n)

def section_cloneaudit():
    t = time.time()
    # A4 toy, token-free carriers (cell model): exact, invertible, no rank-lowering CLEAR
    R, w, fr = build('cell')
    check(w == [] and fr == R.n == 8 and not R.bad and R.ownmove_up == 12 and R.mass == 24 and R.peak == 13, 'cell model')
    check(len(R.log) == 16 and all(a >= b for _, _, b, a in R.log) and all(b == a for _, _, b, a in R.log), 'cell CLEARs rank-neutral')
    ok('CLONEAUDIT cell model (token-free owned carriers): n_pub 8, finals exact, final rank 8/8, 16 dirty CLEARs all rank-neutral, 12 owned ascents (verifier-illegal: owned must descend), mass 24, peak owned 13')
    # negative control: carrier undelivered
    R, w, fr = build('cell', skip=(1, 0))
    check(w == ['Y0'], 'undelivered carrier must be flagged')
    ok('CLONEAUDIT NEG control: one carrier undelivered -> finals wrong [Y0] (flagged)')
    # real tokens: rank drops 20 -> 19 -> 18 -> 17 -> 16, final map singular 16/20
    R, w, fr = build('real')
    drops = [(tg, b, a) for tg, d, b, a in R.log if a < b]
    check(R.n == 20 and not R.bad and R.ownmove_up == 0, 'real legality')
    check([(b, a) for _, b, a in drops] == [(20, 19), (19, 18), (18, 17), (17, 16)], 'rank drops %s' % drops)
    check(fr == 16 and len(w) == 16 and all(nm[0] in 'Yh' for nm in w), 'final map singular 16/20')
    K = kernel(R.rows, R.n); check(len(K) == 4, 'kernel dim')
    expect = {frozenset([('X%d' % r, -1), ('Y%d' % r, -1)] + [('h%d%d' % (r, s), 1) for s in ports if s != r]) for r in ports}
    got = {frozenset((R.names[i], int(c)) for i, c in enumerate(v) if c) for v in K}
    check(got == expect, 'kernel per pair mismatch %s' % got)
    ok('CLONEAUDIT REAL tokens (public helper carriers): 4 snapshot CLEARs lower state rank 20->19->18->17->16, final map SINGULAR 16/20; kernel = {X_r=-1,Y_r=-1,3 carriers reading X_r=+1} per r; all 4 Y and 12 helpers end wrong; 0 illegal events')
    # positive controls
    P = Run(['X1', 'Y0'], [L(1), ZERO]); P.MOVE('Y0', L(1)); P.INIT('S', L(1)); P.ADD('S', 'X1', copy=True)
    P.ADD('X1', 'Y0'); P.CLEAR('S', 'snapshot X1')
    check(P.log[0][1] and P.log[0][2] == P.log[0][3] == 2, 'pos ctrl 1')
    P = Run(['X1', 'Y0'], [L(1), ZERO]); P.MOVE('Y0', L(1)); P.INIT('S', L(1)); P.ADD('S', 'X1', copy=True); P.CLEAR('S', 'copy, no change')
    check(P.log[0][1] and P.log[0][2] == P.log[0][3], 'pos ctrl 2')
    ok('CLONEAUDIT POS controls: dirty CLEAR of a copy of a still-held register is rank-neutral (2->2, two variants)')
    P = Run(['X1', 'Y0'], [L(1), ZERO]); P.MOVE('Y0', L(1)); P.ADD('X1', 'Y0'); P.ADD('Y0', 'X1', -1)
    check(P.state_rank() == 2 and not P.bad and P.rows == [{0: Q(1), 1: Q(1)}, {0: Q(-1)}], 'public swap')
    ok('CLONEAUDIT POS control: public swap at the line (X,Y)=(x,m)->(x+m,-x) is invertible (rank 2/2), no illegal event')
    ok('CLONEAUDIT toy %.1fs' % (time.time() - t))

def section_rank_lemma_random(seed=20261114, programs=250, events=45):
    """Random legal programs: full-state rank never increases; dirty CLEAR lossless iff content in span of the rest;
    any rank-lowering CLEAR is permanent (final public rank <= min over time of state rank)."""
    t = time.time(); rng = random.Random(seed)
    lev = [[], [1], [1, 2], [1, 2, 4]]            # chain of frames, level k = k-dim; public move up, owned move down
    nlow = nlossless_dirty = nclears = nmono = 0; cap_ok = 0
    for _ in range(programs):
        npub = rng.randint(3, 5); levels = [rng.randint(0, 2) for _ in range(npub)]
        R = Run(['P%d' % i for i in range(npub)], [lev[l] for l in levels]); lv = {i: levels[i] for i in range(npub)}
        olv = {}; mn = R.state_rank(); prev = mn; nown = 0
        check(prev == npub, 'initial rank')
        for _ in range(events):
            kind = rng.choice(['INIT', 'ADD', 'ADD', 'ADD', 'COPY', 'SCALE', 'CLEAR', 'CLEAR', 'MOVE', 'PARK'])
            names = list(range(npub)) + list(olv)
            if kind == 'INIT' and len(olv) < 3:
                nm = 'O%d' % nown; nown += 1; l = rng.randint(0, 3); R.INIT(nm, lev[l]); olv[nm] = l
            elif kind in ('ADD', 'COPY'):
                same = [(a, b) for a in names for b in names if a != b and (lv.get(a, olv.get(a)) == lv.get(b, olv.get(b)))]
                if not same: continue
                a, b = rng.choice(same)
                if kind == 'COPY':
                    if a in olv or a < npub and False: pass
                    if isinstance(a, str):          # COPY into an (already) live owned row only if it is empty; use fresh owned instead
                        if R.owned[a][0]: R.ADD(a, b, rng.choice([-2, -1, 1, 2]))
                        else: R.ADD(a, b, 1, copy=True)
                    else: R.ADD(a, b, rng.choice([-2, -1, 1, 2]))
                else: R.ADD(a, b, rng.choice([-2, -1, 1, 2]))
            elif kind == 'PARK' and len(olv) < 3:      # park a public content in a fresh owned row and zero the public register
                a = rng.randrange(npub); nm = 'O%d' % nown; nown += 1; l = lv[a]
                R.INIT(nm, lev[l]); olv[nm] = l; R.ADD(nm, a, 1, copy=True); R.ADD(a, nm, -1)
            elif kind == 'SCALE' and names:
                R.SCALE(rng.choice(names), rng.choice([-2, -1, 2, 3]))
            elif kind == 'CLEAR' and olv:
                nm = rng.choice(list(olv)); content = R.owned[nm][0]
                rest = [r for r in R.rows] + [v[0] for k, v in R.owned.items() if k != nm]
                before = R.state_rank(); rest_rank = rank(rest, npub)
                in_span = (rank(rest + [content], npub) == rest_rank)
                R.CLEAR(nm); del olv[nm]; after = R.state_rank(); nclears += 1
                check((after == before) == in_span, 'dirty CLEAR lossless iff content in span of the rest')
                if not content: check(after == before, 'clean CLEAR must be neutral')
                if after < before: nlow += 1
                elif content: nlossless_dirty += 1
            elif kind == 'MOVE':
                cand = [i for i in range(npub) if lv[i] < 3]
                if cand and rng.random() < 0.5:
                    i = rng.choice(cand); nl = rng.randint(lv[i] + 1, 3); R.MOVE(i, lev[nl]); lv[i] = nl
                elif olv:
                    nm = rng.choice(list(olv))
                    if olv[nm] > 0:
                        nl = rng.randint(0, olv[nm] - 1); R.MOVE(nm, lev[nl]); olv[nm] = nl
            r = R.state_rank()
            check(r <= prev, 'Rank lemma violated: state rank rose %d -> %d' % (prev, r)); nmono += 1
            mn = min(mn, r); prev = r
        for nm in list(olv): R.CLEAR(nm); del olv[nm]
        fin = rank(R.rows, npub)
        check(fin <= mn, 'rank-lowering CLEAR not permanent'); cap_ok += 1
        check(R.ownmove_up == 0 and not R.bad, 'generator produced an illegal event: %s' % R.bad)
    check(nlow >= 20 and nlossless_dirty >= 20, 'control coverage: both rank-lowering (%d) and lossless dirty (%d) CLEARs must occur' % (nlow, nlossless_dirty))
    ok('RANK LEMMA random legal programs: %d programs, %d events, state rank never increased (0 violations); %d CLEARs: %d rank-lowering, %d dirty-but-lossless; dirty CLEAR lossless iff content in span(rest) (0 violations); final public rank <= min state rank in %d/%d programs; 0 illegal events (%.1fs)' % (programs, nmono, nclears, nlow, nlossless_dirty, cap_ok, programs, time.time() - t))

# =====================================================================================================================
# 2. YCHAN: Lock Lemma / Theorem W toy table (copied from YCHAN/toy.py; nh=3 rows skipped for time)
# =====================================================================================================================
def rank_y(rows):
    R = [list(r) for r in rows if any(r)]; rk = 0; nc = len(R[0]) if R else 0
    for c in range(nc):
        p = next((i for i in range(rk, len(R)) if R[i][c]), None)
        if p is None: continue
        R[rk], R[p] = R[p], R[rk]; pv = R[rk][c]
        for i in range(len(R)):
            if i != rk and R[i][c]:
                f = R[i][c] / pv; R[i] = [a - f * b for a, b in zip(R[i], R[rk])]
        rk += 1
    return rk

def ychan_run(n, nh, target, rng, kasc=0, retime=False):
    S = {}
    for t in range(n):
        for s in 'xyab': S[s + str(t)] = len(S)
    for j in range(nh): S['h%d' % j] = len(S)
    N = len(S); e = lambda k: [Fr(int(i == S[k])) for i in range(N)]
    add = lambda u, v, c=1: [a + c * b for a, b in zip(u, v)]
    zeroes = [Fr(0)] * N
    V0 = ['y%d' % t for t in range(n)] + ['b%d' % t for t in range(n)] + ['h%d' % j for j in range(nh)]
    Zregs = ['Y%d' % t for t in range(n)] + ['Y2_%d' % t for t in range(n)] + ['H%d' % j for j in range(nh)]
    def rvec():
        v = zeroes[:]
        for s in V0:
            if rng.random() < 0.35: v = add(v, e(s), rng.choice([-1, 1, 2]))
        return v
    C = {}
    for i, R in enumerate(Zregs):
        C[R] = rvec() if rng.random() < 0.85 else e(V0[i])
    route = {j: rng.choice([('L', rng.randrange(n)), ('P', rng.randrange(n)), 'V']) for j in range(nh)}
    if retime:
        for j in range(nh):
            if route[j][0] == 'L' and rng.random() < 0.8:
                t = route[j][1]; cY = C['Y%d' % t]; cH = C['H%d' % j]
                lam = rng.choice([-1, 1]); mu = rng.choice([-1, 0, 1])
                C['H%d' % j] = add(cH, cY, lam)
                C['Y%d' % t] = add(cY, cH, mu) if rng.random() < 0.5 else add(cY, C['H%d' % j], mu)
    X = {}; X2 = {}
    for t in range(n):
        up = [C['H%d' % j] for j in route if route[j] == ('L', t)]
        x = e('x%d' % t); a = e('a%d' % t)
        for v in up:
            if rng.random() < 0.7: x = add(x, v, rng.choice([-1, 1]))
            if rng.random() < 0.5: a = add(a, v, rng.choice([-1, 1]))
        X[t] = x; X2[t] = a
    Yp = {t: add(C['Y%d' % t], X[t]) for t in range(n)}
    X2p = {t: add(X2[t], C['Y2_%d' % t], -1) for t in range(n)}
    D = 0; SV = []; PQ = []
    for t in range(n):
        Pq = [Yp[t], C['Y2_%d' % t]] + [C['H%d' % j] for j in route if route[j] == ('P', t)]
        tgt = e('x%d' % t) if target == 'LU' else add(e('x%d' % t), e('y%d' % t))
        if rank_y(Pq + [tgt]) > rank_y(Pq): D += 1
        PQ.append(Pq)
        SV += [X[t], X2p[t]]
    SV += [C['H%d' % j] for j in route if route[j] == 'V' or route[j][0] == 'L']
    for _ in range(kasc): SV.append(rvec())
    TV = []
    for t in range(n):
        TV.append(add(e('x%d' % t), e('y%d' % t), -1) if target == 'LU' else [-c for c in e('y%d' % t)])
        TV += [e('a%d' % t), e('b%d' % t)]
    TV += [e('h%d' % j) for j in range(nh)]
    for Pq in PQ:
        m = len(Pq) - 1
        for _ in range(m):
            base = rank_y(SV); best = None
            for co in itertools.product([-2, -1, 0, 1, 2], repeat=len(Pq)):
                if not any(co): continue
                v = [sum(c * P[i] for c, P in zip(co, Pq)) for i in range(len(Pq[0]))]
                if rank_y(SV + [v]) > base and rank_y(SV + TV + [v]) == rank_y(SV + TV): best = v; break
            if best is None: break
            SV.append(best)
    D += rank_y(SV + TV) - rank_y(SV)
    return D

def section_ychan(nit=1500):
    t = time.time(); rng = random.Random(1)
    table = {}
    for n, nh in [(1, 1), (1, 2), (2, 2)]:
        for target in ['LU', 'UL']:
            for kasc, rt in [(0, False), (n, False), (0, True)]:
                res = [ychan_run(n, nh, target, rng, kasc=kasc, retime=rt) for _ in range(nit)]
                table[(n, nh, target, kasc, rt)] = (min(res), sorted(collections.Counter(res).items())[:4])
    exp = {  # lane toy.out (seed 1, 1500 samples) for the rows ported here
        (1, 1, 'LU', 0, False): (1, [(1, 252), (2, 1013), (3, 235)]), (1, 1, 'LU', 1, False): (0, [(0, 94), (1, 689), (2, 623), (3, 94)]),
        (1, 1, 'UL', 0, False): (1, [(1, 317), (2, 843), (3, 317), (4, 23)]), (1, 1, 'UL', 1, False): (0, [(0, 124), (1, 612), (2, 630), (3, 129)]),
        (2, 2, 'LU', 0, False): (2, [(2, 9), (3, 165), (4, 1180), (5, 144)]), (2, 2, 'LU', 2, False): (0, [(0, 1), (1, 97), (2, 769), (3, 581)]),
        (2, 2, 'UL', 0, False): (2, [(2, 18), (3, 319), (4, 1008), (5, 151)]), (2, 2, 'UL', 2, False): (0, [(0, 12), (1, 195), (2, 734), (3, 504)]),
        (2, 2, 'LU', 0, True): (2, [(2, 6), (3, 196), (4, 1177), (5, 117)]), (2, 2, 'UL', 0, True): (2, [(2, 25), (3, 310), (4, 1033), (5, 130)]),
    }
    for k, v in exp.items():
        check(table[k][0] == v[0], 'min D %s: got %s lane %s' % (k, table[k][0], v[0]))
    # Theorem W: free wiring (no owned ascent) forces D >= n for every sample, for every row; n ascents reach D=0
    for (n, nh, target, kasc, rt), (mn, _) in table.items():
        if kasc == 0: check(mn >= n and mn == n, 'free wiring min D must equal n: %s %d' % ((n, nh, target, rt), mn))
        elif n == kasc and not rt: check(mn == 0, 'n owned ascents must give D=0: %s' % ((n, nh, target),))
    ok('YCHAN Lock/Theorem W: free wiring (LU and UL, incl. re-timed L) min D = 1 at n=1 and 2 at n=2 (nh 1,2); +n owned ascents (positive control) min D = 0; (%d samples/row, seed 1; the lane own toy.py rerun today gives a slightly different histogram than its stored toy.out, e.g. n=1 nh=1 LU hist (1,266),(2,986),(3,248) vs stored (1,252),(2,1013),(3,235); minima are stable; nh=3 rows not ported) (%.1fs)' % (nit, time.time() - t))

# =====================================================================================================================
# 3. NEWMOVE: Commutation Theorem (copied from NEWMOVE/toy.py; same seed 7 and call order -> same counts)
# =====================================================================================================================
P31 = 2 ** 31 - 1
def rank_p(M):
    M = [r[:] for r in M]; rk = 0; cols = len(M[0]) if M else 0
    for c in range(cols):
        piv = next((i for i in range(rk, len(M)) if M[i][c] % P31), None)
        if piv is None: continue
        M[rk], M[piv] = M[piv], M[rk]; inv = pow(M[rk][c], P31 - 2, P31)
        M[rk] = [x * inv % P31 for x in M[rk]]
        for i in range(len(M)):
            if i != rk and M[i][c] % P31:
                f = M[i][c]; M[i] = [(a - f * b) % P31 for a, b in zip(M[i], M[rk])]
        rk += 1
    return rk
def matmul_p(A, B):
    return [[sum(a * b for a, b in zip(r, col)) % P31 for col in zip(*B)] for r in A]

def newmove_t1(R, trials=300, k=2, control=False):
    viol = 0
    for _ in range(trials):
        n = 7; frames = [(), (1,), (1, 2), (1, 2, 3), (2,), (2, 3)]
        sub = lambda a, b: set(a) < set(b)
        lab = [() if r < 3 else R.choice(frames[1:]) for r in range(n)]
        N = n * k
        C = [[[1 if c == r * k + i else 0 for c in range(N)] for i in range(k)] for r in range(n)]
        V0 = [c for r in range(3) for c in range(r * k, r * k + k)]
        dep = []; did_cross = False
        for step in range(40):
            if R.random() < 0.35:
                r = R.randrange(n); ups = [f for f in frames if sub(lab[r], f)]
                if ups:
                    if lab[r] == (): dep += [[row[c] for c in V0] for row in C[r]]
                    lab[r] = R.choice(ups)
            else:
                f = R.choice(frames); grp = [r for r in range(n) if lab[r] == f]
                if control and not did_cross and f != () and any(lab[r] == () for r in range(3)):
                    src = next(r for r in range(3) if lab[r] == ()); grp = grp + [src]; did_cross = True
                if len(grp) < 1: continue
                A = [[R.randrange(P31) for _ in range(k * len(grp))] for _ in range(k * len(grp))]
                stack = [row for r in grp for row in C[r]]
                new = matmul_p(A, stack)
                for j, r in enumerate(grp): C[r] = new[j * k:(j + 1) * k]
        outside = [[row[c] for c in V0] for r in range(n) if lab[r] != () for row in C[r]]
        if outside and rank_p(dep + outside) > rank_p(dep) if dep else (outside and rank_p(outside) > 0):
            viol += 1
    return viol

def mat_inv2(G):
    n = len(G); M = [r[:] + [int(i == j) for j in range(n)] for i, r in enumerate(G)]
    for c in range(n):
        piv = next(i for i in range(c, n) if M[i][c]); M[c], M[piv] = M[piv], M[c]
        for i in range(n):
            if i != c and M[i][c]: M[i] = [a ^ b for a, b in zip(M[i], M[c])]
    return [r[n:] for r in M]
def mv(M, v): return tuple(sum(M[i][j] * v[j] for j in range(len(v))) % 2 for i in range(len(M)))
def transpose(M): return [list(r) for r in zip(*M)]
def dot2(a, b): return sum(x * y for x, y in zip(a, b)) % 2

def section_newmove():
    t = time.time(); R = random.Random(7)
    v0 = newmove_t1(R); v1 = newmove_t1(R, control=True)
    check(v0 == 0, 'Lock violations with arbitrary local maps: %d' % v0)
    check(v1 > 0, 'control must bite')
    msg = 'NEWMOVE T1 Commutation Theorem: arbitrary frame-local 2x2 field maps %d/300 Lock violations; one cross-label op control %d/300' % (v0, v1)
    ok(msg + (' (identical to lane: 0/300, 47/300)' if (v0, v1) == (0, 47) else ' (lane reported 47/300 for the control; qualitative control reproduced, counts differ)'))
    h = 3; vecs = list(itertools.product((0, 1), repeat=h))
    def subspaces():
        seen = set()
        for k in range(h + 1):
            for gens in itertools.combinations(vecs, k):
                S = {tuple([0] * h)}
                for g in gens: S |= {tuple((a + b) % 2 for a, b in zip(s, g)) for s in S}
                seen.add(frozenset(S))
        return seen
    def LU(U):
        perp = [v for v in vecs if all(dot2(v, u) == 0 for u in U)]
        return frozenset(u + tuple((a + b) % 2 for a, b in zip(u, w)) for u in U for w in perp)
    def KG(G):
        Gi = mat_inv2(G); GiT = transpose(Gi)
        return lambda x: mv(G, x[:h]) + tuple((a + b) % 2 for a, b in zip(mv([[(G[i][j] + GiT[i][j]) % 2 for j in range(h)] for i in range(h)], x[:h]), mv(GiT, x[h:])))
    L0 = frozenset(tuple([0] * h) + v for v in vecs); LF = frozenset(v + v for v in vecs)
    def dist(Lx, Mx): import math; return h - int(math.log2(len(Lx & Mx)))
    ok_fix = ok_map = 0; maxd = 0; nG = 0; subs = subspaces()
    for _ in range(200):
        G = [[R.randrange(2) for _ in range(h)] for _ in range(h)]
        try: mat_inv2(G)
        except StopIteration: continue
        nG += 1; K = KG(G)
        ok_fix += (frozenset(map(K, L0)) == L0 and frozenset(map(K, LF)) == LF)
        for U in subs:
            GU = frozenset(mv(G, u) for u in U)
            ok_map += frozenset(map(K, LU(U))) == LU(GU)
            maxd = max(maxd, dist(LU(U), LU(GU)))
    check(ok_fix == nG and ok_map == nG * len(subs) and maxd > 0, 'T2 global rotation')
    ok('NEWMOVE T2 chart rotation (h=3, F2): K_G fixes L0 and LF %d/%d; K_G L_U = L_GU %d/%d; max d(L_U,L_GU)=%d>0 (relabel reading is a real transition) (%.1fs)' % (ok_fix, nG, ok_map, nG * len(subs), maxd, time.time() - t))

# =====================================================================================================================
# 4. TOPLBUILD g1toy: lift law (WILDPAIR wp.run + GLIFT geometry/unit_flag inlined)
# =====================================================================================================================
def perpF(F, N):
    return frozenset(c for c in range(1 << N) if all(not dot(c, v) for v in F))
def dot(a, b): return bin(a & b).count('1') & 1
def fdim(F): return len(F).bit_length() - 1
def basis(F):
    b = []
    for v in sorted(F):
        w = v
        for x in b: w = min(w, w ^ x)
        if w: b.append(w)
    return b
def wp_run(W):
    N = W['N']; R = W['regs']; fr = {}; row = {}; own = set(); bad = []; units = 0; asc = 0; dirty = 0
    for r, d in R.items(): fr[r] = span(d['f0']); row[r] = {r: Fr(1)}
    for i, op in enumerate(W['program']):
        k, r = op[0], op[1]
        alive = r in R or r in own
        if k == 'MOVE':
            F = span(op[2])
            if not alive: bad.append((i, 'move-dead', r)); continue
            A = fr[r]
            if r in R:
                if not (A < F): bad.append((i, 'public-not-ascending', r))
            else:
                if not (A <= F or F <= A): bad.append((i, 'owned-nonnested', r))
                units += abs(fdim(F) - fdim(A)); asc += fdim(F) > fdim(A)
            fr[r] = F
        elif k in ('ADD', 'COPY'):
            s = op[3] if k == 'ADD' else op[2]; c = Fr(op[2]) if k == 'ADD' else Fr(1)
            if not (s in R or s in own): bad.append((i, 'src-dead', s)); continue
            if k == 'COPY':
                if r in R or r in own: bad.append((i, 'copy-into-live', r)); continue
                own.add(r); fr[r] = fr[s]; row[r] = {}
            elif not alive: bad.append((i, 'add-dead', r)); continue
            if fr[r] != fr[s]: bad.append((i, 'frame', r, s))
            if r == s: bad.append((i, 'self-add')); continue
            d = row[r]
            for a, v in row[s].items():
                nv = d.get(a, 0) + c * v
                if nv: d[a] = nv
                else: d.pop(a, None)
        elif k == 'SCALE':
            if not alive or Fr(op[2]) == 0: bad.append((i, 'scale', r)); continue
            row[r] = {a: v * Fr(op[2]) for a, v in row[r].items()}
        elif k == 'INIT':
            if alive: bad.append((i, 'init-live', r)); continue
            own.add(r); fr[r] = span(op[2]); row[r] = {}
        elif k == 'CLEAR':
            if r not in own: bad.append((i, 'clear-nonowned', r)); continue
            dirty += bool(row[r]); own.discard(r); del fr[r]; del row[r]
    if own: bad.append(('owned-alive', sorted(own)))
    for r, d in R.items():
        if fr[r] != span(d['f1']): bad.append(('final-frame', r))
    return dict(bad=bad, rows={r: row[r] for r in R}, frames={r: fr[r] for r in R}, units=units, ascents=asc, dirty=dirty)

def geometry(m):
    """A_m lines: ports q_ij = e_i + e_j + e_{m+1} in GF(2)^(m+2); roots v_ij = e_i - e_j (Gram G)."""
    N = m + 2; pairs = list(itertools.combinations(range(m + 1), 2))
    prts = [(1 << i) | (1 << j) | (1 << (m + 1)) for i, j in pairs]
    roots = [[(1 if k == i else -1 if k == j else 0) for k in range(m + 1)] for i, j in pairs]
    n = len(prts)
    G = [[sum(a * b for a, b in zip(roots[s], roots[t])) for t in range(n)] for s in range(n)]
    B = [[Fr(r[k]) for k in range(m)] for r in roots]
    IJ = [[Fr(1 + (a == b)) for b in range(m)] for a in range(m)]
    C = [[sum(B[t][a] * IJ[a][j] for a in range(m)) / 2 for j in range(m)] for t in range(n)]
    for s in range(n):
        for t in range(n):
            assert sum(C[s][j] * B[t][j] for j in range(m)) == Fr(G[s][t], 2)
            assert (G[s][t] % 2 == 1) == (s != t and dot(prts[s], prts[t]) == 0), 'partner <=> G odd'
    Z = {(s, t): Fr(G[s][t], 2) for s in range(n) for t in range(n) if s != t and G[s][t]}
    return N, prts, G, B, C, Z

def unit_flag(start, top, rng):
    ch = [start]; cur = start
    while fdim(cur) < fdim(top):
        cand = [v for v in top if v not in cur]
        v = rng.choice(cand); cur = frozenset(cur | {x ^ v for x in cur}); ch.append(cur)
    assert ch[-1] == top
    return ch

def lsolve(cols, rhs):
    syms = sorted({k for v in cols for k in v} | set(rhs)); n = len(cols)
    A = [[Fr(v.get(s, 0)) for v in cols] + [Fr(rhs.get(s, 0))] for s in syms]; piv = []; r0 = 0
    for c in range(n):
        p = next((i for i in range(r0, len(A)) if A[i][c]), None)
        if p is None: continue
        A[r0], A[p] = A[p], A[r0]; iv = 1 / A[r0][c]; A[r0] = [x * iv for x in A[r0]]
        for i in range(len(A)):
            if i != r0 and A[i][c]: f = A[i][c]; A[i] = [x - f * y for x, y in zip(A[i], A[r0])]
        piv.append(c); r0 += 1
    if any(A[i][-1] for i in range(r0, len(A))): return None
    sol = [Fr(0)] * n
    for i, c in enumerate(piv): sol[c] = A[i][-1]
    return sol

def rank_d(vecs):
    syms = sorted({k for v in vecs for k in v}); M = [[Fr(v.get(s, 0)) for s in syms] for v in vecs]; r = 0
    for c in range(len(syms)):
        p = next((i for i in range(r, len(M)) if M[i][c]), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        for i in range(len(M)):
            if i != r and M[i][c]: f = M[i][c] / M[r][c]; M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        r += 1
    return r

def g1_build(m, t, variant, rng, k1=None, k2=None):
    N, prts, G, B, C, Z = geometry(m); n = len(prts)
    Vf = span([1 << i for i in range(N)]); Z0 = frozenset({0}); hyp = [perpF(span([qq]), N) for qq in prts]
    cand = [u for u in range(n) if u != t and dot(prts[u], prts[t]) == 0]
    c = rng.choice(cand)
    chain = unit_flag(span([prts[c]]), hyp[t], rng)
    regs = {}
    X = ['X%d' % u for u in range(n)]
    for u in range(n): regs[X[u]] = dict(kind='X', f0=basis(span([prts[u]])), f1=basis(Vf))
    Y, A, H = 'Y%d' % t, 'A%d' % t, 'H%d' % t
    Bp = 'B%d' % t
    if variant == 'pln_B': regs[Bp] = dict(kind='H', f0=[], f1=basis(Vf))
    regs[Y] = dict(kind='Y', f0=[], f1=basis(hyp[t])); regs[A] = dict(kind='H', f0=[], f1=basis(Vf)); regs[H] = dict(kind='H', f0=[], f1=basis(Vf))
    P = []; M = lambda r, F: P.append(('MOVE', r, basis(F))); Ad = lambda d, k, s: P.append(('ADD', d, Fr(k), s)) if k else None
    k1 = Fr(rng.choice([-2, -1, 1, 2, 3])) if k1 is None else Fr(k1); k2 = Fr(rng.choice([-1, 0, 1, 2])) if k2 is None else Fr(k2)
    O, O2, Pz = 'O%d' % t, 'Q%d' % t, 'P%d' % t
    if variant != 'ctrl_zr':
        P.append(('INIT', O, basis(span([prts[t]])))); Ad(O, 1, X[t]); M(O, Z0)
        Ad(A, -1, H)
        Ad(O, 1, H)
    if variant == 'ctrl_m1':
        P.append(('INIT', O2, basis(span([prts[t]])))); Ad(O2, 1, X[t]); M(O2, Vf); M(O2, hyp[t])
    if variant == 'ctrl_zr':
        Fq = span([prts[t], prts[c]])
        P.append(('INIT', Pz, basis(span([prts[c]])))); Ad(Pz, 1, X[c]); M(Pz, Fq)
        M(X[t], Fq); Ad(X[t], 1, Pz); P.append(('CLEAR', Pz))
        P.append(('INIT', O, basis(Fq))); Ad(O, 1, X[t]); M(O, span([prts[c]]))
        Ad(X[c], -1, O); P.append(('CLEAR', O))
    if variant in ('pln_lo', 'ctrl_m1', 'pln_B'):
        Ad(A, 1, O); P.append(('CLEAR', O))
    if variant == 'ctrl_t0':
        Ad(Y, 1, O); Ad(Y, -1, H); P.append(('CLEAR', O)); Ad(A, 1, H)
    M(H, Vf)
    if variant != 'ctrl_t0':
        M(A, chain[0])
        if variant in ('pln_lo', 'pln_hi'):
            Ad(X[c], k1, A); Ad(A, k2, X[c])
        if variant == 'pln_B':
            M(Bp, chain[0]); Ad(Bp, 1, A); Ad(Bp, -k1, X[c]); Ad(X[c], k2 or 1, Bp)
        if variant == 'pln_hi':
            M(O, chain[0]); Ad(A, 1, O); P.append(('CLEAR', O))
    M(Y, chain[0])
    for F in chain[1:]:
        for r in ([A, X[c]] if variant != 'ctrl_t0' else [X[c]]) + ([Bp] if variant == 'pln_B' else []) + [Y]: M(r, F)
    st = wp_run(dict(N=N, regs=regs, program=P + [('CLEAR', O2)] if variant == 'ctrl_m1' else P))
    rows = st['rows']; info = {}
    names = list(regs); zc = lsolve([rows[r] for r in names], {X[t]: Fr(1)})
    info['z_support'] = sorted(r for r, v in zip(names, zc or []) if v) if zc else 'singular'
    if variant in ('pln_lo', 'pln_hi', 'ctrl_zr', 'pln_B'):
        present = [A, X[c]] + ([Bp] if variant == 'pln_B' else [])
        sol = lsolve([rows[r] for r in present], {X[t]: Fr(1)})
        info['top_solvable'] = sol is not None
        if sol:
            for r, k in zip(present, sol): Ad(Y, k, r)
    if variant == 'ctrl_m1':
        Ad(Y, 1, A); Ad(A, -1, O2); Ad(Y, -1, A); P.append(('CLEAR', O2))
    for u in range(n):
        if u != c and not (variant == 'ctrl_zr' and u == t):
            for F in unit_flag(span([prts[u]]), Vf, rng)[1:]: M(X[u], F)
    if variant == 'ctrl_zr':
        for F in unit_flag(span([prts[t], prts[c]]), Vf, rng)[1:]: M(X[t], F)
    for r in ([A, X[c]] if variant != 'ctrl_t0' else [X[c], A]) + ([Bp] if variant == 'pln_B' else []): M(r, Vf)
    W = dict(N=N, regs=regs, program=P)
    st = wp_run(W); rows = st['rows']
    Vr = [r for r in regs if st['frames'][r] == Vf]
    Tg = {r: {r: Fr(1)} for r in Vr}
    def_rank = len(Vr) - rank_d([rows[r] for r in Vr])
    yok = rows[Y] == {Y: Fr(1), X[t]: Fr(1)}
    if def_rank == 0:
        coef = {r: lsolve([Tg[s] for s in Vr], rows[r]) for r in Vr}
        Mx = [coef[r][:] for r in Vr]; nv = len(Vr)
        for col in range(nv):
            if Mx[col][col] == 0:
                piv = next(i for i in range(col + 1, nv) if Mx[i][col])
                P.append(('ADD', Vr[col], Fr(1), Vr[piv])); Mx[col] = [a + b for a, b in zip(Mx[col], Mx[piv])]
            if Mx[col][col] != 1:
                s_ = 1 / Mx[col][col]; P.append(('SCALE', Vr[col], s_)); Mx[col] = [a * s_ for a in Mx[col]]
            for i in range(nv):
                if i != col and Mx[i][col]:
                    f_ = Mx[i][col]; P.append(('ADD', Vr[i], -f_, Vr[col])); Mx[i] = [a - f_ * b for a, b in zip(Mx[i], Mx[col])]
        st = wp_run(W); rows = st['rows']
        exact = all(rows[r] == Tg[r] for r in Vr) and rows[Y] == {Y: Fr(1), X[t]: Fr(1)}
    else:
        exact = False
    info.update(D=def_rank + (0 if yok else 1), def_rank=def_rank, Y_ok=yok, legal=(st['bad'] == []), bad=st['bad'][:3],
                exact_word=exact, owned_units=st['units'], owned_ascents=st['ascents'], dirty_clears=st['dirty'], k=(k1, k2), carrier=c)
    return info

def section_g1toy():
    t = time.time(); agg_all = {}
    for m in (3, 4):
        n = len(geometry(m)[1])
        for variant in ('pln_lo', 'pln_hi', 'pln_B', 'ctrl_t0', 'ctrl_m1', 'ctrl_zr'):
            agg = collections.Counter()
            for tt in range(n):
                for s in range(12):
                    rng = random.Random(1000 * tt + s)
                    k1, k2 = [(1, -1), (-1, 1), (2, Fr(-1, 2)), (1, 0), (0, 1), (3, 2), (None, None)][s % 7] if variant.startswith('pln') else (None, None)
                    r = g1_build(m, tt, variant, rng, k1, k2)
                    agg['runs'] += 1; agg['D=%d' % r['D']] += 1; agg['legal' if r['legal'] else 'ILLEGAL'] += 1
                    agg['exact' if r['exact_word'] else 'not_exact'] += 1
                    if 'top_solvable' in r: agg['top_solvable=%s' % r['top_solvable']] += 1
                    agg['z_in_cone' if r['z_support'] != 'singular' and 'X%d' % tt not in r['z_support'] else 'z_on_Xt_or_sing'] += 1
                    agg['owned_units=%d' % r['owned_units']] += 1
            agg_all[(m, variant)] = agg
            runs = agg['runs']
            check(runs == 12 * n and agg['legal'] == runs, 'legality/runs %s' % ((m, variant),))
            if variant.startswith('pln'):
                check(agg['D=1'] == runs and agg['not_exact'] == runs and agg['top_solvable=False'] == runs and agg['z_on_Xt_or_sing'] == runs, 'PLN must fail: %s %s' % ((m, variant), dict(agg)))
            else:
                check(agg['D=0'] == runs and agg['exact'] == runs, 'control must succeed: %s %s' % ((m, variant), dict(agg)))
            if variant == 'ctrl_zr': check(agg['top_solvable=True'] == runs and agg['z_in_cone'] == runs and agg['owned_units=2'] == runs, 'ctrl_zr')
    c3 = agg_all[(3, 'pln_lo')]['runs'] + agg_all[(3, 'pln_hi')]['runs'] + agg_all[(3, 'pln_B')]['runs']
    c4 = agg_all[(4, 'pln_lo')]['runs'] + agg_all[(4, 'pln_hi')]['runs'] + agg_all[(4, 'pln_B')]['runs']
    ok('TOPLBUILD G1 lift law: PLN top delivery (pln_lo/pln_hi/pln_B) top-solvable 0/%d on A3 and 0/%d on A4 (D=1 every run, all legal, none exact; z_t stays on X_t); controls ctrl_t0, ctrl_m1, ctrl_zr D=0 and exact word in every run (ctrl_zr: 2 owned units, z_t in cone, top solvable) (%.1fs)' % (c3, c4, time.time() - t))
    ok('GRAMLIFT ctrl (A3): no lift pln_lo/pln_hi D=1 on every run, ctrl_t0 D=0, ctrl_zr (1 lift + 1 DOWN) D=0 exact -- same runs as above (12 seeds x 6 ports)')

# =====================================================================================================================
# 5. MULTIHELP: Zone lemma toy (uses the CLONEAUDIT Run above)
# =====================================================================================================================
e_ = [1, 2, 4, 8]; q1, q2, qa, qa2, b1, b2 = 1, 2, 4, 8, 2, 1; VV = e_
inXi = lambda fr: all(not dot(v, q1) and not dot(v, q2) for v in fr)
def solve_rep(rows, tgt, n):
    m = len(rows); M = [[rows[z].get(j, Q(0)) for z in range(m)] + [tgt.get(j, Q(0))] for j in range(n)]
    piv = []; r = 0
    for c in range(m):
        p = next((i for i in range(r, n) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; M[r] = [x / M[r][c] for x in M[r]]
        for i in range(n):
            if i != r and M[i][c] != 0: f = M[i][c]; M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        piv.append(c); r += 1
    if any(M[i][m] != 0 for i in range(r, n)): return None
    rho = [Q(0)] * m
    for i, c in enumerate(piv): rho[c] = M[i][m]
    return rho

class ZRun(Run):
    def setup(s, W, helpers):
        s.W = W; s.trace = []; s.tg = s.targets(helpers)
    def targets(s, helpers):
        ix = s.idx; t = {}
        t['Y1'] = {ix('X_b1'): Q(-1), ix('X_s'): Q(s.W[0][0]), ix('X_s2'): Q(s.W[0][1])}
        t['Y2'] = {ix('X_b2'): Q(-1), ix('X_s'): Q(s.W[1][0]), ix('X_s2'): Q(s.W[1][1])}
        t['X_b1'] = {ix('X_b1'): Q(1), ix('Y1'): Q(-1)}; t['X_b2'] = {ix('X_b2'): Q(1), ix('Y2'): Q(-1)}
        t['X_s'] = {ix('X_s'): Q(1)}; t['X_s2'] = {ix('X_s2'): Q(1)}
        for hh in helpers: t[hh] = {ix(hh): Q(1)}
        return {k: {c: v for c, v in d.items() if v} for k, d in t.items()}
    def xi_rank(s):
        r1 = solve_rep(s.rows, {k: v for k, v in s.tg['Y1'].items()}, s.n); r2 = solve_rep(s.rows, s.tg['Y2'], s.n)
        blk = [{0: r1[z], 1: r2[z]} for z in range(s.n) if inXi(s.cur[z])]
        blk = [{k: v for k, v in b.items() if v} for b in blk]
        viol = [s.names[z] for z in range(s.n) if (r1[z] and any(dot(v, q1) for v in s.cur[z])) or (r2[z] and any(dot(v, q2) for v in s.cur[z]))]
        return rank(blk, 2), viol
    def snap(s, tag): s.trace.append((tag,) + s.xi_rank())

def mh_common(R):
    R.SCALE('Y1', -1); R.SCALE('Y2', -1)
    R.MOVE('Y1', [b1]); R.ADD('X_b1', 'Y1'); R.ADD('Y1', 'X_b1', -1)
    R.MOVE('Y2', [b2]); R.ADD('X_b2', 'Y2'); R.ADD('Y2', 'X_b2', -1)
def mh_finish(R, helpers):
    for r in ['X_b1', 'X_b2', 'X_s', 'X_s2'] + helpers:
        if span(R.cur[R.idx(r)]) != span(VV): R.MOVE(r, VV)
    wrong = [nm for nm in R.tg if R.rows[R.idx(nm)] != R.tg[nm]]
    return wrong, rank(R.rows, R.n), sorted({v for _, _, vs in R.trace for v in vs})
mh_names = ['X_s', 'X_s2', 'X_b1', 'X_b2', 'Y1', 'Y2']; mh_inits = [[qa], [qa2], [b1], [b2], [], []]
G_ = [qa, qa2]; G1_ = [qa, qa2, b1]; G2_ = [qa, qa2, b2]

def mh_escape(W):
    H = ['h1', 'h2']; R = ZRun(mh_names + H, mh_inits + [[], []]); R.setup(W, H); R.snap('t0'); mh_common(R); R.snap('cells')
    for hh, X in (('h1', 'X_s'), ('h2', 'X_s2')):
        R.MOVE(hh, [qa] if X == 'X_s' else [qa2]); R.ADD(X, hh, -1); R.ADD(hh, X)
    R.snap('parked')
    for r in ('h1', 'h2', 'X_s', 'X_s2'): R.MOVE(r, G_)
    (p, qq), (r_, s_) = W; det = Q(p * s_ - qq * r_); assert det != 0
    R.SCALE('h1', p); R.ADD('h1', 'h2', Q(qq))
    R.SCALE('h2', Q(s_) - Q(r_) * Q(qq) / Q(p)); R.ADD('h2', 'h1', Q(r_) / Q(p))
    R.snap('mixed in Xi')
    R.MOVE('h1', G1_); R.MOVE('Y1', G1_); R.ADD('Y1', 'h1'); R.snap('deliver Y1')
    R.MOVE('h2', G2_); R.MOVE('Y2', G2_); R.ADD('Y2', 'h2'); R.snap('deliver Y2')
    for r in ('h1', 'h2', 'X_s', 'X_s2'): R.MOVE(r, VV)
    R.ADD('h2', 'h1', -Q(r_) / Q(p)); R.SCALE('h2', 1 / (Q(s_) - Q(r_) * Q(qq) / Q(p))); R.ADD('h1', 'h2', -Q(qq)); R.SCALE('h1', 1 / Q(p))
    for hh, X in (('h1', 'X_s'), ('h2', 'X_s2')): R.ADD(hh, X, -1); R.ADD(X, hh)
    R.snap('V settled')
    wrong, fr, viol = mh_finish(R, H)
    return R, wrong, fr, viol

def mh_single():
    H = ['h1', 'h2']; R = ZRun(mh_names + H, mh_inits + [[], []]); R.setup(((1, 0), (1, 0)), H); R.snap('t0'); mh_common(R); R.snap('cells')
    R.MOVE('h1', [qa]); R.ADD('X_s', 'h1', -1); R.ADD('h1', 'X_s')
    R.MOVE('h2', [qa]); R.ADD('X_s', 'h2', -1); R.ADD('h2', 'X_s'); R.snap('two reads')
    R.MOVE('h1', [qa, b1]); R.MOVE('Y1', [qa, b1]); R.ADD('Y1', 'h1'); R.snap('Y1')
    R.MOVE('h2', [qa, b2]); R.MOVE('Y2', [qa, b2]); R.ADD('Y2', 'h2'); R.snap('Y2')
    for r in ('h1', 'h2', 'X_s'): R.MOVE(r, VV)
    R.ADD('h2', 'X_s', -1); R.ADD('X_s', 'h2'); R.ADD('h1', 'X_s', -1); R.ADD('X_s', 'h1')
    wrong, fr, viol = mh_finish(R, H)
    return R, wrong, fr, viol

def mh_chainable():
    nb1 = 8
    R = ZRun(mh_names, [[qa], [qa2], [nb1], [b2], [], []]); R.setup(((1, 0), (1, 0)), [])
    R.SCALE('Y1', -1); R.SCALE('Y2', -1)
    R.MOVE('Y1', [nb1]); R.ADD('X_b1', 'Y1'); R.ADD('Y1', 'X_b1', -1); R.MOVE('Y2', [b2]); R.ADD('X_b2', 'Y2'); R.ADD('Y2', 'X_b2', -1)
    R.MOVE('X_s', [qa, nb1]); R.MOVE('Y1', [qa, nb1]); R.ADD('Y1', 'X_s')
    R.MOVE('X_s', [qa, nb1, b2]); R.MOVE('Y2', [qa, nb1, b2]); R.ADD('Y2', 'X_s')
    for r in ['X_b1', 'X_b2', 'X_s', 'X_s2']: R.MOVE(r, VV)
    return R, [nm for nm in R.tg if R.rows[R.idx(nm)] != R.tg[nm]]

def section_multihelp():
    t = time.time()
    for W, lab in (((Q(1), Q(1)), (Q(1), Q(-1))), ((Q(1, 2), Q(-1, 2)), (Q(1, 2), Q(1, 2)))):
        R, wrong, fr, viol = mh_escape((W[0:2], lab) if False else (W, lab))
        tr = [(a, b) for a, b, _ in R.trace]
        check(not R.bad and R.ownmove_up == 0 and wrong == [] and fr == 8 == R.n and viol == [] and len(R.owned) == 0, 'ESCAPE must be exact with 0 owned: %s %s' % (wrong, R.bad))
        check([b for _, b in tr] == [2, 2, 2, 2, 1, 0, 0], 'Xi rank trace %s' % tr)
        check(R.peak == 0, 'no owned rows used')
    ok('MULTIHELP Zone lemma ESCAPE: 2 senders (weights (1,1),(1,-1) and +-1/2), 2 tokened public helpers, X-PARK + Xi mix, 0 owned rows (peak 0): 0 illegal events, all finals exact, final map 8/8, Xi rank 2->2->2->2->1->0->0, no adjoint-support violation')
    try:
        mh_escape(((Q(1), Q(1)), (Q(1), Q(1)))); raise RuntimeError('proportional weights must be singular')
    except AssertionError:
        ok('MULTIHELP NEG control: proportional weights (1,1),(1,1): Xi mix singular (det 0), no e1/e2 pieces')
    R, wrong, fr, viol = mh_single()
    y2 = {R.names[k]: v for k, v in R.rows[R.idx('Y2')].items()}
    check(not R.bad and wrong == ['Y2'] and fr == 8 and viol == ['h1'] and [b for _, b, _ in R.trace][-2:] == [0, 0], 'single-sender NEG')
    check(y2 == {'X_b2': Q(-1), 'X_s': Q(1), 'h1': Q(-1)}, 'Y2 final %s' % y2)
    ok('MULTIHELP NEG control: ONE sender (per-sender counting needs >=1 owned row): finals wrong [Y2] (Y2 = -x_b2 + x_s - h1), Xi rank stuck at 1 until delivery, adjoint-support violation by h1')
    R, wrong = mh_chainable()
    check(not R.bad and wrong == [], 'chainable POS')
    ok('MULTIHELP POS control: chainable geometry, one sender on its own chain: 0 illegal events, finals exact (%.1fs)' % (time.time() - t))

# =====================================================================================================================
# 6. GRAMLIFT alg.py: A3 Gram-lift algebra, Theorem M (own exact linear algebra)
# =====================================================================================================================
def rref(M):
    A = [[Fr(x) for x in row] for row in M]; piv = []; r = 0
    ncol = len(A[0]) if A else 0
    for c in range(ncol):
        p = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if p is None: continue
        A[r], A[p] = A[p], A[r]; inv = 1 / A[r][c]; A[r] = [x * inv for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]; A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        piv.append(c); r += 1
        if r == len(A): break
    return A[:r], piv
def rank_m(M): return len(rref(M)[1]) if M and M[0] else 0
def nullspace(M):
    R, piv = rref(M); n = len(M[0]); out = []
    for f in [c for c in range(n) if c not in piv]:
        v = [Fr(0)] * n; v[f] = Fr(1)
        for i, c in enumerate(piv): v[c] = -R[i][f]
        out.append(v)
    return out
def mmul(A, B):
    Bt = list(zip(*B)); return [[sum(a * b for a, b in zip(r, c)) for c in Bt] for r in A]
def minv(M):
    n = len(M); A = [list(map(Fr, r)) + [Fr(int(i == j)) for j in range(n)] for i, r in enumerate(M)]
    R, piv = rref(A); assert piv[:n] == list(range(n)), 'singular'; return [r[n:] for r in R]

def section_gramlift():
    t = time.time()
    N, prts, G, B, C_, Z = geometry(3); n = 6
    Rr = [[Fr(x) for x in r] for r in B]; Gm = [[Fr(x) for x in r] for r in G]
    K = nullspace(Gm)
    check(rank_m(Gm) == 3 and len(K) == 3, 'rank G / dim K')
    check(all((G[s][u] == 0) == (dot(prts[s], prts[u]) == 1) for s in range(n) for u in range(n) if s != u) and [G[i][i] for i in range(n)] == [2] * 6, 'Gram pattern')
    colsB = [[Rr[i][j] for i in range(n)] for j in range(3)]
    inter = len(colsB) + len(K) - rank_m(colsB + K)
    check(inter == 0, 'range(B) cap K')
    part = lambda u, w: u != w and dot(prts[u], prts[w]) == 0
    cs = [p for p in itertools.permutations(range(n)) if all(part(u, p[u]) for u in range(n))]
    check(len(cs) == 80, 'partner derangements %d' % len(cs))
    rng = random.Random(3); got = 0
    for c in (cs[0], cs[40], cs[79]):
        P = [[Fr(int(c[u] == w)) for w in range(n)] for u in range(n)]
        for trial in range(200):
            Cm = [[Fr(rng.randint(-2, 2)) for _ in range(n)] for _ in range(3)]
            BC = mmul(Rr, Cm); E = [[(1 if i == j else 0) - P[i][j] - BC[i][j] for j in range(n)] for i in range(n)]
            if rank_m(E) < n: continue
            A = mmul(minv(E), Rr)
            for u in range(n):
                xpart = [P[u][w] + E[u][w] for w in range(n)]; spart = [sum(E[u][w] * A[w][j] for w in range(n)) for j in range(3)]
                check(spart == Rr[u], 'sigma-part'); check(all(xpart[w] == (1 if w == u else 0) - BC[u][w] for w in range(n)), 'x-part')
            Psi = [[sum(k[w] * ((1 if w == u else 0) - BC[u][w]) for w in range(n)) for k in K] + list(Rr[u]) for u in range(n)]
            Psi0 = [[k[u] for k in K] for u in range(n)]
            check(rank_m(Psi) == 6 and rank_m(Psi0) == 3, 'Theorem M ranks %d %d' % (rank_m(Psi), rank_m(Psi0)))
            got += 1; break
    check(got == 3, 'three carrier maps')
    ok('GRAMLIFT A3: rank G=3, dim ker G=3, G zero exactly on non-orthogonal pairs, diag 2; Y-side frozen algebra exact (E=I-P-BC invertible, xi_u=x_u+kappa_u, kappa_u in K) on 3 of the 80 partner derangements; range(B) cap K = 0 hence Theorem M rank Psi = 6 = n (so D >= 6 - m_o = 6 with m_o=0) vs no-lift baseline rank Psi0 = 3 (%.1fs)' % (time.time() - t))

if __name__ == '__main__':
    section_cloneaudit()
    section_rank_lemma_random()
    section_ychan()
    section_newmove()
    section_g1toy()
    section_multihelp()
    section_gramlift()
    print('total %.1fs' % (time.time() - T0))
    print('PASS_WALL_TOYS')
