"""Kernel selection for the R715 bit word: choose the entrance class (one of the 8 frame lines) of every candidate carrier so that
the number of pivots, |C| - sum_i rank_F2 resp(T_i), is maximal, then emit PR #443 kernel entries [[E lines], pivot, donors].
Why this is the whole problem for coordinate rank-1 entrances: a class i with members T_i (all in S_i) has donors = any F2-basis of
resp(T_i) and pivots = the other members (each is an XOR of donors), so the best a class can do is |T_i| - rank resp(T_i); donors and
pivots of different classes are different helpers.  Search = simulated annealing over the class assignment with a self-contained
xorshift64* generator (bit-for-bit reproducible on any platform and Python version).
usage: select_kernel.py REPO_RESEARCH_DIR WORD_IN OUT_SELECTION.json [--seed N] [--iters N] [--restarts N] [--ilp SECONDS]
  --seed/--iters/--restarts  annealing (default: the pinned search that produced data/kernel-selection.json)
  --ilp S                    also run the CP-SAT relation model (<= 3 donors per pivot, needs ortools) for S seconds and report it
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0."""
import sys, json, math, itertools
from collections import defaultdict
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import kernel_cap as KC

class XS:
    """xorshift64* (Vigna 2016); randbelow by 53-bit multiply-shift; no platform dependence"""
    M = (1 << 64) - 1
    def __init__(s, seed): s.x = (seed * 0x9E3779B97F4A7C15 + 0x1234567) & s.M or 1; [s.next() for _ in range(8)]
    def next(s):
        x = s.x; x ^= x >> 12; x ^= (x << 25) & s.M; x ^= x >> 27; s.x = x
        return (x * 0x2545F4914F6CDD1D) & s.M
    def below(s, n): return ((s.next() >> 11) * n) >> 53
    def unit(s): return (s.next() >> 11) / float(1 << 53)

def anneal(G, seed, iters, T0=0.6, Tmin=0.03):
    C, resp, axes = G.C, G.resp, G.axes; rng = XS(seed)
    a = {h: axes[h][rng.below(len(axes[h]))] for h in C}
    cls = {i: [h for h in C if a[h] == i] for i in G.FRAMEL}
    rk = {i: KC.rank_f2([resp[h] for h in cls[i]]) for i in G.FRAMEL}
    cur = sum(rk.values()); best, ba = cur, dict(a); movable = [h for h in C if len(axes[h]) > 1]
    for it in range(iters):
        T = T0 * (1 - it / iters) + Tmin
        h = movable[rng.below(len(movable))]; old = a[h]; alt = [i for i in axes[h] if i != old]; new = alt[rng.below(len(alt))]
        cls[old].remove(h); cls[new].append(h)
        ro, rn = KC.rank_f2([resp[x] for x in cls[old]]), KC.rank_f2([resp[x] for x in cls[new]])
        c2 = cur - rk[old] - rk[new] + ro + rn
        if c2 <= cur or rng.unit() < math.exp((cur - c2) / T):
            cur = c2; rk[old], rk[new] = ro, rn; a[h] = new
            if cur < best: best, ba = cur, dict(a)
        else: cls[new].remove(h); cls[old].append(h)
    return best, ba

def entries_from_assignment(G, a):
    """donors = greedy F2 basis of each class (in helper-id order); pivots = the remaining members, each written over the basis"""
    resp, sel = G.resp, []
    for i in G.FRAMEL:
        mem = sorted(h for h in a if a[h] == i)
        ind, bl = [], []
        for h in mem:                                   # pass 1: independent members
            y, cm = resp[h], {h}
            for bv, bs in bl:
                if y >> (bv.bit_length() - 1) & 1: y ^= bv; cm = cm ^ bs
            if y: bl.append((y, cm)); bl.sort(key=lambda z: -z[0]); ind.append(h)
        bl = []
        for h in ind:                                   # pass 2: elimination basis over the independent members only
            y, cm = resp[h], {h}
            for bv, bs in bl:
                if y >> (bv.bit_length() - 1) & 1: y ^= bv; cm = cm ^ bs
            bl.append((y, cm)); bl.sort(key=lambda z: -z[0])
        indset = set(ind)
        for p in mem:
            if p in indset: continue
            y, cm = resp[p], set()
            for bv, bs in bl:
                if y >> (bv.bit_length() - 1) & 1: y ^= bv; cm = cm ^ bs
            assert y == 0
            sel.append([[i], p, sorted(cm)])
    return sel

def parity_fix(G, sel):
    """PR #443's rank congruence: replicas*(8R - sum entrance ranks) = 0 mod 64 with 32 replicas, i.e. an even entrance-rank total"""
    tot = sum(len(e[0]) for e in sel)
    if (8 * G.ret['R'] - tot) % 2: sel = sel[:-1]
    return sel

def search(G, seed, iters, restarts):
    best = None
    for r in range(restarts):
        b, a = anneal(G, seed + r, iters)
        print('  restart %d seed %d: pivots %d' % (r, seed + r, len(G.C) - b), flush=True)
        if best is None or b < best[0]: best = (b, a)
    return best

def ilp(G, seconds):
    from ortools.sat.python import cp_model
    C, resp, axes = G.C, G.resp, G.axes
    S = {i: [h for h in C if i in axes[h]] for i in G.FRAMEL}; rels = []
    for i in G.FRAMEL:
        for p in S[i]:
            others = [h for h in S[i] if h != p]; t = resp[p]; by = defaultdict(list)
            for h in others: by[resp[h]].append(h)
            idx = {h: k for k, h in enumerate(others)}
            for h in by.get(t, []): rels.append((p, (h,), i))
            for x, y in itertools.combinations(others, 2):
                if resp[x] ^ resp[y] == t: rels.append((p, (x, y), i))
                for z in by.get(t ^ resp[x] ^ resp[y], []):
                    if idx[z] > idx[y]: rels.append((p, (x, y, z), i))
    M = cp_model.CpModel()
    a = {(h, i): M.NewBoolVar('a%d_%d' % (h, i)) for h in C for i in axes[h]}; pv = {h: M.NewBoolVar('p%d' % h) for h in C}; dn = {h: M.NewBoolVar('d%d' % h) for h in C}
    for h in C:
        M.Add(sum(a[h, i] for i in axes[h]) <= 1); M.Add(pv[h] + dn[h] <= 1); M.Add(pv[h] + dn[h] <= sum(a[h, i] for i in axes[h]))
    u = [M.NewBoolVar('u%d' % k) for k in range(len(rels))]; byp = defaultdict(list)
    for k, (p, D, i) in enumerate(rels):
        byp[p].append(k); M.AddImplication(u[k], pv[p]); M.AddImplication(u[k], a[p, i])
        for d in D: M.AddImplication(u[k], dn[d]); M.AddImplication(u[k], a[d, i])
    for p in C: M.Add(sum(u[k] for k in byp[p]) == pv[p])
    M.Maximize(sum(pv.values()))
    S_ = cp_model.CpSolver(); S_.parameters.max_time_in_seconds = seconds; S_.parameters.num_workers = 4; S_.parameters.random_seed = 1
    st = S_.Solve(M)
    return dict(relations=len(rels), status=S_.StatusName(st), pivots=int(S_.ObjectiveValue()), bound=S_.BestObjectiveBound())

if __name__ == '__main__':
    args = [x for x in sys.argv[1:] if not x.startswith('--')]; opt = {}
    it = iter(sys.argv[1:])
    for x in it:
        if x.startswith('--'): opt[x] = next(it)
    args = [x for x in sys.argv[1:] if not x.startswith('--') and x not in opt.values()]
    R, wp, out = args
    seed = int(opt.get('--seed', 0)); iters = int(opt.get('--iters', 0)); restarts = int(opt.get('--restarts', 0))
    U = KC.setup(R); w, ret, mv = KC.primitive_retimed(U, wp); G = KC.Geo(U, ret)
    best, a = search(G, seed, iters, restarts)
    sel = parity_fix(G, entries_from_assignment(G, a)); info = KC.check_selection(G, sel)
    print(json.dumps(dict(seed=seed, iters=iters, restarts=restarts, pivots=len(sel), annealed_pivots=len(G.C) - best, **info), sort_keys=True))
    json.dump(sel, open(out, 'w'))
    if '--ilp' in opt: print('ILP', json.dumps(ilp(G, float(opt['--ilp']))))
