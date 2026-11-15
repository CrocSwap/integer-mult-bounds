"""BIG-RELAY rehost2.py: joint relabel of F -> G for EVERY register whose chain visits F (interior stops, births at F, ends at F).
New chain: replace F by G; drop duplicates if G equals a neighbour; must stay strictly ascending; mains never visit relay frames.
Cost = exact helper cost f(d_end-d_start) - sum f(gaps) (D0/call), delta vs base."""
import pickle, collections, sys
from lib import *
W = load(); NP, mains, fixed, dim = setup(W); ch = chains(W)
X = pickle.load(open('explore.pkl', 'rb'))
def span(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return frozenset(s)
SP = [span(b) for b in W['frames']]
visit = collections.defaultdict(list)
for r in range(NP):
    for k, (fr, t) in enumerate(ch[r]): visit[fr].append(r)
res = []
for F in X['relay']:
    regs = sorted(set(visit[F])); assert not any(r in mains for r in regs)
    base = sum(hcost([dim[x] for x, _ in ch[r]]) for r in regs)
    best = None
    for G in range(len(SP)):
        if G == F: continue
        tot = 0.0; ok = True
        for r in regs:
            c = [x for x, _ in ch[r]]; c = [G if x == F else x for x in c]
            c2 = [c[0]] + [c[i] for i in range(1, len(c)) if c[i] != c[i - 1]]
            if any(not SP[c2[i]] < SP[c2[i + 1]] for i in range(len(c2) - 1)) or len(c2) < 2: ok = False; break
            tot += hcost([dim[x] for x in c2])
        if ok and (best is None or tot - base < best[0]): best = (tot - base, G)
    res.append((F, len(regs), best))
ok = [r for r in res if r[2] is not None]
print('relay frames with a legal joint re-host', len(ok), '; improving', [(F, n, G, round(d, 4)) for F, n, (d, G) in ok if d < -1e-9])
print('nonimproving deltas', sorted(round(r[2][0], 3) for r in ok if r[2][0] >= -1e-9))
pickle.dump(res, open('rehost2.pkl', 'wb'))
