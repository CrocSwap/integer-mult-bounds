"""G2CLUSTER epoch2g.py (own code): descend-then-reintake lifetime with MIXED labels.
Walk V0=<e3> -> P1=<e1,e2,e3> -> V1=<e1,e2> -> P2=<e1,e2,e4,e5>; cost 2+1+2 = 5. Exact replay + exhaustive F2-decoder minimum
over rows supported on the receipt ports (targets x sources)."""
import sys, itertools, collections
sys.path.insert(0, 'code/uphase')
from fattr import *
B1T = [int(a) for a in sys.argv[1].split(',')]; B2T = [int(a) for a in sys.argv[2].split(',')]
H0S = [int(a) for a in sys.argv[3].split(',')]; H1S = [int(a) for a in sys.argv[4].split(',')]
P = sorted(set(B1T + B2T + H0S + H1S)); idx = {q: i for i, q in enumerate(P)}
assert all(bin(q).count('1') % 2 for q in P)
init = {}
for t, q in enumerate(P):
    init[('X', t)] = (span([q]), {('x', t): Fr(1)}); init[('Y', t)] = (frozenset([0]), {('y', t): Fr(1)})
V0 = span([4]); P1 = span([1, 2, 4]); V1 = span([1, 2]); P2 = span([1, 2, 8, 16])
assert all(q in P1 for q in B1T) and all(q in P2 for q in B2T) and all(not dot(q, 4) for q in H0S) and all(not dot(q, 1) and not dot(q, 2) for q in H1S)
assert not set(B1T) & set(B2T)
prog = [('INIT', 'O', V0, {}, True)]
def viaH(q, C, tag):
    h = ('H', tag, q); init[h] = (frozenset([0]), {('h', str(h)): Fr(1)})
    return [('ADD', h, Fr(1), ('Y', idx[q])), ('MOVE', h, C), ('ADD', 'O', Fr(1), h)]
for q in H0S: prog += viaH(q, V0, 0)
prog += [('MOVE', 'O', span([1, 4])), ('MOVE', 'O', P1)]
for q in B1T: prog += [('MOVE', ('X', idx[q]), P1), ('ADD', ('X', idx[q]), Fr(-1), 'O')]
prog += [('MOVE', 'O', V1)]
for q in H1S: prog += viaH(q, V1, 1)
prog += [('MOVE', 'O', span([1, 2, 8])), ('MOVE', 'O', P2)]
for q in B2T: prog += [('MOVE', ('X', idx[q]), P2), ('ADD', ('X', idx[q]), Fr(-1), 'O')]
prog += [('CLEAR', 'O')]
out = analyze(prog, init, {}, P)
R = sum(lf['cost'] for lf in out['L'])
print('ports', P, '| legality', out['bad'], 'R', R, 'identity_fail', out['identity_fail'])
T = [idx[q] for q in B1T + B2T]; S_ = [idx[q] for q in H0S + H1S]
odd = [(t, s) for t in T for s in S_ if dot(P[t], P[s])]; oi = {c: i for i, c in enumerate(odd)}
M = lambda t, s: out['fin'][('X', t)].get(('y', s), 0)
tgt = sum(1 << oi[c] for c in odd if M(*c) % 2)
rk = rank2([sum(1 << j for j, s in enumerate(S_) if dot(P[t], P[s]) and M(t, s) % 2) for t in T])
print('targets', len(T), 'sources', len(S_), 'odd cells', len(odd), 'rank_F2(Q o Mbar) =', rk)
byprice = collections.defaultdict(set)
for D in range(1, 1 << len(T)):
    Dl = [T[i] for i in range(len(T)) if D >> i & 1]
    for Sm in range(1, 1 << len(S_)):
        Sl = [S_[j] for j in range(len(S_)) if Sm >> j & 1]
        inc = 0; rows = []
        for t in Dl:
            m = 0
            for j, s in enumerate(Sl):
                if dot(P[t], P[s]): inc |= 1 << oi[(t, s)]; m |= 1 << j
            rows.append(m)
        if inc: byprice[rank2(rows)].add(inc)
print('classes', {k: len(v) for k, v in sorted(byprice.items())}, flush=True)
def sums(parts):
    acc = {0}
    for p in parts: acc = {a ^ b for a in acc for b in byprice[p]}
    return acc
cache = {}
def S(parts):
    k = tuple(sorted(parts))
    if k not in cache: cache[k] = sums(k)
    return cache[k]
def size(parts):
    r = 1
    for p in parts: r *= max(1, len(byprice[p]))
    return r
for total in range(1, R + 2):
    hit = None
    for k in range(1, total + 1):
        for pp in itertools.combinations_with_replacement(range(1, total + 1), k):
            if sum(pp) != total or any(len(byprice[p]) == 0 for p in pp): continue
            best = None
            for r in range(0, len(pp)):
                for A in set(itertools.combinations(pp, r)):
                    Bl = list(pp)
                    for a in A: Bl.remove(a)
                    c = size(A) + size(Bl)
                    if best is None or c < best[0]: best = (c, list(A), Bl)
            _, A, Bl = best
            SA = S(A) if A else {0}; SB = S(Bl)
            if len(SA) > len(SB): SA, SB = SB, SA
            if any((tgt ^ a) in SB for a in SA): hit = pp; break
        if hit: break
    print('total', total, '->', 'FOUND ' + str(hit) if hit else 'none', flush=True)
    if hit: print('F2-decoder minimum =', total, 'vs R =', R); break
else:
    print('F2-decoder minimum >', R, '= R  *** exceeds R ***')
