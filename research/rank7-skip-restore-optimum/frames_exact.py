# SPDX-License-Identifier: Apache-2.0
"""Exact frame optimum of a BORROW-WORD for a fixed gate order (Python standard library only).

This is a numpy-free port of the certified frame solver used for the receipts of this package: the BORROW-WORD frame model
of our r12 harness (`bp.py`: build_problem, BorrowGraph, centre_descents) on the frame toolkit of PR #1186
(research/exact-frame-toolkit/frames.py: Graph domains, exact variable elimination, component accounting, Costs). Only
the exact variable-elimination path is ported; a component that elimination cannot finish raises instead of falling back
to the toolkit's numpy chain-dual solver, so every optimum reported here is an exhaustive minimum.

Frame model (the BORROW-WORD branch of PR2833's audit_local.py): every A (after the prelude), B and restore gate is one
vertex whose frame (a subspace of F_2^9) is shared by its registers; register chains are nested (monotone); every rank
jump is paid c[jump]; ends climb (paid) to the end frames; at the end of A the targets equal their target levels and the
centres their centre frames (cut equality); a warp requires the lender's current frame to EQUAL its entry frame U (no
payment) and resets it to E (modelled by splitting the lender into virtual registers). Centre descents are fixed.
Optional caps bound a register's frame at its last vertex before its end (used for the forced restore-entry caps).

Weights: c[r] = floor(2^40 * lo_r(b)) at b = 0.001703676387993676, lo_r the outward lower moment bound of the vendored
research/frame-domain-ceiling engines (exactly frames.Costs). Marius-Paul Dumitrean, with substantial AI assistance
(Claude Code).
"""
import collections
import importlib.util
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GK = _load('rank7sro_gk_common', HERE / 'vendor' / 'gk_common.py')                # canonical GF(2) bases
MOM = _load('rank7sro_moment', HERE / 'vendor' / 'moment.py')                     # moment engine (Mercator/exp)
MOM2 = _load('rank7sro_base_two_moment', HERE / 'vendor' / 'base_two_moment.py')  # second engine (PR39 cross-check)

V = 112
H = 9
M_DIM = 73
W_LIVE = 7168
B_DEFAULT = '0.001703676387993676'
UNIT_BITS = 40
VE_MAX_COMPONENT = 600
VE_MAX_TUPLES = 5_000_000


class Infeasible(Exception):
    pass


@lru_cache(None)
def basis(F):
    return GK.basis(F)


@lru_cache(None)
def span(F):
    s = {0}
    for b in F:
        s |= {x ^ b for x in s}
    return frozenset(s)


def leq(F, G):
    return span(tuple(F)) <= span(tuple(G))


def join(F, G):
    return basis(tuple(F) + tuple(G))


def meet(*frames):
    s = set(span(FULL9))
    for f in frames:
        s &= span(tuple(f))
    return basis(tuple(s))


FULL9 = basis(tuple(1 << i for i in range(H)))


def perp_port(p):
    return basis(tuple(x for x in range(1, 1 << H) if (x & p).bit_count() % 2 == 0))


def regs_of(g):
    return [g[1]] + ([g[2]] if g[0] == 'add' else [])


@lru_cache(None)
def weights(b=B_DEFAULT):
    """integer surrogate weights c[0..9] (frames.Costs, unit 2^-40)"""
    b = Q(b)
    fl, fu = MOM2.moment(M_DIM, W_LIVE, [(1, 32 * M_DIM * M_DIM)], b)
    c = {0: 0}
    for r in range(1, H + 1):
        lo1, hi1 = MOM.moment({r: 1}, M_DIM, W_LIVE, b, True)
        lo2, hi2 = MOM2.moment(M_DIM, W_LIVE, [(r, 1)], b)
        lo2 += fl / Q(10 ** 16)
        hi2 += fu / Q(10 ** 16)
        lo, hi = max(lo1, lo2), min(hi1, hi2)
        if not 0 < lo <= hi:
            raise ValueError(('moment bounds out of order', r))
        c[r] = (lo.numerator << UNIT_BITS) // lo.denominator
    return tuple(c[r] for r in range(H + 1))


def profile_cost(profile, c=None):
    c = c or weights()
    return sum(n * c[int(r)] for r, n in profile.items())


def centre_descents(w):
    """the auditor's cut-path payments (fixed by centre frames, target levels and cut gates)"""
    lev = {int(t): basis(tuple(U)) for t, U in w.get('target_levels', {}).items()}
    paid = collections.Counter()
    for q, U in zip(w['centers'], w['center_frames']):
        U = basis(tuple(U))
        served = {lev.get(e[1] - V, ()) for e in w['cut'] if e[2] == q}
        for T in sorted(served, key=lambda x: -len(x)):
            if not leq(T, U):
                raise ValueError('centre path not nested')
            if T != U:
                paid[len(U) - len(T)] += 1
            U = T
    return paid


def build_problem(w):
    """BORROW-WORD -> inline problem with virtual registers split at warps (bp.build_problem)."""
    R = w['report']['R']
    N = 2 * V + R
    removed = set(w['removed'])
    start = [(p,) for p in w['ports']] + [()] * (V + R)
    for q, U in w.get('start_extra', {}).items():
        start[int(q)] = basis(tuple(U))
    end = [FULL9] * V + [perp_port(p) for p in w['ports']] + [FULL9] * R
    for q, U in w.get('helper_final', {}).items():
        end[int(q)] = basis(tuple(U))
    starts = list(start)
    finals = [None] * N
    alias = list(range(N))
    eq_end = set()
    nxt_virtual = [N]

    def close_and_split(r, fr, to):
        cur = alias[r]
        finals[cur] = basis(tuple(fr))
        eq_end.add(cur)
        new = nxt_virtual[0]
        nxt_virtual[0] += 1
        starts.append(basis(tuple(to)))
        finals.append(None)
        alias[r] = new

    def ren(e):
        g = list(e)
        if g[0] == 'add':
            g[1] = alias[g[1]]
            g[2] = alias[g[2]]
        else:
            g[1] = alias[g[1]]
        return g

    npre = w.get('prelude_events', 0)
    A_out = []
    A_idx = []
    for i, e in enumerate(w['A']):
        if e[0] == 'warp':
            if i >= npre:
                raise ValueError('warp after prelude')
            _, r, op, fr, to = e
            close_and_split(r, fr, to)
        else:
            A_out.append(ren(e))
            A_idx.append(i)
    centers_at_cut = [alias[q] for q in w['centers']]
    byp = collections.defaultdict(list)
    for op, rec in enumerate(w['warps'], 1):
        byp[rec[0]].append(op)
    B_out = []
    for p in range(len(w['B']) + 1):
        for op in byp.get(p, []):
            pos, lender, cols, U, E = w['warps'][op - 1]
            close_and_split(lender, U, E)
        if p < len(w['B']):
            B_out.append(ren(w['B'][p]))
    T_out = [ren(e) for e in w['restore']]
    Nv = nxt_virtual[0]
    for r in range(N):
        a = alias[r]
        if finals[a] is None:
            finals[a] = end[r]
    for r in removed:
        starts[r] = ()
        finals[r] = ()
        if alias[r] != r:
            raise ValueError('removed helper with a warp')
    w2 = dict(A=A_out, B=B_out, _tail=T_out, ports=w['ports'], centers=centers_at_cut, center_frames=w['center_frames'],
              target_levels=w.get('target_levels', {}), R=Nv - 2 * V,
              _start_frames=[tuple(s) for s in starts], _final_frames=[tuple(f) for f in finals])
    meta = dict(N=N, Nv=Nv, eq_end=eq_end, A_idx=A_idx, virtual=Nv - N, removed=len(removed))
    return w2, meta


def aliases(w, meta):
    """original register -> list of its virtual registers (warp segments) in solver order"""
    N = meta['N']
    alias = {q: [q] for q in range(N)}
    nxt = N
    for e in w['A']:
        if e[0] == 'warp':
            alias[e[1]].append(nxt)
            nxt += 1
    byp = collections.defaultdict(list)
    for op, rec in enumerate(w['warps'], 1):
        byp[rec[0]].append(op)
    for p in range(len(w['B']) + 1):
        for op in byp.get(p, []):
            alias[w['warps'][op - 1][1]].append(nxt)
            nxt += 1
    return alias


class FrameGraph:
    """event graph of the inline problem (frames.Graph + bp.BorrowGraph, check_literal=False, tail_mutable=True)"""

    def __init__(self, w, eq_end, caps=None, cut_equality=True):
        R = w['R']
        N = 2 * V + R
        self.N = N
        caps = caps or {}
        nodes = []
        chains = [[] for _ in range(N)]
        mutable = []
        start_frames = w['_start_frames']
        final_frames = w['_final_frames']
        tail = w.get('_tail', [])

        def node(regs, Fr, sec, index=None):
            k = len(nodes)
            nodes.append((tuple(regs), basis(tuple(Fr)), sec, index))
            for r in regs:
                chains[r].append(k)
            if sec in ('A', 'B', 'tail'):
                mutable.append(k)

        for r in range(N):
            node([r], start_frames[r], 'start')
        for sec in ('A', 'B'):
            if sec == 'B':
                for r, Fr in zip(w['centers'], w['center_frames']):
                    node([r], Fr, 'cut')
                for t in range(V):
                    node([V + t], w.get('target_levels', {}).get(str(t), []), 'cut')
            for i, e in enumerate(w[sec]):
                node(regs_of(e), e[-1] if e[-1] is not None else [], sec, i)
        for i, e in enumerate(tail):
            node(regs_of(e), e[-1], 'tail', i)
        for r in range(N):
            node([r], final_frames[r], 'end')
        self.chains = chains
        self.mutable = mutable
        prev = {}
        nxt = {}
        for r, ch in enumerate(chains):
            for p, q in zip(ch, ch[1:]):
                prev[q, r] = p
                nxt[p, r] = q
        self.prev = prev
        self.nxt = nxt
        allowed = set(mutable)
        lower = {}
        upper = {}
        for k, (regs, F0, sec, idx) in enumerate(nodes):
            lower[k] = basis(tuple(x for r in regs for x in lower[prev[k, r]])) if k in allowed else F0
            if k in allowed:
                for r in regs:
                    j = nxt.get((k, r))
                    if j is None:
                        continue
                    if (cut_equality and sec == 'A' and nodes[j][2] == 'cut') or (nodes[j][2] == 'end' and r in eq_end):
                        lower[k] = basis(tuple(lower[k]) + tuple(nodes[j][1]))
            elif sec != 'end':
                for r in regs:
                    j = nxt.get((k, r))
                    if j is not None and nodes[j][2] == 'end' and r in eq_end and span(F0) != span(nodes[j][1]):
                        raise Infeasible(('fixed vertex differs from its warp frame', k, sec, idx, r))
        for k in reversed(range(len(nodes))):
            regs, F0, sec, idx = nodes[k]
            if k in allowed:
                U = set(span(FULL9))
                for r in regs:
                    U.intersection_update(span(upper[nxt[k, r]]))
                for r in regs:
                    if r in caps and nodes[nxt[k, r]][2] in ('tail', 'end'):
                        U.intersection_update(span(caps[r]))
                upper[k] = basis(tuple(U))
                if not leq(lower[k], upper[k]):
                    raise Infeasible(('L not inside U at mutable vertex', k, sec, idx))
            else:
                upper[k] = F0
                if not leq(lower[k], F0):
                    raise Infeasible(('fixed vertex below its forced lower frame', k, sec, idx))
                for r in regs:
                    if (k, r) in nxt and not leq(F0, upper[nxt[k, r]]):
                        raise Infeasible(('fixed vertex above its successor cap', k, sec, idx))
        self.lower = lower
        self.upper = upper
        nodes = [((regs, lower[k], sec, idx) if (k in allowed and lower[k] == upper[k]) else (regs, F0, sec, idx))
                 for k, (regs, F0, sec, idx) in enumerate(nodes)]
        self.nodes = nodes
        self.var = [k for k in mutable if lower[k] != upper[k]]
        self.varset = set(self.var)
        self.dom = {k: self._domain(k) for k in self.var}
        adj = collections.defaultdict(set)
        for (k, r), j in prev.items():
            if k in self.varset and j in self.varset:
                adj[k].add(j)
                adj[j].add(k)
        comps = []
        remaining = set(self.var)
        while remaining:
            root = min(remaining)
            stack = [root]
            remaining.remove(root)
            comp = []
            while stack:
                k = stack.pop()
                comp.append(k)
                for j in adj[k] & remaining:
                    remaining.remove(j)
                    stack.append(j)
            comps.append(sorted(comp))
        self.components = sorted(comps, key=lambda z: (-len(z), min(z)))

    def _domain(self, k):
        L, U = self.lower[k], self.upper[k]
        extras = []
        current = L
        for v in U:
            if v not in span(current):
                extras.append(v)
                current = basis(tuple(current) + (v,))
        d = len(extras)
        if d > 5:
            raise ValueError(('domain too large', k, d))
        spaces = {()}
        frontier = [()]
        while frontier:
            nxt = []
            for S in frontier:
                sp = set(span(S))
                for v in range(1, 1 << d):
                    if v not in sp:
                        T = basis(S + (v,))
                        if T not in spaces:
                            spaces.add(T)
                            nxt.append(T)
            frontier = nxt

        def lift(v):
            z = 0
            for i, x in enumerate(extras):
                if v >> i & 1:
                    z ^= x
            return z
        return sorted({basis(tuple(L) + tuple(lift(v) for v in S)) for S in spaces})

    def frame(self, assign, k):
        return assign[k] if k in self.varset else self.nodes[k][1]

    def profile(self, assign):
        H_ = collections.Counter()
        for (k, r), j in self.prev.items():
            d = len(self.frame(assign, k)) - len(self.frame(assign, j))
            if d:
                H_[d] += 1
        return H_


def solve_component(g, c, comp, max_tuples=VE_MAX_TUPLES):
    """min-sum variable elimination over one component (frames.solve_component_ve); (cost, assignment) or None"""
    cset = set(comp)
    factors = []
    for (k, r), j in g.prev.items():
        if k in cset and j in cset:
            tab = {}
            for F in g.dom[j]:
                for G in g.dom[k]:
                    if leq(F, G):
                        tab[(F, G)] = c[len(G) - len(F)]
            factors.append(([j, k], tab))
        elif k in cset:
            Fj = g.nodes[j][1]
            factors.append(([k], {(F,): c[len(F) - len(Fj)] for F in g.dom[k]}))
        elif j in cset:
            Fk = g.nodes[k][1]
            factors.append(([j], {(F,): c[len(Fk) - len(F)] for F in g.dom[j]}))
    adj = {k: set() for k in comp}
    for s, _ in factors:
        if len(s) == 2:
            adj[s[0]].add(s[1])
            adj[s[1]].add(s[0])
    gg = {v: set(nb) for v, nb in adj.items()}
    order = []

    def fill(v):
        nb = list(gg[v])
        cnt = 0
        for i in range(len(nb)):
            for j in range(i + 1, len(nb)):
                if nb[j] not in gg[nb[i]]:
                    cnt += 1
        return cnt
    while gg:
        v = min(gg, key=lambda x: (fill(x), len(gg[x]), x))
        nb = list(gg[v])
        for i in range(len(nb)):
            for j in range(i + 1, len(nb)):
                gg[nb[i]].add(nb[j])
                gg[nb[j]].add(nb[i])
        for u in nb:
            gg[u].discard(v)
        del gg[v]
        order.append(v)
    active = [(list(s), dict(f)) for s, f in factors]
    back = []
    for v in order:
        group = [(s, f) for s, f in active if v in s]
        rest = [(s, f) for s, f in active if v not in s]
        cs, cf = list(group[0][0]), dict(group[0][1])
        for s, f in group[1:]:
            common = [x for x in s if x in cs]
            new = [x for x in s if x not in cs]
            idx_s = {x: i for i, x in enumerate(s)}
            idx_c = {x: i for i, x in enumerate(cs)}
            byc = collections.defaultdict(list)
            for key, val in f.items():
                byc[tuple(key[idx_s[x]] for x in common)].append((tuple(key[idx_s[x]] for x in new), val))
            nf = {}
            for key, val in cf.items():
                for nk, nv in byc.get(tuple(key[idx_c[x]] for x in common), ()):
                    nf[key + nk] = val + nv
            cs, cf = cs + new, nf
            if len(cf) > max_tuples:
                return None
        vi = cs.index(v)
        ns = cs[:vi] + cs[vi + 1:]
        best = {}
        arg = {}
        for key, val in cf.items():
            ctx = key[:vi] + key[vi + 1:]
            if ctx not in best or val < best[ctx]:
                best[ctx] = val
                arg[ctx] = key[vi]
        back.append((v, ns, arg))
        active = rest + ([(ns, best)] if ns else [([], {(): min(best.values())})])
    total = sum(f.get((), 0) for s, f in active if not s)
    assign = {}
    for v, ns, arg in reversed(back):
        assign[v] = arg[tuple(assign[x] for x in ns)]
    return total, assign


def optimal_frames(g, c=None):
    """exact optimum of the frame graph: exhaustive elimination per component plus fixed boundary edges"""
    c = c or weights()
    assign = {}
    total = 0
    for comp in g.components:
        res = solve_component(g, c, comp) if len(comp) <= VE_MAX_COMPONENT else None
        if res is None:
            raise ValueError(('component too wide for exact elimination', len(comp)))
        cost, a = res
        assign.update(a)
        total += cost
    fixed = 0
    for (k, r), j in g.prev.items():
        if k not in g.varset and j not in g.varset:
            fixed += c[len(g.nodes[k][1]) - len(g.nodes[j][1])]
    prof = g.profile(assign)
    cost = total + fixed
    if cost != profile_cost(prof, c):
        raise ValueError('component accounting mismatch')
    for (k, r), j in g.prev.items():
        if not leq(g.frame(assign, j), g.frame(assign, k)):
            raise ValueError('returned assignment is not nested')
    return dict(cost=cost, profile=prof, assign=assign)


def frame_optimum(w, caps=None):
    """certified-model optimum of a BORROW-WORD; caps: {original register: cap frame at its last vertex before its end}"""
    w2, meta = build_problem(w)
    vcaps = {}
    if caps:
        al = aliases(w, meta)
        vcaps = {al[r][-1]: basis(tuple(U)) for r, U in caps.items()}
    g = FrameGraph(w2, meta['eq_end'], caps=vcaps)
    res = optimal_frames(g)
    cd = centre_descents(w)
    prof = collections.Counter(res['profile'])
    prof.update(cd)
    return dict(cost=res['cost'] + profile_cost(cd), profile=dict(sorted(prof.items())), graph=g, meta=meta,
                assign=res['assign'], variables=len(g.var), components=len(g.components),
                largest_component=max((len(x) for x in g.components), default=0))
