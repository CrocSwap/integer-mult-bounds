# EIGENCAP ec4: numeric probe of [CONJ] SINGLE with a known-feasible control FIRST: the exact QZB climb4 STEP-1 design
# (same piece list order, placements, seed, solver as t_climb4.log where it solved at 1.4e-13). Probe only if control passes.
# Placements 0/4 for the merged pieces excluded: invariant => IDLE LAW kills them [P].
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'qzbuild'))
from qzdrive import make_design, try_design
from qzclimb import val
k = 4; n = 6; TR = int(sys.argv[1])
A = set(range(4)); masks = [A, A, {1,2,3}, {1,2,3}, {2,3}, {2,3}]; order = (0,1,2,3)
P = [frozenset(p) for p in [{1},{1},{2},{2},{3},{3},{2,3},{2,3}]]
pl = {0:2, 1:2, 2:3, 3:3, 4:4, 5:4, 6:2, 7:3}
d = make_design(n, k, masks, P, order, pl)
ok, z, S, nr = try_design(d, tries=TR)
print('CONTROL ML k4 val %.3f ok %s res %.2e' % (val(n,k,masks,P), ok, nr), flush=True)
if not ok: print('control failed -> probe not run'); sys.exit()
for p1 in (1,2,3):
    for p2 in range(p1, 4):
        Q = [frozenset({1,2}), frozenset({1,2})] + P[4:]
        q = {0:p1, 1:p2, 2:4, 3:4, 4:2, 5:3}
        d = make_design(n, k, masks, Q, order, q)
        ok, z, S, nr = try_design(d, tries=TR)
        print('  {1,2}x2 at', p1, p2, 'val %.3f ok %s res %.2e' % (val(n,k,masks,Q), ok, nr), flush=True)
        if ok:
            import pickle; pickle.dump((Q, q, z), open('ec4_hit_%d%d.pkl' % (p1, p2), 'wb'))
