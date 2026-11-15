"""Our own engine for bitE8/1 words (E8 root-line labels, h = 8): frame algebra over Q via root-line masks,
legality/F2 replay, five-stage histogram, exact bit coarse saving and PR #315 outer assembly (our engine copies).
Chafik Boukhalfa (chafreaky) with Anthropic Claude assistance; Apache-2.0."""
import gzip, json, os, importlib.util
from fractions import Fraction as Q
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
def _load(n):
    s = importlib.util.spec_from_file_location('e8_' + n, os.path.join(HERE, "engines", n + ".py"))
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
moment = _load('moment'); other = _load('base_two_moment'); outer = _load('outer')

B2 = Q(876248285600677, 10**18)   # Sussman E8 five-stage (PR #352)
B3 = Q(932783231884153, 10**18)   # DaysSky seven-stage B_3 (PR #363; no Lean proof)


def load_word(p):
    with (gzip.open(p, 'rt') if p.endswith('.gz') else open(p)) as f:
        return json.load(f)


def save_word(c, p):
    with gzip.open(p, 'wt') as f:
        json.dump(c, f, separators=(',', ':'))


def rank(vecs):
    rows = [[Q(x) for x in r] for r in vecs]; rk = 0
    n = len(rows[0]) if rows else 0
    for col in range(n):
        p = next((i for i in range(rk, len(rows)) if rows[i][col] != 0), None)
        if p is None: continue
        rows[rk], rows[p] = rows[p], rows[rk]
        for i in range(len(rows)):
            if i != rk and rows[i][col] != 0:
                f = rows[i][col] / rows[rk][col]; rows[i] = [a - f * b for a, b in zip(rows[i], rows[rk])]
        rk += 1
    return rk


class Lat:
    """Root-spanned subspaces of Q^8 represented by the mask of root lines they contain."""
    def __init__(self, lines):
        self.lines = [tuple(x) for x in lines]; self.v = len(lines)
        self._dim = {0: 0}; self._close = {}
        # Gram (form <x,y>/2) for orthogonality
        self.ip = [[sum(a * b for a, b in zip(x, y)) // 2 for y in self.lines] for x in self.lines]

    def close(self, mask):
        """mask of all root lines in span(roots of mask)"""
        if mask in self._close: return self._close[mask]
        idx = [i for i in range(self.v) if mask >> i & 1]
        basis = []
        for i in idx:
            if rank([self.lines[j] for j in basis] + [self.lines[i]]) > len(basis): basis.append(i)
        d = len(basis); out = 0
        if d == 8: out = (1 << self.v) - 1
        elif d:
            B = [self.lines[j] for j in basis]
            for i in range(self.v):
                if rank(B + [self.lines[i]]) == d: out |= 1 << i
        self._close[mask] = out; self._close[out] = out; self._dim[out] = d
        return out

    def dim(self, mask):
        if mask not in self._dim: self.close(mask)
        return self._dim[mask]

    def basis(self, mask):
        b = []
        for i in range(self.v):
            if mask >> i & 1 and rank([self.lines[j] for j in b] + [self.lines[i]]) > len(b): b.append(i)
        return b

    def perp(self, t):
        return self.close(sum(1 << j for j in range(self.v) if self.ip[t][j] == 0))


def to_masks(c, L):
    return [L.close(sum(1 << i for i in fr)) for fr in c['frames']]


PHASES = ('D', 'A', 'B', 'C')


def replay(c, L=None, masks=None, check_f2=True, span=True, span_mode='z'):
    """Exact legality + F2 replay + histogram of a bitE8/1 word. Returns dict(H_local, steps, ...).
    Legality: each register's frames nested (mask inclusion = exact Q-subspace inclusion for root-spanned frames) and
    strictly increasing at each move; every gate at one common frame; D compensation at frame 0; y at frame 0 at the
    scatter; COPY of retained totals; final frames (x, helpers FULL; y_t at its cap t-perp).
    Source-span: every non-target operand's x-support lies in the gate frame."""
    L = L or Lat(c['lines']); masks = masks or to_masks(c, L)
    v, R, h = c['v'], c['R'], c['h']; n = 2 * v + R; FULL = (1 << v) - 1
    cur = [masks[f] for f in c['start']]
    for r in range(v): assert cur[r] == L.close(1 << r), 'x start'
    for r in range(v, 2 * v): assert cur[r] == 0, 'y start at 0'
    sig = [L.dim(cur[r]) for r in range(n)]
    H = Counter(); steps = 0; viol = []
    val = [1 << i for i in range(n)]
    zsupp = [{i: 1} if i < v else {} for i in range(n)]  # integer support of each register over the x columns (all ADDs are +1)
    def climb(r, m):
        nonlocal steps
        if cur[r] == m: return
        assert cur[r] & ~m == 0 and cur[r] != m, ('not nested', r)
        H[L.dim(m) - L.dim(cur[r])] += 1; steps += 1; cur[r] = m
    def run(gates, ph):
        for k, (f, d, srcs) in enumerate(gates):
            m = masks[f]
            assert d >= v and d not in srcs and len(set(srcs)) == len(srcs), (ph, k)
            for x in [d] + srcs: climb(x, m)
            for s in srcs:
                val[d] ^= val[s]
                if span:
                    if s < v or s >= 2 * v:
                        ms = sum(1 << i for i in zsupp[s])
                        if ms & ~m: viol.append((ph, k, s))
                    zd = zsupp[d]
                    for i, a in zsupp[s].items():
                        w = zd.get(i, 0) + a
                        if w: zd[i] = w
                        else: zd.pop(i, None)
                    if span_mode == 'f2':
                        zsupp[d] = {i: 1 for i in range(v) if val[d] >> i & 1}
            if span and d >= 2 * v:
                md = sum(1 << i for i in zsupp[d])
                if md & ~m: viol.append((ph, k, d))
    run(c['D'], 'D')
    for r in range(v, n): assert cur[r] == masks[c['start'][r]], 'D compensation at frame 0 (helpers untouched otherwise)'
    run(c['A'], 'A')
    for t in range(v): assert cur[v + t] == 0, 'y at frame 0 at the scatter'
    copies = [val[q] for q in c['ret']]
    for q in c['ret']:
        assert q >= 2 * v; H[L.dim(cur[q])] += 1
    for t, row in enumerate(c['scatter']):
        for k in row: val[v + t] ^= copies[k]
    run(c['B'], 'B'); run(c['C'], 'C')
    for r in range(n): climb(r, masks[c['final'][r]])
    for r in range(v): assert cur[r] == FULL
    for r in range(2 * v, n): assert cur[r] == FULL
    for t in range(v): assert cur[v + t] == L.perp(t), 'y final at cap'
    if check_f2:
        for s in range(v): assert val[s] == 1 << s
        for t in range(v): assert val[v + t] == (1 << (v + t)) | (1 << t), ('target', t)
        for r in range(2 * v, n): assert val[r] == 1 << r, ('helper', r)
    return dict(sig=sig, viol=viol, H=H, steps=steps, n=n, v=v, R=R, h=h, L=L, masks=masks, ncopy=len(c['ret']))


def profile(H_local, v, h=8):
    prof = Counter({j: 5 * c for j, c in H_local.items()})
    for j in (2 * h - 2, h - 1, 2 * h + 2, 4): prof[j] += 2 * v
    return prof


def coarse(H, m, W):
    grid = Q(1, 10**18)
    root = moment.certify(dict(H), m, W, True); c = Q(int(Q(root['lower']) * 10**18), 10**18)
    assert moment.moment(H, m, W, c, True)[1] < 1 < moment.moment(H, m, W, c + grid, True)[0]
    fb = 32 * m * m * sum(H.values())
    _, up = other.moment(m, W, list(H.items()), c); _, bad = other.moment(m, W, [(1, fb)], c)
    lo, _ = other.moment(m, W, list(H.items()), c + grid); blo, _ = other.moment(m, W, [(1, fb)], c + grid)
    assert up + Q(1, 10**16) * bad < 1 < lo + Q(1, 10**16) * blo
    return c


def kappa(c, b):
    grid = Q(1, 10**18); eta = Q(1, 10**12); beta = Q(1, 10**9); cap = (1 - beta) * b
    sv = min(c, Q(((cap - grid) * 10**18).__floor__(), 10**18)); binding = 'bit' if sv == c else 'complex'
    chain = [Q(384599, 10**10)]
    for _ in range(3):
        a = (1 - sv) * sv + sv * chain[-1]; assert chain[-1] < a < sv < 1 - a; chain.append(a)
    bit = chain[-1]
    bridge = dict(proof='PROOF.md', representation='Exact powers with source-bound finite overcharges',
                  semantic=dict(G=dict(base=2, exponent=30000), E=dict(base=2, exponent=100000), B_upper=dict(base=2, exponent=100001),
                                C0=dict(base=2, exponent=210000), C1=1, strict_literal_gap=1, induction_gap_lower=1),
                  rows=dict(coefficient=20161, degree=10**6, suffix_slope=4 * 10**6, degree_gap=Q(10**6) - Q(51 * 20161, 25)))
    q = bit * (1 - 2 * eta); mn = (1 - eta) * q / (1 + q); t = mn * 10**18; k = Q((t.numerator - 1) // t.denominator, 10**18)
    asm = outer.assembly(bit, b, bridge, k, eta=eta, beta=beta)
    assert len(asm['strict_constraints']) == 47 and min(asm['strict_constraints'].values()) > 0
    try:
        outer.assembly(bit, b, bridge, k + grid, eta=eta, beta=beta); raise SystemExit('ADJACENT ADMITTED')
    except AssertionError: pass
    return k, binding


def price_word(c, **kw):
    r = replay(c, **kw)
    v, h, R = r['v'], r['h'], r['R']; m = 5 * h
    resid = sum(h - r['sig'][x] for x in range(2 * v, 2 * v + R))
    T = 1 if resid % h == 0 else h
    W = (4 * v * h + resid) * T // h; assert (4 * v * h + resid) * T % h == 0
    prof = Counter({j: T * k for j, k in profile(r['H'], v, h).items()}); mass = sum(a * b for a, b in prof.items())
    L_copy = h * r['ncopy']
    assert m * W - mass == T * (4 * v - 5 * L_copy), ('deficit', m * W - mass)
    assert 2 * max(prof) < m
    cc = coarse(prof, m, W)
    return dict(c=cc, H=r['H'], prof=prof, W=W, T=T, resid=resid, m=m, deficit=m * W - mass, replay=r)


def phi_fn(m, W, a):
    """linearized moment term per child of rank r (float), for search scoring"""
    import math
    return lambda r: r / (m * W) * math.exp(a * math.log(m / r))
