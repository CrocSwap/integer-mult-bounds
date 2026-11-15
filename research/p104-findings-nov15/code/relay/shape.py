"""BIG-RELAY shape.py: what each relay frame does. Per frame: registers touching it, F-op transfer graph (j->i for i += c j),
mutual pairs (butterflies), and for pinned no-path pairs whether F is the JOIN of the two predecessor frames and/or the MEET of
the two successor frames (the 'diamond' [a_i+a_j, b_i^b_j] collapses to F)."""
import pickle, collections
from lib import *
W = load(); NP, mains, fixed, dim = setup(W); P = W['program']; ch = chains(W)
X = pickle.load(open('explore.pkl', 'rb')); PN = pickle.load(open('pin.pkl', 'rb'))['nopath']
def span(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return frozenset(s)
SP = [span(b) for b in W['frames']]; idx = {s: i for i, s in enumerate(SP)}
def join(A, B):
    s = set(A)
    for v in B: s |= {x ^ v for x in s}
    return frozenset(s)
ops = collections.defaultdict(list)
for t, e in enumerate(P):
    if e[0] == 'ADD' and e[4] in PN: ops[e[4]].append(e)
def nb(r, F):
    c = [x for x, _ in ch[r]]; k = c.index(F); return (c[k - 1] if k else None), (c[k + 1] if k + 1 < len(c) else None)
st = collections.Counter(); shp = collections.Counter(); dia = collections.Counter()
for F in PN:
    E = ops[F]; tr = {(e[1], e[2]) for e in E}
    mutual = sum(1 for (i, j) in tr if (j, i) in tr) // 2
    regs = {x for e in E for x in e[1:3]}
    shp[('regs', min(len(regs), 9), 'transfers', min(len(tr), 12), 'mutual', mutual)] += 1
    for (i, j) in PN[F]:
        ai, bi = nb(i, F); aj, bj = nb(j, F)
        if None in (ai, aj, bi, bj): dia['endpoint at F'] += 1; continue
        J = join(SP[ai], SP[aj]); M = SP[bi] & SP[bj]
        dia[('F==join(a_i,a_j)', J == SP[F], 'F==meet(b_i,b_j)', M == SP[F])] += 1
print('transfer-graph shapes (top):'); [print('  ', k, v) for k, v in shp.most_common(10)]
print('pinned no-path pairs, diamond test:', dict(dia))
# ceiling: each diamond-collapsed pinned pair needs a courier that visits a_j (after j's pick) and b_i (before i's read), which no
# helper does today (flood): >= 1 new stop (>= f(2)-2f(1) = 2 ln 2) per distinct (a_j, b_i).
import math
L = 2 * math.log(2); gain = {r[0]: r[6] for r in X['rows']}
need = collections.Counter(); 
for F in PN:
    s = set()
    for (i, j) in PN[F]:
        ai, bi = nb(i, F); aj, bj = nb(j, F)
        if None in (ai, aj, bi, bj): continue
        if join(SP[ai], SP[aj]) == SP[F] and (SP[bi] & SP[bj]) == SP[F]: s.add((aj, bi))
    need[F] = len(s)
cz = sum(max(0, gain[F] - L * need[F]) for F in PN); call = sum(gain.values())
print('relay gain total %.1f D0/call; frames with >=1 collapsed pinned pair %d; ceiling after courier stops %.1f D0/call; frames still positive %d'
      % (call, sum(1 for F in PN if need[F]), cz, sum(1 for F in PN if gain[F] > L * need[F] + 1e-9)))
print('need dist', sorted(collections.Counter(need.values()).items()))
H = pickle.load(open('pin.pkl', 'rb'))['half']
need2 = {}
for F in PN:
    best = {}
    for (i, j) in PN[F]:
        ai, bi = nb(i, F); aj, bj = nb(j, F)
        if None in (ai, aj, bi, bj): continue
        if join(SP[ai], SP[aj]) == SP[F] and (SP[bi] & SP[bj]) == SP[F]:
            k = (aj, bi); c = 1 if H[F][(i, j)] else 2; best[k] = min(best.get(k, 9), c)
    need2[F] = sum(best.values())
cz2 = sum(max(0, gain[F] - L * need2[F]) for F in PN)
print('refined (2 new stops when no helper touches either end): ceiling %.1f D0/call, frames positive %d' % (cz2, sum(1 for F in PN if gain[F] > L * need2[F] + 1e-9)))
print('half-touched pairs', sum(1 for F in H for v in H[F].values() if v), 'of', sum(len(H[F]) for F in H))
