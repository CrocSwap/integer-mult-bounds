"""G2CLUSTER gadgets2.py: UP's gadgets G1/G2/G3 (constructions copied from uphase/gadgets.py) under GLOBAL FA (owned
weights + flush), forward and on the adjoint (= global PA)."""
import sys
sys.path.insert(0, 'code/g2cluster')
sys.path.insert(0, 'code/uphase')
from gfa_test import *
from adjoint import adjoint
N = 3; V = frozenset(range(8))
perpq = lambda q: frozenset(x for x in range(8) if not dot(x, q))
Lq = lambda q: span([q])
def base(Q):
    init = {}
    for t, q in enumerate(Q):
        init[('X', t)] = (Lq(q), {('x', t): Fr(1)}); init[('Y', t)] = (frozenset([0]), {('y', t): Fr(1)})
    return init
def witness(Q, t):
    q = Q[t]; o = ('W', t)
    return [('MOVE', ('Y', t), perpq(q)), ('INIT', o, perpq(q), {}, True), ('ADD', o, Fr(1), ('Y', t)), ('MOVE', o, V),
            ('MOVE', ('X', t), V), ('ADD', ('X', t), Fr(-1), o), ('CLEAR', o)]
G = {}
Q = [1, 2, 4]; c = 0; init = base(Q); init[('H', 0)] = (frozenset([0]), {('h', 0): Fr(1)})
g = [('ADD', ('H', 0), Fr(1, 2), ('Y', c)), ('INIT', ('U', 0), frozenset([0]), {}, True), ('ADD', ('U', 0), Fr(1, 2), ('Y', c)),
     ('MOVE', ('H', 0), Lq(1)), ('ADD', ('X', c), Fr(-2), ('H', 0)), ('MOVE', ('U', 0), Lq(1)), ('ADD', ('H', 0), Fr(-1), ('U', 0)), ('CLEAR', ('U', 0)),
     ('MOVE', ('H', 0), V), ('MOVE', ('Y', c), perpq(1)), ('MOVE', ('X', c), V), ('ADD', ('X', c), Fr(2), ('H', 0))]
for t in (1, 2): g += witness(Q, t)
G['G1'] = (g, init, Q)
Q = [1, 2, 4]; c, r = 0, 1; init = base(Q); H1 = Lq(1)
g = [('INIT', ('O', 1), frozenset([0]), {}, True), ('ADD', ('O', 1), Fr(1), ('Y', r)), ('ADD', ('Y', r), Fr(1), ('Y', c)),
     ('MOVE', ('Y', r), H1), ('MOVE', ('O', 1), H1), ('INIT', ('O', 2), H1, {}, True), ('ADD', ('O', 2), Fr(1), ('Y', r)), ('ADD', ('O', 2), Fr(-1), ('O', 1)),
     ('ADD', ('Y', r), Fr(-1), ('O', 2)), ('ADD', ('X', c), Fr(-1), ('O', 2)), ('CLEAR', ('O', 1)), ('CLEAR', ('O', 2)),
     ('MOVE', ('Y', r), perpq(2)), ('MOVE', ('X', c), V), ('MOVE', ('Y', c), perpq(1))]
g += witness(Q, 2)
o = ('W', r); g += [('INIT', o, perpq(2), {}, True), ('ADD', o, Fr(1), ('Y', r)), ('MOVE', o, V), ('MOVE', ('X', r), V), ('ADD', ('X', r), Fr(-1), o), ('CLEAR', o)]
G['G2'] = (g, init, Q)
Q = [1, 2, 4]; c = 0; init = base(Q); init[('H', 0)] = (frozenset([0]), {('h', 0): Fr(1)})
g = [('INIT', ('O', 1), frozenset([0]), {}, True), ('ADD', ('O', 1), Fr(1), ('H', 0)), ('ADD', ('H', 0), Fr(1), ('Y', c)), ('MOVE', ('H', 0), H1), ('MOVE', ('O', 1), H1),
     ('INIT', ('O', 2), H1, {}, True), ('ADD', ('O', 2), Fr(1), ('H', 0)), ('ADD', ('O', 2), Fr(-1), ('O', 1)),
     ('ADD', ('H', 0), Fr(-1), ('O', 2)), ('ADD', ('X', c), Fr(-1), ('O', 2)), ('CLEAR', ('O', 1)), ('CLEAR', ('O', 2)),
     ('MOVE', ('H', 0), V), ('MOVE', ('X', c), V), ('MOVE', ('Y', c), perpq(1))]
for t in (1, 2): g += witness(Q, t)
G['G3'] = (g, init, Q)
if __name__ == '__main__':
    for name, (g, init, Q) in G.items():
        run_named(name + ' forward (global FA)', g, init, Q)
        ap, ai = adjoint(g, init, N)
        run_named(name + ' adjoint (global PA)', ap, ai, Q)
