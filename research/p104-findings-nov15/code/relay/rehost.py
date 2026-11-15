"""BIG-RELAY rehost.py: re-host ALL events of relay frame F at one other frame G (joint relabel, timing unchanged).
Each stopping helper h (a_h -> F -> b_h) must be able to sit at G during its F-stay: a_h < G < b_h (new stop), or G == a_h / G == b_h
(merge into the neighbouring stop: the MOVE is shifted, legal only if h has no op in between, true here since the stay at F holds only F-ops).
Exact hop-cost delta (D0/call); rows unchanged by construction (same ops, same order)."""
import pickle, collections
from lib import *
W = load(); NP, mains, fixed, dim = setup(W)
X = pickle.load(open('explore.pkl', 'rb'))
def span(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return frozenset(s)
SP = [span(b) for b in W['frames']]
best = []
for F in X['relay']:
    S = X['stops'][F]; cands = []
    for G in range(len(SP)):
        if G == F: continue
        d = 0.0; ok = True
        for (h, ar, lv, a, b) in S:
            old = -f(dim[F] - dim[a]) - f(dim[b] - dim[F])
            if G == a or G == b: new = -f(dim[b] - dim[a])
            elif SP[a] < SP[G] < SP[b]: new = -f(dim[G] - dim[a]) - f(dim[b] - dim[G])
            else: ok = False; break
            d += new - old
        if ok: cands.append((d, G))
    if cands: best.append((min(cands), F, len(cands)))
print('relay frames with any joint re-host target', len(best), 'of', len(X['relay']))
print('improving (delta<0):', [(F, G, round(d, 4)) for (d, G), F, n in best if d < -1e-9][:20])
print('delta dist', collections.Counter(round(d, 3) for (d, G), F, n in best))
