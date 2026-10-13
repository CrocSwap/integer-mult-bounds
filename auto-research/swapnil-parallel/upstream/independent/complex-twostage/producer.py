"""NStar3: the pair-exclusion complex side producer with retained totals (h even).

An addition circuit over the binomial(h,3) triple inputs x_t. It emits signed pieces (S, node, coef) whose
half-weighted sum, plus the retained-total scatter, is x_S, and retains the h totals
E_i = sum_{t not containing i} x_t (i < h-1) and T = sum_t x_t. Nodes are interned by their support (set of
triples), so an equal sum is never built twice. Structure:
  triple()   recursive triple exclusion over point pairs (groups), giving every 'exclusion' sum
             sum_{t disjoint from S} x_t for |S| <= 3;
  block()    pair-exclusion block (one point excluded, one pair excluded), with an 8-addition 3-point base;
  stars      minus pieces from group-level leave-one-out vectors shared across pairs (two_vec).
Usage: python3 producer.py 24   (prints the circuit size R)"""
import sys
from itertools import combinations
from collections import defaultdict
sys.setrecursionlimit(10000)


class NStar3:
    def __init__(s, h, base=4):
        assert h % 2 == 0 and h >= 8, 'groups are point pairs: h even, h >= 8'
        s.h = h; s.base = base
        s.triples = list(combinations(range(h), 3)); s.tid = {t: i for i, t in enumerate(s.triples)}
        s.sup = [0]; s.args = [None]; s.look = {}            # node 0 is the empty sum; node i+1 is input triple i
        for i, t in enumerate(s.triples): s.sup.append(1 << i); s.args.append(None)
        s.cov = {}; s.pieces = []; s.retained = []; s.twos = {}
        s.top = True
        w = {t: s.tid[t] + 1 for t in s.triples}
        s.results = s.triple(list(range(h)), w)
        for S in s.triples: s.emit(S, s.results[S], 1)
        for i in range(h - 1): s.retained.append((('E', i), s.results[(i,)]))
        s.retained.append((('*',), s.results[()]))
        s.star_pieces()
        s.prune()

    # node store: interned by support; a sum of two nodes must not share triples (no cancellation)
    def add(s, a, b):
        if not a: return b
        if not b: return a
        assert not s.sup[a] & s.sup[b], 'cancellation'
        key = s.sup[a] | s.sup[b]; n = s.look.get(key)
        if n is None:
            n = len(s.sup); s.look[key] = n; s.sup.append(key); s.args.append((a, b))
        return n
    def total(s, vals):
        if not vals: return 0
        if len(vals) == 1: return vals[0]
        k = len(vals) // 2
        return s.add(s.total(vals[:k]), s.total(vals[k:]))
    def vector(s, vals):
        """total and all leave-one-out sums, by prefix/suffix chains."""
        n = len(vals); pre = [0]
        for x in vals: pre.append(s.add(pre[-1], x))
        suf = [0] * (n + 1)
        for i in range(n - 1, -1, -1): suf[i] = s.add(vals[i], suf[i + 1])
        return pre[-1], [s.add(pre[i], suf[i + 1]) for i in range(n)]
    def grouping(s, pts): return [pts[i:i + 2] for i in range(0, len(pts), 2)]
    def x(s, *p): return s.tid[tuple(sorted(p))] + 1

    # pair-exclusion block: total, one point excluded, one pair excluded ---------------------------
    def block(s, points, edges, weights):
        T = s.total; A = s.add
        if len(points) == 3:                       # 8-addition base: the three pair sums share q1, q2, q3
            p1, p2, p3 = points; e = lambda a, b: edges[tuple(sorted((a, b)))]; wt = weights
            q1 = A(e(p2, p3), wt[p2]); q2 = A(e(p1, p3), wt[p3]); q3 = A(e(p1, p2), wt[p1])
            O = {p1: A(q1, wt[p3]), p2: A(q2, wt[p1]), p3: A(q3, wt[p2])}
            tot = A(O[p1], A(q3, e(p1, p3)))
            return tot, O, {(p1, p2): wt[p3], (p1, p3): wt[p2], (p2, p3): wt[p1]}
        if len(points) <= 4:
            tot = lambda om: T([x for p, x in edges.items() if not set(p) & set(om)] + [x for p, x in weights.items() if p not in om])
            return tot(()), {a: tot((a,)) for a in points}, {(a, b): tot((a, b)) for a, b in combinations(points, 2)}
        groups = s.grouping(points); ng = len(groups); e = lambda a, b: edges[tuple(sorted((a, b)))]
        coarse = {(i, j): T([e(a, b) for a in groups[i] for b in groups[j]]) for i, j in combinations(range(ng), 2)}
        wt = {i: T([weights[a] for a in g] + [e(a, b) for a, b in combinations(g, 2)]) for i, g in enumerate(groups)}
        total, outside, far = s.block(list(range(ng)), coarse, wt)
        strips = {}; sums = {}
        for i, g in enumerate(groups):
            other = [j for j in range(ng) if j != i]
            for a in g:
                carry = T([weights[u] for u in g if u != a])
                vals = [T([e(u, v) for u in g if u != a for v in groups[j]]) for j in other]
                st, one = s.vector([carry] + vals)
                strips[a] = {j: z for j, z in zip(other, one[1:])}; sums[a] = st
        out = {}; single = {a: s.add(outside[i], sums[a]) for i, g in enumerate(groups) for a in g}
        for i, g in enumerate(groups):
            for a, b in combinations(g, 2): out[a, b] = outside[i]
        for i, j in combinations(range(ng), 2):
            for a in groups[i]:
                left = s.add(far[i, j], strips[a][j])
                for b in groups[j]:
                    cross = T([e(u, v) for u in groups[i] if u != a for v in groups[j] if v != b])
                    out[a, b] = s.add(left, s.add(strips[b][i], cross))
        return total, single, out

    # recursive triple exclusion ---------------------------------------------------------------------
    def triple(s, pts, w):
        top = s.top; s.top = False
        T = s.total
        subsets = [c for k in range(4) for c in combinations(pts, k)]
        if len(pts) <= s.base:
            return {c: T([v for t, v in w.items() if not set(c) & set(t)]) for c in subsets}
        groups = s.grouping(pts); ng = len(groups)
        gof = {u: i for i, g in enumerate(groups) for u in g}
        cp = defaultdict(list)
        for t, v in w.items(): cp[tuple(sorted({gof[u] for u in t}))].append(v)
        coarse = {c: T(xs) for c, xs in cp.items() if not (top and len(c) == 2)}
        if top:
            # a two-group coarse item is the union of two free star prefixes {u,v,pu},{u,v,pv}
            for (i, j) in [c for c in cp if len(c) == 2]:
                (i0, i1), (j0, j1) = groups[i], groups[j]
                coarse[i, j] = s.add(s.add(s.x(i0, j0, i1), s.x(i0, j0, j1)), s.add(s.x(i1, j1, i0), s.x(i1, j1, j0)))
        oc = s.triple(list(range(ng)), coarse)
        one = {}
        for u in pts:
            g = gof[u]; others = [j for j in range(ng) if j != g]
            pieces = defaultdict(list)
            for t, v in w.items():
                if u not in t: continue
                rest = [a for a in t if a != u]
                if any(gof[a] == g for a in rest): continue
                pieces[tuple(sorted({gof[a] for a in rest}))].append(v)
            coeff = {c: T(xs) for c, xs in pieces.items()}
            edges = {c: coeff.get(c, 0) for c in combinations(others, 2)}
            weights = {j: coeff.get((j,), 0) for j in others}
            tot, single, pair = s.block(others, edges, weights)
            const = coeff.get((), 0)
            one[u] = {(): s.add(const, tot)}
            one[u].update({(j,): s.add(const, x) for j, x in single.items()})
            one[u].update({c: s.add(const, x) for c, x in pair.items()})
        two = {}
        for u, v in combinations(pts, 2):
            i, j = gof[u], gof[v]
            if i == j: continue
            others = [k for k in range(ng) if k not in (i, j)]
            vals = [T([w.get(tuple(sorted((u, v, a))), 0) for a in groups[k]]) for k in others]
            tot, leave = s.vector([w.get((u, v), 0)] + vals)
            two[u, v] = {(): tot} | {(k,): x for k, x in zip(others, leave[1:])}
        res = {}
        for ex in subsets:
            E = set(ex); G = tuple(sorted({gof[a] for a in E}))
            surv = [u for i in G for u in groups[i] if u not in E]
            pc = {(): oc[G]}
            for u in surv: pc[u,] = one[u][tuple(i for i in G if i != gof[u])]
            for u, v in combinations(surv, 2): pc[u, v] = two[u, v][tuple(i for i in G if i not in (gof[u], gof[v]))]
            if len(surv) == 3:
                pc[tuple(surv)] = w.get(tuple(surv), 0)
                a, b, c = surv; order = [(), (a,), (b,), (a, b), (c,), (a, c), (b, c), (a, b, c)]
            else: order = [c for k in range(len(surv) + 1) for c in combinations(surv, k)]
            res[ex] = T([pc[c] for c in order])
        return res

    # minus pieces (pair stars) from shared group-level leave-one-out vectors -----------------------
    def two_vec(s, u, v):
        """leave-one-group-out vector of star(u,v) over groups other than g(u), g(v)."""
        key = (min(u, v), max(u, v))
        if key in s.twos: return s.twos[key]
        h = s.h; ng = (h + 1) // 2
        others = [k for k in range(ng) if k not in (u // 2, v // 2)]
        vals = [s.total([s.x(u, v, a) for a in range(2 * k, min(2 * k + 2, h))]) for k in others]
        tot, leave = s.vector(vals)
        r = {(): tot} | {(k,): x for k, x in zip(others, leave)}
        s.twos[key] = r; return r
    def star_pieces(s):
        # star(u,v) minus {c} = {u,v,c'} + B_k with B_k = two[u,v](k) + PP_uv, shared by {u,v,c} and {u,v,c'}
        h = s.h
        for a, b in combinations(range(h), 2):
            tw = s.two_vec(a, b)
            if a // 2 == b // 2:
                for c in range(h):
                    if c // 2 == a // 2: continue
                    S = tuple(sorted((a, b, c)))
                    s.emit(S, s.x(a, b, c ^ 1), -1); s.emit(S, tw[(c // 2,)], -1)
                continue
            pa, pb = a ^ 1, b ^ 1
            PP = s.add(s.x(a, b, pa), s.x(a, b, pb))
            for c in range(h):
                if c in (a, b): continue
                S = tuple(sorted((a, b, c)))
                if c == pa: s.emit(S, s.x(a, b, pb), -1); s.emit(S, tw[()], -1)
                elif c == pb: s.emit(S, s.x(a, b, pa), -1); s.emit(S, tw[()], -1)
                else: s.emit(S, s.x(a, b, c ^ 1), -1); s.emit(S, s.add(tw[(c // 2,)], PP), -1)

    def cover(s, n):
        """bitmask of the points covered by the triples of node n."""
        if n not in s.cov:
            sp = s.sup[n]; m = 0
            while sp:
                lo = sp & -sp; m |= sum(1 << p for p in s.triples[lo.bit_length() - 1]); sp ^= lo
            s.cov[n] = m
        return s.cov[n]
    def emit(s, S, n, coef):
        # a piece whose cover together with S is every point would need a full label: split it into its arguments
        if not n: return
        Sm = sum(1 << p for p in S)
        if s.cover(n) | Sm == (1 << s.h) - 1:
            a, b = s.args[n]; s.emit(S, a, coef); s.emit(S, b, coef)
        else: s.pieces.append((S, n, coef))
    def prune(s):
        s.active = set(); st = [n for _, n, _ in s.pieces] + [n for _, n in s.retained]
        while st:
            n = st.pop()
            if n in s.active: continue
            s.active.add(n)
            if s.args[n]: st.extend(s.args[n])
        s.additions = sum(1 for n in s.active if s.args[n])
        s.roles = s.additions + len(s.pieces) + len(s.retained)       # R: one role slot per use of a node


def compile_roles(c):
    """Role slots: every node gets one output slot per user (gate argument, piece, retained total)."""
    users = {x: [] for x in c.active}
    for n in sorted(c.active):
        if c.args[n]:
            for pos, x in enumerate(c.args[n]): users[x].append(('g', n, pos))
    for i, (_, n, _) in enumerate(c.pieces): users[n].append(('p', i))
    for name, n in c.retained: users[n].append(('r', name))
    edge = {}; src = {}; pout = {}; rout = {}; gates = []; size = 0
    for n in sorted(c.active):
        if c.args[n]: ins = (edge[n, 0], edge[n, 1]); piv = ins[0]
        else: piv = size; size += 1; ins = (piv,); src[c.triples[n - 1]] = piv
        outs = (piv,) + tuple(range(size, size + len(users[n]) - 1)); size += len(users[n]) - 1
        assert len(set(ins)) == len(ins) and set(ins) & set(outs) == {piv}
        gates.append((n, ins, outs))
        for u, sl in zip(users[n], outs):
            if u[0] == 'g': edge[u[1], u[2]] = sl
            elif u[0] == 'p': pout[u[1]] = sl
            else: rout[u[1]] = sl
    assert size == c.roles
    return dict(size=size, gates=gates, src=src, pout=pout, rout=rout)


if __name__ == '__main__':
    for h in map(int, sys.argv[1:]):
        c = NStar3(h); print(dict(h=h, v=len(c.triples), additions=c.additions, pieces=len(c.pieces), R=c.roles), flush=True)
