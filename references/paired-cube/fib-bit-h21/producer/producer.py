"""Lane C best producer (variant c_p1a12): a_b_shared 1.26225e-04, a_b 1.21545e-04 under harness/evaluate_ab.py --shared
(bitcomp md5 b9a99aca). Self-contained copy of lanes/C/cprod.py (lane B's native PR #62 rebuild plus lane C
options) with the CFG overrides at the bottom.
"""
"""Lane B: round seven's lineage (PR #62 interval strips + core-aware pair assembly, PR #41 alternating order),
rebuilt natively on the harness circuit so that variants can be explored.

Local pair circuit on n = h-1 points (inputs = pairs); global node for common point c maps pair (a,b) to triple
{c, P_c[a], P_c[b]}. Equal global supports are interned by the harness (pair-star merging across common points).
"""
from itertools import combinations
import os

H = int(os.environ.get('BIT_H', 23))
CFG = dict(
    balanced_coarse=int(os.environ.get('B_BAL', 0)),
    total_order='nat',          # rev | sortdesc | sortasc | nat
    top_layout='rev_interval',  # rev_interval | interval | sorted+ | sorted- | skip | ps | rev_skip
    deep_layout='sorted+',
    point_order='cyc_C_rel',    # alt | nat | alt_norev | cyc_<A|B|C>_<rel|abs|none> (cyclic triple packing on Z_23)
    assembly='core',            # core | plain (used only when asm specs are absent)
    top_groups='split_last',    # split the last top-level group into two singletons
    # pair assembly per level (level 0, levels >= 1) for out[a,b], out[a,b2], out[a2,b], out[a2,b2]:
    # Y: e + (FS + S); E: (FS + e) + S; T: FS + (S + e)  (S + e is a saturated pair-star)
    asm0=['Yi', 'Yj', 'Tj', 'Ti'],
    asm1=['Yi', 'Tj', 'Tj', 'Ei'],
    coarse_mode='perm0123',     # level-0 coarse 4-edge sum chained e(a,b), e(a,b2), e(a2,b), e(a2,b2)
    coarse_mode1='perm3012',    # levels >= 1: e(a2,b2) + e(a,b) first (diagonal), then e(a,b2), e(a2,b)
    cyc_base=((0, 1, 11), (0, 2, 9), (0, 3, 8)),   # cyclic triple packing on Z_23 (69 blocks)
    cyc_leave=(4, 6),           # leave differences; c+-4, c+-6 paired as {c+4,c-6}, {c-4,c+6} (mode C)
)


class Local:
    """Pair circuit with interning by local support (pairs of n points)."""

    def __init__(self, n, h):
        self.n, self.h = n, h
        self.inputs = list(combinations(range(n), 2))
        self.var = {p: i + 1 for i, p in enumerate(self.inputs)}
        self.support = [0] + [1 << i for i in range(len(self.inputs))]
        self.args = [None] * len(self.support)
        self.lookup = {s: i for i, s in enumerate(self.support)}
        self._level = -1
        self.cur = 'input'
        self.tag = ['input'] * len(self.support)

    glookup = None

    def gsup(self, x):
        s, g = self.support[x], 0
        while s:
            low = s & -s
            g |= self.bitmap[low.bit_length() - 1]
            s ^= low
        return g

    def add(self, a, b):
        if not a:
            return b
        if not b:
            return a
        assert not self.support[a] & self.support[b]
        s = self.support[a] | self.support[b]
        if s in self.lookup:
            return self.lookup[s]
        x = len(self.support)
        self.lookup[s] = x
        self.support.append(s)
        self.args.append((a, b))
        self.tag.append(self.cur)
        return x

    def total(self, values):
        values = [x for x in values if x]
        o = CFG['total_order']
        if o == 'rev':
            values.reverse()
        elif o == 'sortdesc':
            values.sort(key=lambda x: (self.support[x].bit_count(), self.support[x]), reverse=True)
        elif o == 'sortasc':
            values.sort(key=lambda x: (self.support[x].bit_count(), self.support[x]))
        r = 0
        for x in values:
            r = self.add(r, x)
        return r


def prefix_suffix(c, vals):
    n = len(vals)
    prefix = [0]
    for x in vals:
        prefix.append(c.add(prefix[-1], x))
    suffix = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix[i] = c.add(vals[i], suffix[i + 1])
    return prefix[-1], [c.add(prefix[i], suffix[i + 1]) for i in range(n)]


def skip_prefix(c, vals):
    k = len(vals)
    if k <= 2:
        return prefix_suffix(c, vals)
    v = [0] + list(vals)
    A = [0] * (k + 1)
    for i in range(1, k):
        A[i] = c.add(A[i - 1], v[i])
    B = [0] * (k + 2)
    for i in range(k, 1, -1):
        B[i] = c.add(v[i], B[i + 1])
    out = [0] * (k + 1)
    out[1] = B[2]
    for j in range(2, k + 1):
        out[j] = c.add(A[j - 2], c.add(v[j - 1], B[j + 1]))
    return c.add(A[k - 1], v[k]), out[1:]


def interval_splits(k):
    full = (1 << k) - 1
    interval = lambda a, m: sum(1 << ((a + t) % k) for t in range(m))
    splits = [(interval(a, m), interval(a, m - 1), 1 << ((a + m - 1) % k))
              for m in range(2, k) for a in range(k)]
    return splits + [(full, interval(0, k - 1), 1 << (k - 1))]


def interval_layout(fallback):
    def apply(c, vals):
        k = len(vals)
        if k < 3:
            return fallback(c, vals)
        node = {1 << i: x for i, x in enumerate(vals)}
        for S, L, R in interval_splits(k):
            node[S] = c.add(node[L], node[R])
        full = (1 << k) - 1
        return node[full], [node[full ^ (1 << j)] for j in range(k)]
    return apply


def reversed_layout(layout):
    def apply(c, vals):
        total, out = layout(c, list(vals)[::-1])
        return total, out[::-1]
    return apply


def sorted_layout(layout, sign):
    def apply(c, vals):
        order = sorted(range(len(vals)), key=lambda i: (c.support[vals[i]].bit_count(), sign * c.support[vals[i]]))
        total, out = layout(c, [vals[i] for i in order])
        restored = [0] * len(vals)
        for position, original in enumerate(order):
            restored[original] = out[position]
        return total, restored
    return apply


def leave_one_out(c, values, layout):
    values = list(values)
    nonzero = [i for i, x in enumerate(values) if x]
    if not nonzero:
        return 0, [0] * len(values)
    if len(nonzero) == 1:
        x = values[nonzero[0]]
        return x, [0 if i in nonzero else x for i in range(len(values))]
    total, out = layout(c, [values[i] for i in nonzero])
    result = [total] * len(values)
    for i, x in zip(nonzero, out):
        result[i] = x
    return total, result


def base_block(c, points, edges, weights):
    def tot(omit):
        return c.total([x for p, x in edges.items() if not set(p) & set(omit)] +
                       [x for p, x in weights.items() if p not in omit])
    return tot(()), {a: tot((a,)) for a in points}, {(a, b): tot((a, b)) for a, b in combinations(points, 2)}


def block_layout(inner, size=2, sib_first=False):
    """two-level leave-one-out: consecutive blocks of `size` items, LOO over the block sums by `inner`, then
    LOO_j = blockLOO[block(j)] + (the other items of j's block)."""
    def apply(c, vals):
        k = len(vals)
        if k < 2 * size:
            return inner(c, vals)
        blocks = [list(range(i, min(i + size, k))) for i in range(0, k, size)]
        bsum = []
        for blk in blocks:
            r = 0
            for t in blk:
                r = c.add(r, vals[t])
            bsum.append(r)
        btot, bloo = inner(c, bsum)
        out = [0] * k
        for bi, blk in enumerate(blocks):
            for idx in blk:
                r = bloo[bi]
                for t in blk:
                    if t != idx:
                        r = c.add(vals[t], r) if sib_first else c.add(r, vals[t])
                out[idx] = r
        return btot, out
    return apply



def parse_plan(spec):
    """'2:1,3:1,5:3' -> [(2,1),(3,1),(5,3)]: interval of length L = I(s, La) + I(s + La, L - La)."""
    return [tuple(int(x) for x in t.split(':')) for t in spec.split(',') if t]


def fib_layout(plans, fallback):
    """cyclic-interval strips: for k items, every needed length L = La + (L - La) at all k starts (two-use chains);
    LOO output j = I(j + 1, k - 1); total = I(0, k - 1) + item k - 1. plans: {k: [(L, La), ...]} ending at k - 1."""
    def apply(c, vals):
        k = len(vals)
        plan = plans.get(k)
        if k < 3 or plan is None:
            return fallback(c, vals)
        I = {(s, 1): vals[s] for s in range(k)}
        for L, La in plan:
            for s in range(k):
                I[s, L] = c.add(I[s, La], I[(s + La) % k, L - La])
        out = [I[(j + 1) % k, k - 1] for j in range(k)]
        return c.add(I[0, k - 1], vals[k - 1]), out
    return apply


def env_plans(var):
    """FIB0='10=2:1,3:1,6:3,9:6;9=...' -> {k: plan}"""
    spec = os.environ.get(var, '')
    out = {}
    for part in spec.split(';'):
        if part:
            k, pl = part.split('=')
            out[int(k)] = parse_plan(pl)
    return out


def get_layout(name):
    if name.startswith('blk'):          # blk<size>[s]_<inner>
        head, inner = name.split('_', 1)
        sib_first = head.endswith('s')
        size = int(head[3:].rstrip('s'))
        return block_layout(get_layout(inner), size, sib_first)
    if name.startswith('fib'):          # fib<level>: plans from env FIB<level>, else rev_interval / sorted+
        base = dict(fib0=reversed_layout(interval_layout(skip_prefix)),
                    fib1=sorted_layout(interval_layout(skip_prefix), 1))[name]
        return fib_layout(env_plans('FIB' + name[3:]), base)
    return dict(rev_interval=reversed_layout(interval_layout(skip_prefix)),
                interval=interval_layout(skip_prefix),
                **{'sorted+': sorted_layout(interval_layout(skip_prefix), 1),
                   'sorted-': sorted_layout(interval_layout(skip_prefix), -1)},
                skip=skip_prefix, rev_skip=reversed_layout(skip_prefix), ps=prefix_suffix)[name]


def make_block(h, cfg):
    top = get_layout(cfg['top_layout'])
    deep = get_layout(cfg['deep_layout'])

    def block(c, points, edges, weights, level):
        if len(points) <= 2:
            c.cur = 'base%d' % level
            return base_block(c, points, edges, weights)
        layout = top if level == 0 else deep
        groups = [points[i:i + 2] for i in range(0, len(points), 2)]
        if level == 0 and cfg.get('top_groups') == 'split_last':
            groups = groups[:-1] + [[x] for x in groups[-1]]
        elif level == 0 and cfg.get('top_groups') == 'split_last_rev':
            groups = groups[:-1] + [[x] for x in groups[-1][::-1]]
        elif level == 0 and cfg.get('top_groups') == 'triples_last':
            groups = groups[:-2] + [groups[-2] + groups[-1][:1], groups[-1][1:]]
        ng = len(groups)
        e = lambda a, b: edges[tuple(sorted((a, b)))]
        c.cur = 'coarse%d' % level
        cm = cfg.get('coarse_mode', 'chain') if level == 0 else cfg.get('coarse_mode1', cfg.get('coarse_mode', 'chain'))
        if cm == 'rows':
            coarse = {(i, j): c.total([c.total([e(a, b) for b in groups[j]]) for a in groups[i]])
                      for i, j in combinations(range(ng), 2)}
        elif cm.startswith('perm'):
            pm = [int(ch) for ch in cm[4:]]
            def coarse_sum(i, j):
                es = [e(a, b) for a in groups[i] for b in groups[j]]
                es = [es[p] for p in pm if p < len(es)] if len(es) == 4 else es
                r = 0
                for x in es:
                    r = c.add(r, x)
                return r
            coarse = {(i, j): coarse_sum(i, j) for i, j in combinations(range(ng), 2)}
        elif cfg['balanced_coarse']:
            def coarse_sum(i, j):
                return c.total([c.total([e(a, b) for a in groups[i]]) for b in groups[j]])
            coarse = {(i, j): coarse_sum(i, j) for i, j in combinations(range(ng), 2)}
        else:
            coarse = {(i, j): c.total([e(a, b) for a in groups[i] for b in groups[j]])
                      for i, j in combinations(range(ng), 2)}
        c.cur = 'wt%d' % level
        wt = {i: c.total([weights[a] for a in g] + [e(a, b) for a, b in combinations(g, 2)])
              for i, g in enumerate(groups)}
        total, outside, far = block(c, list(range(ng)), coarse, wt, level + 1)
        strips, sums = {}, {}
        for i, g in enumerate(groups):
            other = [j for j in range(ng) if j != i]
            for a in g:
                c.cur = 'carry%d' % level
                carry = c.total([weights[u] for u in g if u != a])
                c.cur = 'vals%d' % level
                vals = [c.total([e(u, v) for u in g if u != a for v in groups[j]]) for j in other]
                c.cur = 'loo%d' % level
                st, one = leave_one_out(c, [carry] + vals, layout)
                strips[a] = {j: z for j, z in zip(other, one[1:])}
                sums[a] = st
        out = {}
        c.cur = 'single%d' % level
        single = {a: c.add(outside[i], sums[a]) for i, g in enumerate(groups) for a in g}
        for i, g in enumerate(groups):
            for a, b in combinations(g, 2):
                out[a, b] = outside[i]
        for i, j in combinations(range(ng), 2):
            spec = cfg.get('asm%d' % min(level, 1))
            if spec and len(groups[i]) == 2 and len(groups[j]) == 2:
                (a, a2), (b, b2) = groups[i], groups[j]
                F = far[i, j]
                part = {a: a2, a2: a, b: b2, b2: b}
                S = {a: strips[a][j], a2: strips[a2][j], b: strips[b][i], b2: strips[b2][i]}
                FS = {}
                def fs(x):
                    c.cur = 'FS%d' % level
                    if x not in FS:
                        FS[x] = c.add(F, S[x])
                    return FS[x]
                order = [(a, b), (a, b2), (a2, b), (a2, b2)]
                for k in cfg.get('asm_order', (0, 1, 2, 3)):
                    x, y = order[k]
                    ch = spec[k]
                    ee = e(part[x], part[y])
                    if level == 0 and getattr(c, 'glookup', None) is not None:
                        gi = c.gsup(S[x]) | c.gsup(ee)
                        gj = c.gsup(S[y]) | c.gsup(ee)
                        if gi in c.glookup:
                            ch = 'Ti'
                        elif gj in c.glookup:
                            ch = 'Tj'
                    if ch == 'Yi':
                        fy = fs(y); c.cur = 'Y%d' % level; m = c.add(fy, S[x]); c.cur = 'pout%d' % level
                        out[x, y] = c.add(ee, m)
                    elif ch == 'Yj':
                        fx = fs(x); c.cur = 'Y%d' % level; m = c.add(fx, S[y]); c.cur = 'pout%d' % level
                        out[x, y] = c.add(ee, m)
                    elif ch == 'Ei':
                        fy = fs(y); c.cur = 'Y%d' % level; m = c.add(fy, ee); c.cur = 'pout%d' % level
                        out[x, y] = c.add(m, S[x])
                    elif ch == 'Ej':
                        fx = fs(x); c.cur = 'Y%d' % level; m = c.add(fx, ee); c.cur = 'pout%d' % level
                        out[x, y] = c.add(m, S[y])
                    elif ch == 'Ti':
                        fy = fs(y); c.cur = 'T%d' % level; m = c.add(S[x], ee); c.cur = 'pout%d' % level
                        out[x, y] = c.add(fy, m)
                    elif ch == 'Tj':
                        fx = fs(x); c.cur = 'T%d' % level; m = c.add(S[y], ee); c.cur = 'pout%d' % level
                        out[x, y] = c.add(fx, m)
                continue
            amode = cfg.get('assembly1', cfg['assembly']) if level >= 1 else cfg['assembly']
            if amode == 'core' and len(groups[i]) == 2 and len(groups[j]) == 2:
                (a, a2), (b, b2) = groups[i], groups[j]
                F = far[i, j]
                Sa, Sa2, Sb, Sb2 = strips[a][j], strips[a2][j], strips[b][i], strips[b2][i]
                c.cur = 'FS%d' % level
                FSa, FSa2 = c.add(F, Sa), c.add(F, Sa2)
                FSb, FSb2 = c.add(F, Sb), c.add(F, Sb2)
                c.cur = 'Y%d' % level
                Y1 = c.add(FSb, Sa)
                Y2 = c.add(FSa, Sb2)
                Y3 = c.add(FSa2, e(a, b2))
                Y4 = c.add(FSb2, e(a, b))
                c.cur = 'pout%d' % level
                out[a, b] = c.add(e(a2, b2), Y1)
                out[a, b2] = c.add(e(a2, b), Y2)
                out[a2, b] = c.add(Y3, Sb)
                out[a2, b2] = c.add(Y4, Sa2)
                continue
            c.cur = 'odd%d' % level
            for a in groups[i]:
                left = c.add(far[i, j], strips[a][j])
                for b in groups[j]:
                    cross = c.total([e(u, v) for u in groups[i] if u != a for v in groups[j] if v != b])
                    out[a, b] = c.add(left, c.add(strips[b][i], cross))
        return total, single, out
    return block


def cyclic_points(h, c, base=((0, 1, 3), (0, 4, 9), (0, 6, 13)), leave=(8, 11), mode='A', gorder='rel'):
    """Pairs of [h]-c from a cyclic triple packing on Z_h: block pairs {x, y} with {c, x, y} a block, then the
    leave neighbours c+-d1, c+-d2 paired by mode."""
    pairs = []
    for blk in base:
        for k in blk:
            i = (c - k) % h
            pts = sorted(((i + t) % h for t in blk if (i + t) % h != c))
            pairs.append(tuple(pts))
    d1, d2 = leave
    L = {'A': [((c + d1) % h, (c - d1) % h), ((c + d2) % h, (c - d2) % h)],
         'B': [((c + d1) % h, (c + d2) % h), ((c - d1) % h, (c - d2) % h)],
         'C': [((c + d1) % h, (c - d2) % h), ((c - d1) % h, (c + d2) % h)]}[mode]
    assert len(set(x for p in pairs + L for x in p)) == h - 1
    if gorder == 'rel':
        pairs.sort(key=lambda p: sorted((x - c) % h for x in p))
    elif gorder == 'abs':
        pairs.sort()
    return [x for p in pairs + L for x in p]


def alternating_points(h, common):
    if CFG['point_order'].startswith('cyc'):
        _, mode, gorder = CFG['point_order'].split('_')
        if 'cyc_base' in CFG:
            return cyclic_points(h, common, base=CFG['cyc_base'], leave=CFG['cyc_leave'], mode=mode, gorder=gorder)
        return cyclic_points(h, common, mode=mode, gorder=gorder)
    if CFG['point_order'] == 'nat':
        return [x for x in range(h) if x != common]
    po = CFG['point_order']
    pairs = [(a, a + 1) for a in range(0, h - 1, 2) if common not in (a, a + 1)]
    if common % 2 and po in ('alt', 'alt_sfirst', 'alt_swin'):
        pairs.reverse()
    if po == 'alt_swin' and common % 2:          # odd circuits also swap the two points of every pair
        pairs = [(b, a) for a, b in pairs]
    head = [x for pair in pairs for x in pair]
    tail = [x for x in range(h) if x != common and x not in head]
    if po == 'alt_sfirst':                       # the special group {partner(c), h-1} first
        return tail + head
    return head + tail


def local_circuit(h, cfg, L=None):
    n = h - 1
    L = L or Local(n, h)
    block = make_block(h, cfg)
    pts = list(range(n))
    total, _, two = block(L, pts, {p: L.var[p] for p in combinations(pts, 2)}, {a: 0 for a in pts}, 0)
    outputs = dict(two)
    outputs[()] = total
    active = set()
    stack = list(outputs.values())
    while stack:
        x = stack.pop()
        if not x or x in active:
            continue
        active.add(x)
        if L.args[x]:
            stack.extend(L.args[x])
    return L, outputs, active


PROV = {}
LOCAL = []


def build_side(C, h):
    if CFG.get('adaptive_T'):
        return build_side_adaptive(C, h)
    L, outputs, active = local_circuit(h, CFG)
    LOCAL[:] = [L, outputs, active]
    out, ret = {}, {}
    swap = CFG.get('swap', 0)
    flip = set(CFG.get('swap_flip', ()))       # local tags whose operand order is flipped relative to `swap`
    # pass structure: 'two_pass' creates the total's (retained) ancestry for every common point first
    passes = [sorted(active)]
    if CFG.get('two_pass'):
        anc, st = set(), [outputs[()]]
        while st:
            x = st.pop()
            if x and x not in anc:
                anc.add(x)
                if L.args[x]:
                    st.extend(L.args[x])
        passes = [sorted(anc), sorted(active - anc)]
    ms = {common: {} for common in range(h)}
    Ps = {common: alternating_points(h, common) for common in range(h)}
    loop = CFG.get('loop', 'circuit')          # circuit | circuit_rev | node (each local node for every circuit)
    commons = list(range(h))[::-1] if loop == 'circuit_rev' else list(range(h))

    def make(common, x):
        P, m = Ps[common], ms[common]
        if L.args[x] is None:
            a, b = L.inputs[x - 1]
            m[x] = C.inputs[tuple(sorted((common, P[a], P[b])))]
        else:
            a, b = m[L.args[x][0]], m[L.args[x][1]]
            m[x] = C.add(b, a) if swap ^ (L.tag[x] in flip) else C.add(a, b)
            PROV.setdefault(m[x], (common, x))
            GTAG.setdefault(m[x], L.tag[x])
    for nodes in passes:
        if loop == 'node':
            for x in nodes:
                for common in commons:
                    make(common, x)
        else:
            for common in commons:
                for x in nodes:
                    make(common, x)
    for common in range(h):
        P, m = Ps[common], ms[common]
        for pair, x in outputs.items():
            if pair:
                T = tuple(sorted((common, P[pair[0]], P[pair[1]])))
                out[(common, T)] = m[x]
            else:
                ret[common] = m[x]
    return dict(out=out, ret=ret)


TAG = {}
GTAG = {}


def build_side_adaptive(C, h):
    """Per-circuit construction: an output uses a saturated pair-star T node on whichever side already exists
    globally (built by an earlier circuit), so block-consistent pairings share their T pieces."""
    out, ret = {}, {}
    for common in range(h):
        P = alternating_points(h, common)
        L = Local(h - 1, h)
        L.bitmap = [1 << C.tindex[tuple(sorted((common, P[a], P[b])))] for a, b in L.inputs]
        L.glookup = C.lookup
        L, outputs, active = local_circuit(h, CFG, L)
        LOCAL[:] = [L, outputs, active]
        m = {}
        for x in sorted(active):
            if L.args[x] is None:
                a, b = L.inputs[x - 1]
                m[x] = C.inputs[tuple(sorted((common, P[a], P[b])))]
            else:
                m[x] = C.add(m[L.args[x][0]], m[L.args[x][1]])
                PROV.setdefault(m[x], (common, x))
                TAG.setdefault(m[x], L.tag[x])
        for pair, x in outputs.items():
            if pair:
                T = tuple(sorted((common, P[pair[0]], P[pair[1]])))
                out[(common, T)] = m[x]
            else:
                ret[common] = m[x]
    return dict(out=out, ret=ret)


# lane C best configuration
CFG.update({'total_order': 'nat', 'top_layout': 'rev_interval', 'deep_layout': 'sorted+', 'point_order': 'alt', 'assembly': 'core', 'top_groups': None, 'asm0': None, 'asm1': None, 'coarse_mode': 'chain', 'coarse_mode1': 'perm2301', 'swap': 1, 'swap_flip': ['pout1', 'Y1', 'FS1', 'pout2', 'Y2', 'FS2']})

CFG.update(top_layout='fib0', deep_layout='fib1')
