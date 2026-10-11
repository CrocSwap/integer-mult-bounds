"""Exact maximum number of kernel pivots on a bit word (rank-1 coordinate-entrance model of README section 2), computed, not searched.

Model.  Candidates C (helpers whose first frame contains frame lines), axis lists fl[h] = frame lines inside first(h), delivery vectors
r_h = resp(h) in F2^120.  README section 2 item 3: with classes T_i (disjoint, T_i subset of S_i = {h : i in fl[h]})
    max pivots = |C| - min over partitions of  sum_i rank_F2(r_h : h in T_i)          (a MIN-SUM-RANK LIST PARTITION).
It is not a matroid union / intersection / parity problem (those maximise rank) and it is NP-hard when the number of classes is unbounded
(vertex cover reduces to it), so there is no general polynomial algorithm; with 8 classes and this block structure it is solved exactly:
  1. The matroid of the delivery vectors splits into connected components (fundamental-circuit graph); the objective is additive over them.
  2. A component of at most 40 elements: exhaustive dynamic programme over the tuple of class spans (cost = rank increments).
  3. A big component: its elements are block-local (support inside one connected group of targets, blocks defined by vectors of weight <= 4)
     or coupling elements.  Blocks have disjoint coordinates, so ranks add over blocks.  LOWER BOUND = sum of the exact block minima (DP)
     + the minimum over all assignments of the free coupling elements of sum_i rank(C_i modulo the largest span the blocks could give class i).
     EXACT SEARCH: depth-first over the block-optimal (and, up to the slack budget, near-optimal) span tuples of the blocks, with the optimistic
     completion "every remaining block at its maximal span" for pruning.  The first total T = LB, LB+1, ... that is attainable is the minimum;
     every T below it is shown infeasible (the slack of a block is at most T - LB, and the per-block state lists with that slack are complete),
     and the attainable T is a witness.  On R715 this is: T = 120 infeasible with the block-optimal states alone, T = 121 attained.
usage: exact_pivots.py REPO_RESEARCH_DIR WORD_IN OUT.json     (word geometry from kernel_cap.Geo; same word and retiming as the ceiling analysis)
The same algorithm was first run on dumped data (components 208 / 28 / 14 and 13 coloops).  Written for this package by DreamingOfClouds with
Claude Opus 5.5 (Anthropic), via Claude Code; the exact method (block decomposition, per-block exact DP, coupling enumeration, DFS with
optimistic completion) is from the matroid-optimisation scouting pass on the pivot problem.  Apache-2.0."""
import os, sys, json, itertools
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kernel_cap as KC

MAXSLACK = 2          # the search raises T above the lower bound by at most this much (R715 needs 1); a failure raises instead of guessing
SMALL = 40            # components up to this many elements are solved by the plain span-tuple DP

def red(y, b):
    for x in b: y = min(y, y ^ x)
    return y

def canon(basis):
    """canonical (fully reduced, sorted) basis of the span, as a hashable tuple"""
    out = []
    for x in sorted(basis, reverse=True):
        x = red(x, out)
        if x: out.append(x); out.sort(reverse=True)
    ch = True
    while ch:
        ch = False
        for i in range(len(out)):
            for j in range(len(out)):
                if i != j and (out[i] >> (out[j].bit_length() - 1)) & 1: out[i] ^= out[j]; ch = True
    return tuple(sorted(out, reverse=True))

def span_of(vs):
    b = []
    for y in vs:
        y = red(y, b)
        if y: b.append(y); b.sort(reverse=True)
    return b

def quot_rank(vecs, basis):
    b = list(basis); r = 0
    for v in vecs:
        y = red(v, b)
        if y: b.append(y); b.sort(reverse=True); r += 1
    return r

def components(C, resp):
    """connected components of the linear matroid of resp over C (two elements are together iff some circuit contains both); loops are singletons"""
    par = {h: h for h in C}
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    basis = []
    for h in C:
        y, cm = resp[h], {h}
        for bv, bs in basis:
            if y >> (bv.bit_length() - 1) & 1: y ^= bv; cm = cm ^ bs
        if y: basis.append((y, cm)); basis.sort(key=lambda z: -z[0])
        else:
            cm = list(cm)
            for x in cm[1:]: par[find(cm[0])] = find(x)
    comp = defaultdict(list)
    for h in C: comp[find(h)].append(h)
    return sorted((sorted(v) for v in comp.values()), key=lambda v: (-len(v), v[0]))

class Exact:
    def __init__(self, fl, resp, nbits):
        self.fl, self.resp, self.nbits = fl, resp, nbits

    def blockstates(self, els, cap):
        """all reachable (span-tuple per class -> minimal cost) after assigning every element of els to one class of its list; cost = rank increments <= cap"""
        fl, resp = self.fl, self.resp
        classes = sorted({i for h in els for i in fl[h]}); ci = {i: k for k, i in enumerate(classes)}
        els = sorted(els, key=lambda h: (len(fl[h]), resp[h]))
        states = {tuple(() for _ in classes): 0}
        for h in els:
            new = {}
            for st, cost in states.items():
                for i in fl[h]:
                    k = ci[i]; b = st[k]; y = red(resp[h], list(b))
                    if y:
                        nc = cost + 1
                        if nc > cap: continue
                        ns = st[:k] + (canon(list(b) + [resp[h]]),) + st[k + 1:]
                    else: nc = cost; ns = st
                    if ns not in new or new[ns] > nc: new[ns] = nc
            states = new
        return classes, states

    def small(self, c):
        for cap in range(1, 60):
            cl, st = self.blockstates(c, cap)
            if st: break
        else: raise AssertionError('no assignment within 59 rank increments')
        return min(st.values())

    def analyse(self, c):
        resp, nb = self.resp, self.nbits
        par = list(range(nb))
        def f(x):
            while par[x] != x: par[x] = par[par[x]]; x = par[x]
            return x
        supp = lambda y: [t for t in range(nb) if y >> t & 1]
        for h in c:
            s = supp(resp[h])
            if len(s) <= 4:
                for t in s[1:]: par[f(t)] = f(s[0])
        blocks = defaultdict(list); coupling = []
        for h in c:
            bs = {f(t) for t in supp(resp[h])}
            if len(bs) == 1: blocks[bs.pop()].append(h)
            else: coupling.append(h)
        return blocks, coupling

    def big(self, c):
        """exact minimum sum-rank of one large component; returns (T, lower_bound, info)"""
        fl, resp = self.fl, self.resp
        blocks, coupling = self.analyse(c)
        mins = {kk: self.small(els) for kk, els in blocks.items()}
        cache = {}
        def STs(kk, sl):
            """block kk's span states with slack (cost above the block minimum) at most sl, cheapest first"""
            if (kk, sl) not in cache:
                cl, st = self.blockstates(blocks[kk], mins[kk] + sl)
                cache[kk, sl] = (cl, sorted(st.items(), key=lambda kv: kv[1]))
            return cache[kk, sl]
        S0 = sum(mins.values())
        classes8 = sorted({i for h in c for i in fl[h]})
        locmax = {kk: {i: span_of([resp[h] for h in els if i in fl[h]]) for i in classes8} for kk, els in blocks.items()}
        fixed = [h for h in coupling if len(fl[h]) == 1]; free = sorted(h for h in coupling if len(fl[h]) > 1)
        assert len(free) <= 20, 'too many free coupling elements to enumerate'
        def Ci(a):
            d = defaultdict(list)
            for h in fixed: d[fl[h][0]].append(h)
            for h, i in zip(free, a): d[i].append(h)
            return d
        def value(a, spans):
            d = Ci(a); return sum(quot_rank([resp[h] for h in d[i]], spans[i]) for i in classes8)
        fullmax = {i: span_of([v for kk in blocks for v in locmax[kk][i]]) for i in classes8}
        vals = [(value(a, fullmax), a) for a in itertools.product(*[fl[h] for h in free])]
        cmin = min(v for v, a in vals)
        LB = S0 + cmin
        order = sorted(blocks, key=lambda kk: len(STs(kk, 0)[1]))
        def feasible(T, sl_cap):
            budget = T - S0       # block slack + coupling rank <= budget
            A = [a for v, a in vals if v <= budget]
            def opt_spans(chosen, depth):
                sp = {i: list(chosen[i]) for i in classes8}
                for kk in order[depth:]:
                    for i in classes8:
                        for v in locmax[kk][i]:
                            y = red(v, sp[i])
                            if y: sp[i].append(y); sp[i].sort(reverse=True)
                return sp
            def dfs(depth, chosen, alive, slack):
                if depth == len(order): return True
                kk = order[depth]; cls, st = STs(kk, sl_cap)
                for s_, cost in st:
                    sl = cost - mins[kk]
                    if slack + sl > budget: continue
                    ch = {i: list(chosen[i]) for i in classes8}
                    for k, i in enumerate(cls):
                        for v in s_[k]:
                            y = red(v, ch[i])
                            if y: ch[i].append(y); ch[i].sort(reverse=True)
                    sp = opt_spans(ch, depth + 1)
                    al = [a for a in alive if slack + sl + value(a, sp) <= budget]
                    if al and dfs(depth + 1, ch, al, slack + sl): return True
                return False
            return dfs(0, {i: [] for i in classes8}, A, 0)
        # T = LB + k is searched first with the block states of slack <= s for s = 0..k.  A hit is always a witness.  A miss is a proof
        # only for s = k: the block slacks and the coupling rank add up to at most T - S0 = cmin + k with the coupling part >= cmin.
        log = []
        for k in range(MAXSLACK + 1):
            T = LB + k
            for s in range(k + 1):
                ok = feasible(T, s); log.append([T, s, ok])
                if ok: return T, LB, dict(blocks=len(blocks), coupling=len(coupling), free_coupling=len(free), sum_block_minima=S0, coupling_lower_bound=cmin, tried=log)
        raise AssertionError('minimum sum-rank not found within the slack budget')

def exact_max_pivots(C, fl, resp, nbits):
    X = Exact(fl, resp, nbits); comps = []; total = 0
    for c in components(C, resp):
        rk = len(span_of([resp[h] for h in c]))
        if len(c) <= SMALL: T = X.small(c); LB = None; how = 'span-tuple DP'; info = {}
        else: T, LB, info = X.big(c); how = 'block decomposition + exhaustive search'
        comps.append(dict(size=len(c), rank=rk, min_sum_rank=T, lower_bound=LB, pivots=len(c) - T, method=how, **info)); total += len(c) - T
    return total, comps

def analysis(G):
    C = G.C; fl = {h: list(G.axes[h]) for h in C}; resp = {h: G.resp[h] for h in C}
    nbits = max(1, max(r.bit_length() for r in resp.values()))
    total, comps = exact_max_pivots(C, fl, resp, nbits)
    big = [c for c in comps if c['size'] > 1]
    return dict(model='rank-1 coordinate entrances (README section 2, items 2-3)', candidates=len(C), exact_max_pivots=total,
                exact_max_pivots_after_parity=total - total % 2, proved_ceiling=len(C) - KC.rank_f2([resp[h] for h in C]),
                nontrivial_components=[dict(size=c['size'], rank=c['rank'], min_sum_rank=c['min_sum_rank'], pivots=c['pivots'], method=c['method']) for c in big],
                coloops=sum(1 for c in comps if c['size'] == 1 and c['pivots'] == 0), loops=sum(1 for c in comps if c['size'] == 1 and c['pivots'] == 1),
                big_component_search=[{k: c[k] for k in ('size', 'lower_bound', 'sum_block_minima', 'coupling_lower_bound', 'blocks', 'free_coupling', 'tried')} for c in comps if c['size'] > SMALL])

if __name__ == '__main__':
    R, wp, out = sys.argv[1:4]
    U = KC.setup(R); w, ret, mv = KC.primitive_retimed(U, wp); G = KC.Geo(U, ret)
    a = analysis(G)
    json.dump(a, open(out, 'w'), indent=1, sort_keys=True); print(json.dumps(a, sort_keys=True))
