"""CARRIER8 q5.py: PA-relay analysis of REUSE96's monotone Q5 rendezvous run (ops copied from reuse96/g2run.py)."""
import sys; sys.path.insert(0, '.')
from pa import *
P = [1, 2, 7, 11, 13]; fs = frozenset
ops = [('INIT', ('O', 0), fs({0, 13})), ('MOVE', ('Y', 2), fs({0, 11, 13, 6})), ('ADD', ('O', 0), 1, ('Y', 2)),
 ('INIT', ('O', 1), fs({0, 12})), ('MOVE', ('Y', 3), fs({0, 13})), ('ADD', ('O', 0), 1, ('Y', 3)),
 ('ADD', ('Y', 1), 1, ('O', 0)), ('MOVE', ('Y', 1), fs({0, 12})), ('ADD', ('O', 1), 1, ('Y', 1)),
 ('MOVE', ('Y', 1), fs({0, 1, 12, 13})), ('ADD', ('X', 0), 1, ('Y', 1)), ('MOVE', ('Y', 3), fs({0, 10, 13, 7})),
 ('ADD', ('X', 2), 1, ('Y', 3)), ('MOVE', ('Y', 0), fs({0, 2, 12, 14})), ('ADD', ('O', 1), 1, ('Y', 0)),
 ('ADD', ('X', 1), 1, ('Y', 0)), ('MOVE', ('O', 0), fs({0, 1, 12, 13})), ('ADD', ('Y', 1), 1, ('O', 0)),
 ('ADD', ('X', 0), 1, ('Y', 1)), ('MOVE', ('O', 1), fs({0, 11, 12, 7})), ('ADD', ('X', 2), 1, ('O', 1)),
 ('ADD', ('X', 3), 1, ('O', 1)), ('CLEAR', ('O', 0)), ('CLEAR', ('O', 1))]
def init_for(P, F, nh=1):
    I = {}
    for t, q in enumerate(P):
        I[('X', t)] = (span([q]), {('x', t): F.c(1)}); I[('Y', t)] = (fs([0]), {('y', t): F.c(1)})
    for j in range(nh): I[('H', j)] = (fs([0]), {('h', j): F.c(1)})
    return I
for p, sign in [(2, 1), (0, 1), (0, -1)]:
    F = Fld(p)
    o = [(op[0], op[1], sign if (op[0] == 'ADD' and op[1][0] == 'Y' and op[3][0] == 'O' and o_i == 17) else op[2], op[3]) if op[0] == 'ADD' else op
         for o_i, op in enumerate(ops)]
    # over Q the clean must subtract: Y1 -= O0 (op 17); first deposit +1.  sign=1 run over Q is NOT pinned (control).
    r = analyze(o, init_for(P, F), P, F)
    print('field', 'GF2' if p == 2 else 'Q', 'clean-sign', sign, '| bad', r['bad'], 'pinned', r['pinned'], 'R', r['R'],
          'own-price', r['own'], 'drops', r['drops'], 'acyclic', r['acyclic'], 'LS', r.get('LS'), r['chk'])
    for j, ep in enumerate(r['EP']):
        print('   epoch', j, 'life', ep['life'], 'dimA\'', fdim(ep['Ap']) if ep['Ap'] else None, 'dimB', fdim(ep['B']), 'w', ep['w'],
              'c', ep['c'], 'C', ep['C'], 'N', ep['N'], 'seg', ep['seg'], 'drop', ep['drop'], 'own', ep['own'])
from cfuzz import routing_mass
F = Fld(2); r = analyze(ops, init_for(P, F), P, F); print('GF2 routing mass (one row per source content)', routing_mass(r, P, F), 'R', r['R'])
