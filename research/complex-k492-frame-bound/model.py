"""Exact fixed-order frame model of one emitted complex provider program (standard library only).

Prepared for the CrocSwap integer-mult-bounds sprint with substantial AI assistance (Anthropic Claude). Apache-2.0.

Input: CANONICAL-WORD.json.gz and LOCAL-PROGRAMS.json.gz written by
research/complex-k492-owner-repair (hpe_emit_local.py). The emitted program is the
object audited by that package's hpe_audit_local.py, whose frame rules are:
  * an L-register operand of a scalar macro is exactly at the macro frame;
  * frames change only through climb events, which are strictly nested;
  * a private C register keeps one frame between centre events;
  * targets sit at their levels when phase 'centers' opens; every register sits at
    its final frame when 'full_frame_cleanup' opens; starts are fixed.
Class: every scalar macro of phases A and B may take any frame; the frames of all
other macros, all start/final frames, target levels and private-centre frames stay
fixed, as do the macro list, order and operands. Climbs are then determined.
"""
import gzip, hashlib, itertools, json
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

H = 9
FREE_PHASES = ('A', 'B')


def basis(vs):
    b = {}
    for x in vs:
        for p in sorted(b, reverse=True):
            if x >> p & 1: x ^= b[p]
        if x:
            p = x.bit_length() - 1
            for q in list(b):
                if b[q] >> p & 1: b[q] ^= x
            b[p] = x
    return tuple(b[p] for p in sorted(b, reverse=True))


def contains(A, B):
    """B is a subspace of A (both reduced bases)"""
    return len(basis(list(A) + list(B))) == len(A)


@lru_cache(None)
def perp(U):
    return basis([z for z in range(1, 1 << H) if all(not (z & u).bit_count() % 2 for u in U)])


@lru_cache(None)
def meet(A, B):
    return perp(basis(list(perp(tuple(A))) + list(perp(tuple(B)))))


def payload_sha(path):
    return hashlib.sha256(gzip.decompress(Path(path).read_bytes())).hexdigest()


def load(directory, program):
    d = Path(directory)
    c = json.load(gzip.open(d / 'CANONICAL-WORD.json.gz'))
    ev = json.load(gzip.open(d / 'LOCAL-PROGRAMS.json.gz'))[program]
    return c, ev


def extract(c, events):
    """Replay the emitted program; return frames, macro nodes (ops, pin, baseline frame, phase), climbs, centre steps."""
    v, R = c['v'], c['R']; n = 2 * v + R
    F = [basis(f) for f in c['frames']]
    levels = {int(t): F[f] for t, f in c.get('target_levels', {}).items()}
    cur = [F[f] for f in c['start']]
    nodes = []; climbs = defaultdict(list); center = Counter(); private = {}; phase = None
    for e in events:
        tag = e[0]
        if tag == 'phase':
            phase = e[1]
            if phase == 'centers':
                for t in range(v): nodes.append(((v + t,), levels.get(t, ()), cur[v + t], 'pin:centers'))
            if phase == 'full_frame_cleanup':
                for r in range(n): nodes.append(((r,), F[c['final'][r]], cur[r], 'pin:final'))
        elif tag == 'climb':
            _, part, r, a, b, rank = e
            assert cur[r] == F[a] and contains(F[b], F[a]) and len(F[b]) - len(F[a]) == rank > 0
            climbs[r].append(rank); cur[r] = F[b]
        elif tag == 'center':
            _, k, a, b, rank = e
            assert rank == abs(len(F[a]) - len(F[b])) > 0
            private[('C', k)] = F[b]; center[rank] += 1
        elif tag == 'scalar':
            _, op, f = e; f = F[f]
            regs = [tuple(op[1])] + ([tuple(op[2])] if op[0] in ('add', 'copy') else [])
            ops = tuple(r[1] for r in regs if r[0] == 'L'); pin = None
            for r in regs:
                if r[0] == 'C':
                    if op[0] == 'clear': private.pop(r, None); continue
                    private.setdefault(r, f); assert private[r] == f; pin = f
            for r in ops: assert cur[r] == f
            if phase not in FREE_PHASES: pin = f
            if ops: nodes.append((ops, pin, f, phase))
        elif tag in ('adapter', 'residual_adapter'):
            pass                     # boundary wrappers: frame-independent of macro frames, unchanged
        else:
            raise AssertionError(tag)
    assert all(cur[r] == F[c['final'][r]] for r in range(n))
    return F, nodes, climbs, center


def chains(c, nodes):
    n = 2 * c['v'] + c['R']; seq = defaultdict(list)
    for i, nd in enumerate(nodes):
        for r in nd[0]: seq[r].append(i)
    return [seq[r] for r in range(n)]


def intervals(c, F, nodes):
    """lo_i (forward joins) and hi_i (backward meets): every legal assignment has lo_i <= G_i <= hi_i."""
    low = [F[f] for f in c['start']]; lo = []
    for ops, pin, f, ph in nodes:
        L = basis([x for r in ops for x in low[r]])
        if pin is not None: assert contains(pin, L); L = pin
        for r in ops: low[r] = L
        lo.append(L)
    up = [F[f] for f in c['final']]; hi = [None] * len(nodes)
    for i in range(len(nodes) - 1, -1, -1):
        ops, pin, f, ph = nodes[i]; U = up[ops[0]]
        for r in ops[1:]: U = meet(U, up[r])
        if pin is not None: assert contains(U, pin); U = pin
        for r in ops: up[r] = U
        hi[i] = U
    for i, nd in enumerate(nodes):
        assert contains(nd[2], lo[i]) and contains(hi[i], nd[2])
    return lo, hi


def between(L, U):
    """every subspace G with L <= G <= U (lift of all subspaces of the quotient U/L)"""
    comp = []
    for x in U:
        if not contains(basis(list(L) + comp), (x,)): comp.append(x)
    g = len(comp); assert g <= 3
    def lift(s):
        z = 0
        for j in range(g):
            if s >> j & 1: z ^= comp[j]
        return z
    out = {basis(list(L) + [lift(s) for s in sub]) for sub in itertools.product(range(1 << g), repeat=g)}
    return sorted(out, key=lambda b: (len(b), b))


def profile(c, F, nodes, frames):
    """paid L-register climbs implied by a frame assignment, with full legality check"""
    n = 2 * c['v'] + c['R']; cur = [F[x] for x in c['start']]; Hc = Counter()
    for i, nd in enumerate(nodes):
        G = frames[i]
        if nd[1] is not None: assert G == nd[1]
        for r in nd[0]:
            assert contains(G, cur[r]), ('not nested', i, r)
            k = len(G) - len(cur[r])
            if k: Hc[k] += 1
            cur[r] = G
    for r in range(n):
        fin = F[c['final'][r]]; assert contains(fin, cur[r]); k = len(fin) - len(cur[r])
        if k: Hc[k] += 1
    return Hc


def vec(k, mult=1):
    """symbolic cost: coefficient vector over C_2..C_9 (C_0 = C_1 = 0)"""
    v = [0] * 8
    if k >= 2: v[k - 2] = mult
    return tuple(v)


def add(a, b): return tuple(x + y for x, y in zip(a, b))


ZERO = (0,) * 8


def lp(c, F, nodes, lo, hi):
    """Local-polytope LP of the exact model, split into independent components.

    Vertices: free macros (lo < hi). Edges: consecutive macros on a register (with
    multiplicity). Columns: x(i,G) for G in [lo_i,hi_i]; y(e,G,G') for nested pairs.
    Rows: sum_G x(i,G) = 1 and both marginal equalities of every free-free edge.
    Costs are symbolic vectors over C_2..C_9. Every legal assignment is a 0/1 point.
    Returns components, the constant symbolic cost and the baseline symbolic cost.
    """
    n = 2 * c['v'] + c['R']; seq = chains(c, nodes)
    free = {i for i, nd in enumerate(nodes) if nd[1] is None and len(lo[i]) < len(hi[i])}
    dom = {i: between(lo[i], hi[i]) for i in free}
    for i in free: assert nodes[i][2] in dom[i]
    edges = Counter(); unary = defaultdict(lambda: ZERO); const = ZERO; base = ZERO
    def frame(tag, x):
        return F[c['start'][x]] if tag == 'S' else F[c['final'][x]] if tag == 'E' else nodes[x][2]
    for r in range(n):
        ch = [('S', r)] + [('N', i) for i in seq[r]] + [('E', r)]
        for (ta, a), (tb, b) in zip(ch, ch[1:]):
            fa, fb = frame(ta, a), frame(tb, b)
            base = add(base, vec(len(fb) - len(fa)))
            va, vb = ta == 'N' and a in free, tb == 'N' and b in free
            if va and vb: edges[(a, b)] += 1
            elif va:
                for G in dom[a]: unary[(a, G)] = add(unary[(a, G)], vec(len(fb) - len(G)))
            elif vb:
                for G in dom[b]: unary[(b, G)] = add(unary[(b, G)], vec(len(G) - len(fa)))
            else:
                const = add(const, vec(len(fb) - len(fa)))
    parent = {i: i for i in free}
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, b in edges: parent[find(a)] = find(b)
    groups = defaultdict(list)
    for i in free: groups[find(i)].append(i)
    comps = []
    for key in sorted(groups, key=lambda k: min(groups[k])):
        vs = sorted(groups[key]); S = set(vs)
        cols = []; rows = []                 # cols: (name, cost, [(row, coef)]); rows: rhs
        xid = {}
        for i in vs:
            r0 = len(rows); rows.append(1)
            for G in dom[i]:
                xid[(i, G)] = len(cols); cols.append([('x', i, G), unary[(i, G)], [(r0, 1)]])
        for (a, b), m in sorted(edges.items()):
            if a not in S: continue
            ra = {G: len(rows) + j for j, G in enumerate(dom[a])}; rows += [0] * len(dom[a])
            rb = {G: len(rows) + j for j, G in enumerate(dom[b])}; rows += [0] * len(dom[b])
            for G in dom[a]: cols[xid[(a, G)]][2].append((ra[G], -1))
            for G2 in dom[b]: cols[xid[(b, G2)]][2].append((rb[G2], -1))
            for G in dom[a]:
                for G2 in dom[b]:
                    if contains(G2, G):
                        cols.append([('y', (a, b), (G, G2)), vec(len(G2) - len(G), m), [(ra[G], 1), (rb[G2], 1)]])
        comps.append({'nodes': vs, 'domains': {i: dom[i] for i in vs}, 'cols': cols, 'rhs': rows,
                      'edges': {e: m for e, m in edges.items() if e[0] in S}})
    return comps, const, base, free
