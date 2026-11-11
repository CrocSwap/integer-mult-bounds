# Target-prefix mixing generator and its checks: the F2 analogue of PR #425's target-basis packets, written by the
# same Claude Opus 5.5 (Anthropic) via Claude Code effort as this package (DreamingOfClouds); Apache-2.0.
"""Target-prefix mixing on a bitE8/1 word (F2 analogue of PR425's target basis V).
For a receiver target u and donor w whose delivered B-phase registers at frames inside G coincide (as an F2 multiset),
u drops those deliveries and instead takes y_w with ONE addition y_u += y_w at the common frame G.  Exactness:
frame-0 preconditioner y_u += y_w (D phase, after w's own D gates) and scatter_u ^= scatter_w.  Helpers, sources,
A and C phases are untouched.  Deterministic greedy choice by climb-cost saving.  usage: mixgen.py WORD(.json[.gz]) OUT.json"""
import gzip, json, math, sys
from collections import Counter, defaultdict
from fractions import Fraction as Fr
def load(p): return json.load(gzip.open(p, 'rt') if p.endswith('.gz') else open(p))
c = load(sys.argv[1]); v = c['v']; h = c['h']; sb = c.get('source_basis_gates', 0)
def rank(idx):
    rows = []
    for i in idx:
        x = [Fr(a) for a in c['lines'][i]]
        for r in rows:
            p = next(k for k in range(h) if r[k])
            if x[p]: f = x[p] / r[p]; x = [a - f * b for a, b in zip(x, r)]
        if any(x): rows.append(x)
    return len(rows)
dim = [rank(f) for f in c['frames']]; F = [frozenset(f) for f in c['frames']]
cost = lambda r: r * math.log(64 / r) if r > 0 else 0
Bb, Bd = c['B'][:sb], c['B'][sb:]
assert all(v <= d < 2 * v and all(s >= 2 * v for s in ss) for f, d, ss in Bd), 'B must be helper deliveries only'
assert not any(v <= s < 2 * v for ph in 'DAC' for f, d, ss in c[ph] for s in ss), 'no target operands in the input'
seq = defaultdict(list)
for i, (f, d, ss) in enumerate(Bd): seq[d].append((i, f, ss))
def chain(t):
    out = []
    for i, f, ss in seq[t]:
        if not out or out[-1] != f: out.append(f)
    return out
def chcost(frs, fin):
    ds = [0] + [dim[f] for f in frs] + [dim[fin]]
    return sum(cost(b - a) for a, b in zip(ds, ds[1:]) if b > a)
def pref(t, G):
    m = Counter()
    for i, f, ss in seq[t]:
        if F[f] <= F[G]:
            for s in ss: m[s] ^= 1
    return frozenset(k for k, b in m.items() if b)
T = range(v, 2 * v); orig = {t: chain(t) for t in T}; fin = {t: c['final'][t] for t in T}
for t in T: assert all(F[a] <= F[b] for a, b in zip(orig[t], orig[t][1:])), 'input target chains nested'
cands = []
for u in T:
    base = chcost(orig[u], fin[u])
    for w in T:
        if w == u: continue
        for G in orig[w]:
            if not F[G] <= F[fin[u]]: continue
            pu = pref(u, G)
            if not pu or pu != pref(w, G): continue
            rest = [f for f in orig[u] if not F[f] <= F[G]]
            if not all(F[G] <= F[f] for f in rest): continue
            sv = base - chcost([G] + rest, fin[u])
            if sv > 1e-9: cands.append((-sv, u, w, G))
cands.sort()
mixfrom, mixG, donors = {}, {}, defaultdict(set)
def anc(t):
    s = set()
    while t in mixfrom: t = mixfrom[t]; s.add(t)
    return s
for nsv, u, w, G in cands:
    if u in mixfrom or u in anc(w): continue
    if w in mixG and not F[mixG[w]] <= F[G]: continue
    if any(not F[G] <= F[mixG[x]] for x in donors[u]): continue
    mixfrom[u] = w; mixG[u] = G; donors[w].add(u)
saving = sum(chcost(orig[u], fin[u]) - chcost([mixG[u]] + [f for f in orig[u] if not F[f] <= F[mixG[u]]], fin[u]) for u in mixfrom)
order, seen = [], set()
def visit(u):
    if u in seen: return
    if u in mixfrom: visit(mixfrom[u])
    seen.add(u); order.append(u)
for u in sorted(mixfrom): visit(u)
recv = [u for u in order if u in mixfrom]
w2 = json.loads(json.dumps(c))
w2['D'] = c['D'] + [[0, u, [mixfrom[u]]] for u in recv]
for u in recv:
    w2['scatter'][u - v] = sorted(set(w2['scatter'][u - v]) ^ set(w2['scatter'][mixfrom[u] - v]))
drop = {i for u in recv for i, f, ss in seq[u] if F[f] <= F[mixG[u]]}
keep = [g for i, g in enumerate(Bd) if i not in drop]
newB = list(Bb)
for k in range(h + 1):
    newB += [g for g in keep if dim[g[0]] == k]
    newB += [[mixG[u], u, [mixfrom[u]]] for u in recv if dim[mixG[u]] == k]
w2['B'] = newB
w2['target_mix'] = dict(rule='y_u += y_w at frame G (after w reaches G); frame-0 preconditioner y_u += y_w; scatter_u ^= scatter_w',
                        receivers=[[u, mixfrom[u], mixG[u]] for u in recv])
raw = json.dumps(w2, sort_keys=True, separators=(',', ':')).encode()
(gzip.open if sys.argv[2].endswith('.gz') else open)(sys.argv[2], 'wb').write(raw if not sys.argv[2].endswith('.gz') else raw)
print(json.dumps(dict(receivers=len(recv), mix_dims=dict(Counter(dim[mixG[u]] for u in recv)), target_climb_saving_per_call=round(saving, 3),
                      B_gates=[len(c['B']), len(newB)], D_gates=[len(c['D']), len(w2['D'])])))
