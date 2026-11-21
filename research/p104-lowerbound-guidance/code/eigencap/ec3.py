# EIGENCAP ec3: numeric probe (evidence only) of the [CONJ] "non-invariant non-contact events are singletons":
# ML k4 masks, middle idles {1}x2,{2}x2 replaced by two pieces {1,2} (non-invariant by the IDLE LAW), all placements; random starts.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'qzbuild'))
from qzdrive import make_design, try_design
from qzclimb import val
import numpy as np
k = 4; n = 6
masks = [{0,1,2,3}]*2 + [{1,2,3}]*2 + [{2,3}]*2
order = (0,1,2,3)
base = [frozenset({2,3})]*2 + [frozenset({3})]*2
basepl = {0:2, 1:2, 2:3, 3:3}
print('control (ML k4 chart, idles in blocks):', flush=True)
P = base + [frozenset({1})]*2 + [frozenset({2})]*2; pl = dict(basepl); pl.update({4:2,5:2,6:3,7:3})
d = make_design(n, k, [set(m) for m in masks], P, order, pl)
ok, z, S, nr = try_design(d, tries=int(sys.argv[1]), seed=5)
print('  control val %.3f ok %s res %.2e' % (val(n,k,masks,P), ok, nr), flush=True)
P = base + [frozenset({1,2})]*2
for p1 in range(5):
    for p2 in range(p1, 5):
        pl = dict(basepl); pl[4] = p1; pl[5] = p2
        d = make_design(n, k, [set(m) for m in masks], P, order, pl)
        ok, z, S, nr = try_design(d, tries=int(sys.argv[1]), seed=11)
        print('  {1,2} at', p1, p2, 'val %.3f ok %s res %.2e' % (val(n,k,masks,P), ok, nr), flush=True)
