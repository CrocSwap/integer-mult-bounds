"""G2CLUSTER epoch2.py (own code): the 2-epoch lifetime V0=<e3> -> P1=<e1,e2,e3> -> V1=<e1,e2> -> P2=<e1,e2,e4,e5>, R=5.
(1) exact replay with fattr (legality, receipts);  (2) F2-decoder minimum of the receipts (exhaustive, meet-in-the-middle)."""
import sys, itertools, collections
sys.path.insert(0, 'code/uphase')
from fattr import *
N = 5; V = frozenset(range(32))
P = [1, 2, 4, 8, 16, 7, 11, 28]           # port labels (odd weight)
idx = {q: i for i, q in enumerate(P)}
B1T = [1, 4, 7]; B2T = [2, 8, 16, 11]; H0S = [1, 2, 8, 16]; H1S = [4, 28]
perpq = lambda q: frozenset(x for x in range(32) if not dot(x, q))
init = {}
for t, q in enumerate(P):
    init[('X', t)] = (span([q]), {('x', t): Fr(1)}); init[('Y', t)] = (frozenset([0]), {('y', t): Fr(1)})
V0 = span([4]); P1 = span([1, 2, 4]); V1 = span([1, 2]); P2 = span([1, 2, 8, 16])
prog = [('INIT', 'O', V0, {}, True)]
for q in H0S:
    prog += [('MOVE', ('Y', idx[q]), V0), ('ADD', 'O', Fr(1), ('Y', idx[q]))]
prog += [('MOVE', 'O', span([1, 4])), ('MOVE', 'O', P1)]
for q in B1T:
    prog += [('MOVE', ('X', idx[q]), P1), ('ADD', ('X', idx[q]), Fr(-1), 'O')]
prog += [('MOVE', 'O', V1)]
for q in H1S:
    prog += [('MOVE', ('Y', idx[q]), V1), ('ADD', 'O', Fr(1), ('Y', idx[q]))]
# Y's of H0S sit at V0=<e3>; those that are also needed later stay put (charts only ascend; no conflict)
prog += [('MOVE', 'O', span([1, 2, 8])), ('MOVE', 'O', P2)]
for q in B2T:
    prog += [('MOVE', ('X', idx[q]), P2), ('ADD', ('X', idx[q]), Fr(-1), 'O')]
prog += [('CLEAR', 'O')]
out = analyze(prog, init, {}, P)
R = sum(lf['cost'] for lf in out['L'])
print('legality', out['bad'], 'R', R, 'identity_fail', out['identity_fail'], 'inv', out['viol_W'], out['viol_alpha'], 'gtd', out['L'][0]['gtd'])
n = len(P)
S = [[out['fin'][('X', t)].get(('y', s), 0) - 0 for s in range(n)] for t in range(n)]
odd = [(t, s) for t in range(n) for s in range(n) if dot(P[t], P[s])]
oi = {c: i for i, c in enumerate(odd)}
tgt = 0
for (t, s) in odd:
    v = S[t][s]
    if v != 0:
        assert v.denominator == 1
        if v.numerator % 2: tgt |= 1 << oi[(t, s)]
print('receipt odd cells nonzero:', sum(1 for (t, s) in odd if S[t][s] != 0), 'of', len(odd))
# rank of Q o Sbar
rows = []
for t in range(n):
    m = 0
    for s in range(n):
        if dot(P[t], P[s]) and S[t][s] != 0 and S[t][s].numerator % 2: m |= 1 << s
    rows.append(m)
print('rank_F2(Q o Sbar) =', rank2(rows))
# all F2 rows (D,S): odd incidence + price
byprice = collections.defaultdict(set)
for D in range(1, 1 << n):
    Dl = [t for t in range(n) if D >> t & 1]
    for Sm in range(1, 1 << n):
        Sl = [s for s in range(n) if Sm >> s & 1]
        inc = 0
        for t in Dl:
            for s in Sl:
                if dot(P[t], P[s]): inc |= 1 << oi[(t, s)]
        if inc == 0: continue
        pr = rank2([sum((dot(P[t], P[s])) << j for j, s in enumerate(Sl)) for t in Dl])
        byprice[pr].add(inc)
print('distinct incidence vectors by price:', {k: len(v) for k, v in sorted(byprice.items())})
def sums(parts):
    """set of XORs of one vector from each price class in parts"""
    acc = {0}
    for p in parts:
        acc = {a ^ b for a in acc for b in byprice[p]}
    return acc
best = None
for total in range(1, 7):
    found = False
    for parts in [pp for k in range(1, total + 1) for pp in itertools.combinations_with_replacement(range(1, total + 1), k) if sum(pp) == total]:
        parts = sorted(parts, reverse=True)
        h = len(parts) // 2
        A, Bp = parts[:max(1, h)], parts[max(1, h):]
        if sum(len(byprice[p]) for p in A) == 0: continue
        SA = sums(A)
        SB = sums(Bp) if Bp else {0}
        if any((tgt ^ b) in SA for b in SB):
            print('F2 decoder of total price', total, 'exists, parts', parts); found = True; break
    if found: best = total; break
    print('no F2 decoder of total price', total)
print('F2-decoder minimum =', best, ' vs R =', R)
# recover rows of a [2,2] solution
inc2rows = collections.defaultdict(list)
for D in range(1, 1 << n):
    Dl = [t for t in range(n) if D >> t & 1]
    for Sm in range(1, 1 << n):
        Sl = [s for s in range(n) if Sm >> s & 1]
        inc = 0
        for t in Dl:
            for s in Sl:
                if dot(P[t], P[s]): inc |= 1 << oi[(t, s)]
        pr = rank2([sum((dot(P[t], P[s])) << j for j, s in enumerate(Sl)) for t in Dl])
        if pr == 2 and inc: inc2rows[inc].append((D, Sm))
for a in byprice[2]:
    if (tgt ^ a) in byprice[2]:
        r1 = min(inc2rows[a], key=lambda x: bin(x[0]).count('1') + bin(x[1]).count('1'))
        r2 = min(inc2rows[tgt ^ a], key=lambda x: bin(x[0]).count('1') + bin(x[1]).count('1'))
        show = lambda r: ([P[t] for t in range(n) if r[0] >> t & 1], [P[s] for s in range(n) if r[1] >> s & 1])
        print('row1 D,S =', show(r1), ' row2 D,S =', show(r2)); break
