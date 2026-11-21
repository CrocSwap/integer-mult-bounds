# LANDSPANC1 lc1: C1 ("stop at every out-tree node") in ls5's DP. Own LANDSPAN code imported read-only (ls2/ls5), cwd = landspan dir for data paths.
import os, sys
os.chdir('<research-tree>/cards/WILD/UNIMODEL/claspec/landspan'); sys.path.insert(0, '.')
import ls5
from ls5 import *
t = 0.01; s = 1 - t
pR = lambda R: (R - R**s) / (R - 1); p8 = pR(8)
one = {d: 1.0 for d in range(2, n)}
# (A) baseline = ls5 in-only origin pricing
print('A baseline in-only origin S/p8 =', round(bound(one, pR) / p8, 4))
# (B) C1 as explicit per-node stop on every out-tree node: a stop at D is an ARRIVAL by a non-final public (deaths at V) = ls5's I2 row
#     (edge C->D, origin price p(min(8,9-dim C)) = p(min(8,d') mirrored), shared by <=A(C) out-trees).  Run ls5's full a-scan (max over mixing).
best = bound(one, pR); a = dict(one)
for x in [i / 40 for i in range(41)]:
    b = {d: (x if d < 8 else 1.0) for d in range(2, n)}; v = bound(b, pR)
    if v > best + 1e-9: best, a = v, b
print('B in+out I2 rows (C1 = I2), uniform a scan: best S/p8 =', round(best / p8, 4), 'at a', {d: round(x, 3) for d, x in a.items()})
# (C) per-coordinate scan
cur = best
for step in (0.5, 0.25, 0.125, 0.0625, 0.03125):
    for rnd in range(3):
        for d in range(2, 8):
            for sg in (-1, 1):
                b = dict(a); b[d] = min(1.0, max(0.0, a[d] + sg * step))
                if b[d] == a[d]: continue
                v = bound(b, pR)
                if v > cur + 1e-9: a, cur = b, v
print('C coordinate scan: best S/p8 =', round(cur / p8, 4), {d: round(x, 3) for d, x in a.items()})
# (D) CONDITIONAL, NOT claimed: out-tree node stops DISTINCT from in-tree arrivals (additive in+out, full price, no sharing mixture)
vin = dpo(lambda d, e: pR(min(8, 9 - e)), True)
vout = dpo(lambda d, e: pR(min(8, d)), False)
print('D [conditional additive in+out distinct stops] in', round(NT * vin / p8, 3), 'out', round(NT * vout / p8, 3), 'sum', round(NT * (vin + vout) / p8, 3))
