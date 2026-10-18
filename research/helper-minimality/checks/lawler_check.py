"""Soundness checks of the order-free Lawler oracle used by S3/S4/bridge rows (cards/B171/lawler799.py:lawler):
 (a) synthetic mergeable / conflicting pairs; (b) 3000 seeded random small instances: lawler finds an order iff brute force over all
 permutations does, and a returned order is feasible."""
import os, sys, random, itertools
HM = os.environ['HM_ROOT']; sys.path.insert(0, HM + '/cards/B171')
import lawler799 as L
def feasible(order, visits, base):
    J = list(base)
    for k in order:
        J = list(L.basis(J + list(visits[k][0])))
        if not L.ok(J, visits[k][1]): return False
    return True
o, rem = L.lawler([((0b1000,), [0b110]), ((0b1,), [0b1100])], (), ())
print('PASS lawler.mergeable' if o is not None else 'FAIL lawler.mergeable')
o2, rem2 = L.lawler([((0b10,), [0b10]), ((0b1,), [0b1])], (), ())
print('PASS lawler.conflict' if o2 is None else 'FAIL lawler.conflict')
rnd = random.Random(20261013); agree = feas = 0; bad = 0
for t in range(3000):
    n = rnd.randint(1, 6); m = rnd.randint(2, 6)
    vis = [(tuple(rnd.randrange(1, 1 << m) for _ in range(rnd.randint(1, 2))), [rnd.randrange(1, 1 << m) for _ in range(rnd.randint(1, 2))]) for _ in range(n)]
    base = tuple(rnd.randrange(1, 1 << m) for _ in range(rnd.randint(0, 1)))
    bf = any(feasible(p, vis, base) for p in itertools.permutations(range(n)))
    order, _ = L.lawler(vis, base, ())
    if (order is not None) != bf or (order is not None and not feasible(order, vis, base)): bad += 1
    feas += bf; agree += 1
print('%s lawler.bruteforce  %d instances, %d feasible, %d disagreements' % ('PASS' if not bad and 0 < feas < agree else 'FAIL', agree, feas, bad))
sys.exit(1 if bad else 0)
