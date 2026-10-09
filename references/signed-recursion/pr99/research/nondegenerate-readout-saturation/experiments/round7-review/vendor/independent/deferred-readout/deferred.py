"""Shared reader and accounting for the round-seven bit side (stdlib only).

Frozen inputs (certificates/round7/):
  witness_23.json.gz   the base side program: DAG (leaves = triples of [h], additions), outputs (c, T), retained
                       totals, links, the flag matrix, the lift index j(n) of every lifted addition and the late-copy
                       decisions; checked by check_lifted.py;
  deferred_23.json.gz  the reordered stage-1 word: the slot schedule (ops, the node held by every slot over time,
                       slot starts, output and retained slots), the deferred readout frames sigma_u, the V-leaf start
                       frames s_i (both as primitive integer bases), the readout order, the X_S order of every leaf,
                       the order of the deferred V gates, and the dimension of every node frame and late-copy
                       intersection (re-derived exactly by check_frames.py).

Ops: ['add', piv, oth, n]  a[piv] += a[oth], the addition of node n;  ['fan', piv, [f...]]  a[f] += a[piv] for fresh
slots f (copies);  ['src', s, n]  the V gate a[s] += x_S of leaf n (applied outside L, see check_word.py)."""
import gzip, json, os
from collections import Counter, defaultdict
from itertools import combinations
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
DATA = os.path.join(ROOT, 'certificates', 'round7')


def load_json(name):
    with gzip.open(os.path.join(DATA, name), 'rt') as fh:
        return json.load(fh)


def load(h=23, witness=None, data=None):
    """the base witness and the design-B data of one round-seven witness (default: the files of h)."""
    W = load_json(witness or 'witness_%d.json.gz' % h); D = load_json(data or 'deferred_%d.json.gz' % h)
    assert W['h'] == D['h'] == h
    return W, D


class Schedule:
    """The design-B schedule in convenient form."""
    def __init__(self, W, D):
        self.h = h = D['h']; self.R = D['R']; self.trip = list(combinations(range(h), 3)); self.v = len(self.trip)
        self.tid = {T: i for i, T in enumerate(self.trip)}
        self.args = {int(n): (tuple(a) if a else None) for n, a in W['args'].items()}
        self.ops = [tuple(o[:2]) + (tuple(o[2]),) if o[0] == 'fan' else tuple(o) for o in D['ops']]
        self.hold = D['hold']; self.start = D['start']
        self.out = {s: (c, tuple(T)) for s, c, T in D['out']}
        self.ret = {s: c for s, c in D['ret']}
        self.srcop = {o[1]: o[2] for o in self.ops if o[0] == 'src'}
        self.readout = D['readout_order']; self.sel = set(self.readout)
        self.sigma = dict(zip(D['readout_order'], D['sigma']))
        self.f = [0] * self.R
        for s, B in self.sigma.items(): self.f[s] = len(B)
        self.vstart = dict(zip(D['vleaf_slots'], D['vleaf_start']))
        self.xs = [(n, us) for n, us in D['xs_order']]
        self.late_v = D['deferred_v_order']
        self.node_dims = {n: d for n, d in D['node_dims']}
        self.late_dims = {(n, tuple(lt)): d for n, lt, d in D['late_dims']}
        self.late = {int(n): (list(e), list(l)) for n, (e, l) in W['late'].items()}
        self.pivslot = {o[3]: o[1] for o in self.ops if o[0] == 'add'}

    def touch(self, op):
        if op[0] == 'add': return [op[1], op[2]]
        if op[0] == 'fan': return [op[1]] + list(op[2])
        return []

    def root_targets(self):
        rt = {}
        for s, (c, T) in self.out.items(): rt[s] = [self.tid[T]]
        for s, c in self.ret.items(): rt[s] = [t for t, T in enumerate(self.trip) if c in T]
        return rt

    def adjoint(self):
        """garbage coefficients over Z: cov[s][t] = coefficient of slot s's start value in target y_T at the end of L
        (the transpose sweep of L applied to the root reads); the F2 circuit uses their parities."""
        cov = [dict() for _ in range(self.R)]
        for s, ts in self.root_targets().items():
            for t in ts: cov[s][t] = cov[s].get(t, 0) + 1
        def addto(d, e):
            for t, x in e.items(): d[t] = d.get(t, 0) + x
        for op in reversed(self.ops):
            if op[0] == 'add': addto(cov[op[2]], cov[op[1]])
            elif op[0] == 'fan':
                for g in op[2]: addto(cov[op[1]], cov[g])
        return cov

    # ------------------------------------------------------------------ frame keys of every slot's chain
    def start_key(self, s):
        """('v', s) for a V-leaf slot (start s_i), ('n', n0) for a base or early copy, ('c', n0, late suffix)."""
        n0 = self.hold[s][0]
        if self.args[n0] is None: return ('v', s)
        st = self.start[s]; k = st[2]; dec = self.late.get(n0)
        if dec is None or k in dec[0]: return ('n', n0)
        lt = dec[1]; return ('c', n0, tuple(lt[lt.index(k):]))

    def chain_keys(self, s):
        """frames of slot s in time order: [sigma_u | 0], start, then every later node it holds (with the pivot's
        late-copy intersections after a node it pivots), its root frame if any, F."""
        ch = [('sigma', s) if s in self.sel else ('0',), self.start_key(s)]
        for idx, n in enumerate(self.hold[s]):
            if idx > 0: ch.append(('n', n))
            if self.args[n] is not None and self.pivslot.get(n) == s and n in self.late:
                lt = self.late[n][1]
                for i in range(len(lt) - 1): ch.append(('c', n, tuple(lt[i:])))
        if s in self.out: c, T = self.out[s]; ch.append(('out', c, T))
        if s in self.ret: ch.append(('ret', self.ret[s]))
        ch.append(('F',)); return ch

    def dim(self, key):
        k = key[0]
        if k == '0': return 0
        if k == 'F': return self.h
        if k in ('out', 'ret'): return self.h - 1
        if k == 'n': return self.node_dims[key[1]]
        if k == 'c': return self.late_dims[key[1], key[2]]
        if k == 'sigma': return len(self.sigma[key[1]])
        if k == 'v': return len(self.vstart[key[1]])
        raise KeyError(key)

    def ylevels(self, cov):
        """deferred readout levels (dim sigma) on every target, from the garbage-coefficient supports."""
        lev = defaultdict(set)
        for s in self.readout:
            for t in cov[s]: lev[t].add(self.f[s])
        return {t: sorted(lev[t]) for t in range(self.v)}

    def xdata(self, dimof=None):
        dimof = dimof or (lambda s: len(self.vstart[s]))
        out = []
        for n, us in self.xs:
            ds = [1] + [dimof(s) for s in us] + [self.h]
            ds = [d for i, d in enumerate(ds) if i == 0 or d != ds[i - 1]]
            out.append([b - a for a, b in zip(ds, ds[1:])])
        return out


def inner(r, h):
    """children of a rank-r chain step under the inner-corner lemma (one block of width 2r-h when 2r > h)."""
    return [1] * (h - r) + [2 * r - h] if 2 * r > h else [1] * r


def chain_ranks(S, dimof=None):
    """multiset of chain-step ranks over all slots (dims must be monotone along every chain)."""
    dimof = dimof or S.dim; rk = Counter()
    for s in range(S.R):
        ds = [dimof(k) for k in S.chain_keys(s)]
        assert all(b >= a for a, b in zip(ds, ds[1:])), ('decreasing chain', s)
        assert ds[-1] == S.h
        for a, b in zip(ds, ds[1:]):
            if b > a: rk[b - a] += 1
    return rk


ROUND6_CORNER = lambda h: [h - 2] + [1] * (h + 1)          # data-entrance corner runs, rounds six and seven
STAIRCASE_CORNER = lambda h: [h - 2, h - 5] + [1] * 6       # staircase corner (check_stair.py)


def histogram(S, rk, ylev, xdata, corner=None):
    """child-width histogram of the batched two-stage bit interchange with deferred readouts and V leaves.
    Per stage (stage two is the complement time-reversal of stage one, same edge multiset), each of the v invocations:
      every slot u: its auxiliary edge of rank m - r_u (block m - 2 r_u) and its corner of rank r_u = h - dim sigma_u,
        both batched by the inner lemma, plus its chain steps;
      every centre: the copy's step U_c -> 0 of rank h-1;
      every target y_T: the chain 0 -> deferred levels -> t_T^perp (total rank h-1);
      every leaf X_S: its chain <t_S> -> V-gate frames -> F (total rank h-1).
    Data: the entrance block m-4h+2 with its corner runs, one copy-correction singleton per pair."""
    h, v, R = S.h, S.v, S.R; m = h * h; N = v * v; A = v * R; H = Counter()
    corner = corner or ROUND6_CORNER(h); assert sum(corner) == 2 * h - 1
    corners = Counter(h - S.f[s] for s in range(R))
    for _ in range(2):
        for r, c in corners.items():
            H[m - 2 * r] += v * c
            for w in inner(r, h): H[w] += v * c
        for r, c in rk.items():
            for w in inner(r, h): H[w] += v * c
        for _c in range(h):
            for w in inner(h - 1, h): H[w] += v
        for t in range(v):
            ds = sorted(set([0] + ylev[t] + [h - 1]))
            for a, b in zip(ds, ds[1:]):
                for w in inner(b - a, h): H[w] += v
        for xs in xdata:
            for x in xs:
                for w in inner(x, h): H[w] += v
    H[m - 4 * h + 2] += 2 * N
    for w in corner: H[w] += 2 * N
    H[1] += N
    H = {w: c for w, c in H.items() if c}
    Wd = 2 * N + 2 * A; L = 2 * v * h * (h - 1); s = Wd * m - N + L
    return dict(h=h, m=m, v=v, N=N, W=Wd, L=L, s=s, R=R, hist=H)

