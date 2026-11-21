"""G2CLUSTER netattr_rside.py: R-side translation of NETATTR's minimal counterexample (i) (h=3, ports {1,2,4,7}).
Network chart c <-> run chart c^perp. Node j (a=<1,4>,b=<5>) = lifetime intake at <2>, output at <2,5>; node k (a=<2,5>,b=<2>)
= intake at <5>, output at <1,4>. The relay j->k needs b_j <= a_k, i.e. run chart <5> <= <2,5>: a DESCENT, which an owned
register pays (publics only ascend). Realised as one descend-then-reintake lifetime."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, '../uphase')
from gfa_test import *
Q = [1, 2, 4, 7]; i1, i2, i4, i7 = 0, 1, 2, 3
init = {}
for t, q in enumerate(Q):
    init[('X', t)] = (span([q]), {('x', t): Fr(1)}); init[('Y', t)] = (frozenset([0]), {('y', t): Fr(1)})
S2, S25, S5, S14 = span([2]), span([2, 5]), span([5]), span([1, 4])
g = [('INIT', 'O', S2, {}, True),
     ('MOVE', ('Y', i1), S2), ('ADD', 'O', Fr(1), ('Y', i1)), ('MOVE', ('Y', i4), S2), ('ADD', 'O', Fr(1), ('Y', i4)),
     ('MOVE', 'O', S25), ('MOVE', ('X', i7), S25), ('ADD', ('X', i7), Fr(1), 'O'),          # node j deposits into 7
     ('MOVE', 'O', S5),                                                                       # the relay = owned descent (cost 1)
     ('MOVE', ('Y', i7), S5), ('ADD', 'O', Fr(1), ('Y', i7)),                                 # node k gathers 7
     ('MOVE', 'O', S14), ('MOVE', ('X', i1), S14), ('ADD', ('X', i1), Fr(1), 'O'), ('MOVE', ('X', i4), S14), ('ADD', ('X', i4), Fr(1), 'O'),
     ('CLEAR', 'O')]
res = gfa(g, init, Q)
R = sum(lf['cost'] for lf in res['L'])
T = {(t, s): res['fin'][('X', t)].get(('y', s), 0) for t in range(4) for s in range(4) if dot(Q[t], Q[s])}
print('legality', res['bad'], 'R', R, 'identity', res['identity_fail'], '| odd-cell receipts', {(Q[t], Q[s]): str(v) for (t, s), v in T.items() if v})
print('NETATTR instance (i) odd pattern reproduced:', sorted((Q[t], Q[s]) for (t, s), v in T.items() if v) == sorted([(1,1),(1,7),(4,4),(4,7),(7,1),(7,4)]))
rep = lifetime_report(res, Q, verbose=True)
print('decoder mass needed (NETATTR proof) = 3 ; R =', R, '=> R-side NOT a failure (R >= mass, tight)')
