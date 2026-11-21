"""FLUSHROW fr_walk.py (own code): exact flush-row prices on 'up a, down 1, up b' walks with spanning labels (N = 6).
Walk C0 -> C1 (up a) -> C2 = hyperplane of C1 (down 1) -> C3 (up b); intake gamma0 at C0, output alpha1 at C1, intake gamma2 at C2,
output alpha3 at C3.  Prints cost, G2C flush-row price sum (global FA rows), and the forward / backward rectangle covers."""
import sys
sys.path.insert(0, 'code/g2cluster')
sys.path.insert(0, 'code/uphase')
from gfa import *
N = 6; V = range(1, 1 << N); odd = [v for v in V if bin(v).count('1') % 2]
e = [1 << i for i in range(N)]
def perp(F): return frozenset(x for x in range(1 << N) if all(not dot(x, b) for b in basis(F)))
def walk(C0, C1, C2, C3, name):
    T1 = [q for q in odd if q in C1]; T3 = [q for q in odd if q in C3]
    S0 = [q for q in odd if q in perp(C0)]; S2 = [q for q in odd if q in perp(C2)]
    P = sorted(set(T1 + T3 + S0 + S2)); ix = {q: i for i, q in enumerate(P)}
    init = {}
    for t, q in enumerate(P): init[('X', t)] = (span([q]), {('x', t): Fr(1)}); init[('Y', t)] = (frozenset([0]), {('y', t): Fr(1)})
    def path(a, b):   # nested single steps a -> b (a<b or b<a)
        out = []; cur = a
        if a <= b:
            for v in basis(b):
                if v not in cur: cur = span(list(cur) + [v]); out.append(('MOVE', 'O', cur))
        else:
            BB = basis(a); keep = b
            while cur != b:
                # drop to a hyperplane of cur containing b
                for v in basis(cur):
                    H = span([x for x in basis(cur) if x != v] + basis(b))
                    if fdim(H) == fdim(cur) - 1 and b <= H: cur = H; break
                out.append(('MOVE', 'O', cur))
        return out
    yc = {('Y', t): frozenset([0]) for t in range(len(P))}
    prog = [('INIT', 'O', C0, {}, True)]
    for q in S0: prog += [('MOVE', ('Y', ix[q]), C0), ('ADD', 'O', Fr(1), ('Y', ix[q]))]; yc[('Y', ix[q])] = C0
    prog += path(C0, C1)
    for q in T1: prog += [('MOVE', ('X', ix[q]), C1), ('ADD', ('X', ix[q]), Fr(-1), 'O')]
    prog += path(C1, C2)
    for q in S2:
        Y = ('Y', ix[q]); G = span(basis(yc[Y]) + basis(C2))
        if not (C2 <= perp(span([q]))): continue
        if yc[Y] <= C2: prog += [('MOVE', Y, C2), ('ADD', 'O', Fr(1), Y)]; yc[Y] = C2
    prog += path(C2, C3)
    xc = {}
    for q in T3:
        X = ('X', ix[q])
        if q in C1 and not C1 <= C3: continue          # X already at C1, cannot descend; skip (label kept only in alpha1)
        prog += [('MOVE', X, C3), ('ADD', X, Fr(-1), 'O')]
    prog += [('CLEAR', 'O')]
    res = gfa(prog, init, P); lf = res['L'][0]
    fl = [res['rows'][j] for j in lf['rows']]
    pr = [price(set(w), set(eff(c, res['fin'])), P) for (_, w, c, C, k) in fl if w and eff(c, res['fin'])]
    # alpha's actually delivered, gammas actually taken
    a1 = {t for t in range(len(P)) if P[t] in C1 and res['fin'][('X', t)].get(('y', ix[S0[0]]), 0) != 0}
    A1 = [ix[q] for q in T1]; A3 = [ix[q] for q in T3 if not (q in C1 and not C1 <= C3)]
    G0 = [ix[q] for q in S0]; G2 = [ix[q] for q in S2 if yc[('Y', ix[q])] == C2]
    fwd = price(set(A1), set(G0), P) + price(set(A3), set(G0 + G2), P)
    bwd = price(set(A1 + A3), set(G0), P) + price(set(A3), set(G2), P)
    print(name, '| legal', not res['bad'], '| identity', res['identity_fail'], '| cost', lf['cost'], '| flush/clear rows', [k for (_, _, _, _, k) in fl],
          'prices', pr, 'sum', sum(pr), '| forward cover', fwd, '| backward cover', bwd, '| ports', len(P))
E = lambda *v: span([e[i] for i in v])
walk(E(3), E(0, 1, 2, 3), E(0, 1, 2), E(0, 1, 2, 4), 'up3 down1 up1, C0 not in C2')
walk(E(2), E(0, 1, 2, 3), E(0, 1, 2), E(0, 1, 2, 4), 'up3 down1 up1, C0 in C2')
walk(E(3), E(0, 2, 3), E(0, 2), E(0, 2, 4, 5), 'up2 down1 up2, C0 not in C2 (G2C shape)')
walk(E(2), E(0, 1, 2, 3), E(0, 1, 2), E(0, 1, 2, 4, 5), 'up3 down1 up2, C0 in C2')
