"""CTCOVER ctsplit.py (own code): FLUSHROW SPLIT applied to the R2TEST R=2 run; exact replay over GF(2) and Q (SP engine/FA,
read-only import); lifetime census + CT forest check; exact field-independent mass lower bound for the realised odd pattern."""
import sys, itertools; sys.path.insert(0, '../seppays')
from eng import *
from fa import gfa, price
P = [1, 2, 7, 11, 13]; n = 4; T = 5; fs = frozenset
def ops_split(sign):
    return [('INIT', ('O', 0), fs({0, 13})),
     ('MOVE', ('Y', 2), fs({0, 13})), ('ADD', ('O', 0), 1, ('Y', 2)),
     ('MOVE', ('Y', 3), fs({0, 10, 13, 7})), ('ADD', ('O', 0), 1, ('Y', 3)),
     ('MOVE', ('O', 0), fs({0, 1, 12, 13})), ('ADD', ('X', 0), sign, ('O', 0)),
     ('MOVE', ('O', 0), fs({0, 12})),
     # SPLIT hand-over (FR §2): G = H0 at C=<12>, d' = O1 born at C
     ('MOVE', ('H', 0), fs({0, 12})), ('ADD', ('H', 0), 1, ('O', 0)), ('INIT', ('O', 1), fs({0, 12})),
     ('ADD', ('O', 1), 1, ('H', 0)), ('ADD', ('H', 0), -1, ('O', 0)), ('ADD', ('O', 1), -1, ('H', 0)), ('CLEAR', ('O', 0)),
     ('MOVE', ('Y', 0), fs({0, 12})), ('ADD', ('O', 1), 1, ('Y', 0)),
     ('MOVE', ('Y', 1), fs({0, 1, 12, 13})), ('ADD', ('O', 1), 1, ('Y', 1)),
     ('MOVE', ('O', 1), fs({0, 11, 12, 7})), ('ADD', ('X', 3), sign, ('O', 1)), ('ADD', ('X', 2), sign, ('O', 1)),
     ('CLEAR', ('O', 1))]
meta = dict(nh=1, Xch=[span([q]) for q in P], Ych=[fs([0])] * 5, Hch=[fs([0])])
odd = {(t, s) for t in range(T) for s in range(T) if dot(P[t], P[s])}
def lifetimes(ops):
    """per owned lifetime: intake charts, read-out charts, GTD flag, cost"""
    L = {}; ch = {}
    for op in ops:
        if op[0] == 'INIT': L[op[1]] = dict(A=[], B=[], gtd=True, out=False, cost=0); ch[op[1]] = op[2]
        elif op[0] == 'MOVE' and op[1][0] == 'O':
            if ch[op[1]] <= op[2]: L[op[1]]['cost'] += fdim(op[2]) - fdim(ch[op[1]])
            ch[op[1]] = op[2]
        elif op[0] == 'MOVE': ch[op[1]] = op[2]
        elif op[0] == 'ADD':
            d, e = op[1], op[3]
            if d in L:
                if L[d]['out']: L[d]['gtd'] = False
                L[d]['A'].append(ch[d])
            if e in L: L[e]['out'] = True; L[e]['B'].append(ch[e])
    return L
for F, sign in [(Field(2), 1), (Field(0), -1)]:
    ops = ops_split(sign); R = replay(n, P, F, meta, ops)
    g = gfa(n, P, F, meta, ops)
    Rec = R.rec(); pat = {(t, s) for (t, s) in odd if Rec[t][s]}
    print('field', 'GF2' if F.p == 2 else 'Q', 'bad', R.bad, 'pinned', R.pinned(), 'R', R.cost,
          'odd pattern', sorted(pat), 'idfail', g['idfail'], 'oddfail', g['oddfail'], 'FA price sum', g['psum'], 'hot intakes', g['hot'])
    for w, e, C in g['rows']: print('   row w', w, 'eff', e, 'price', price(set(w), set(e), P))
    for k, v in lifetimes(ops).items():
        A = fs.intersection(*v['A']); B = span([x for c in v['B'] for x in c])
        print('   lifetime', k, 'GTD', v['gtd'], 'cost', v['cost'], 'A', sorted(A), 'B', sorted(B))
# exact mass lower bound (any field): rows of price 0 vanish on odd cells; a row with supports (D,S) is nonzero on EVERY odd cell of DxS.
tgt = {(0,2),(0,3),(2,0),(2,1),(2,2),(3,0),(3,1),(3,3)}; Z = odd - tgt
subs = [frozenset(i for i in range(T) if m >> i & 1) for m in range(1, 1 << T)]
rows = {}
for D in subs:
    for S in subs:
        p = price(D, S, P); O = fs((t, s) for t in D for s in S if (t, s) in odd)
        if p <= 2 and O: rows.setdefault(O, p); rows[O] = min(rows[O], p)
one = [O for O, p in rows.items() if O == tgt]
two = [(O1, O2) for O1, p1 in rows.items() for O2, p2 in rows.items() if p1 + p2 <= 2 and tgt <= O1 | O2 and not (Z & (O1 ^ O2)) and not ((O1 & O2) - tgt - Z)]
print('mass<=2 candidates: one-row', len(one), 'two-row', len(two), '=> mass >= 3 over every field' if not one and not two else '')
