"""CANCEL: pattern-safe column transport. For call-0 col t, the rows that must stay exact are R_t = {r : B(r,t) = 1}.
A call-1 column with joint label y can be moved onto t without breaking the mask iff b(u_r, y) = 1 for all r in R_t,
i.e. y lies in the affine solution set of {b(u_r, .) = 1 : r in R_t}. Report dim span lab(R_t) and the solution-set size."""
import sys, itertools; sys.path.insert(0, '.')
from hb import *
allv = np.array(list(itertools.product((0, 1), repeat=9)), dtype=np.int64)
dims, sols = set(), set()
for t in range(112):
    R = np.nonzero(B[:, t])[0]
    dims.add(rank2(lab[R]))
    ok = [y for y in allv if ((lab[R] @ Gb @ y) % 2 == 1).all()]
    sols.add(len(ok)); assert any(np.array_equal(y, lab[t]) for y in ok)
print('dim span lab(R_t):', dims, ' #labels y transportable onto t:', sols)
