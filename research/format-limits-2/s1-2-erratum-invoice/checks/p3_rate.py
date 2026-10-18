"""P3: helper exchange rate on #649 (% of b per helper removed in all 72 calls: its climbs leave the local profile and its
width w returns to the idle cover, either as one narrow w-child or merged into 48-wide idle children).
Shapes = the climb lists of the helper registers of width w in the #626 ck and jp8 words (exact mean over all of them).
Gate: b (hence kappa = b/(1+b)) reproduced from the PLAN profile of #649, #645, #646, #635 and #626."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from invoice import *
import statistics as S

KAPPA = {649: '0.001652528731617094', 645: '0.001649483702558979', 646: '0.001627103256702062',
         635: '0.001636241501576388', 626: '0.001635527380375392'}
PLAN = {649: 'pr649/PLAN.json.gz', 645: 'pr645/PLAN.json.gz', 646: 'pr646/PLAN.json.gz', 635: 'pr635/PLAN.json.gz', 626: 'pr626/PLAN.json.gz'}
prof = {}
for n, rel in PLAN.items():
    pl = load(rel); H = profile(pl); prof[n] = H
    live, dfc, m = pl['live'], pl['deficit'], pl['M']
    b = root(H, m, live); k = b / (1 + b)
    lit = D(KAPPA[n])
    ok = hmass(H) == m * live - dfc and abs(k - lit) <= D('1e-18')
    check('P3.gate-%d' % n, ok, 'kappa = b/(1+b) = %s vs published %s (m=%d, live=%d, deficit=%d)' % (str(k)[:20], KAPPA[n], m, live, dfc))
w = Word626()
BASE = Counter(prof[649]); b649 = root(BASE, M, W0)
def price(width, rule):
    pool = [cl for p in CALLS for cl in w.helpers(p, width)]
    vals = []
    for cl in pool:
        H = Counter(BASE)
        for x in cl:
            H[x] -= 72
        if rule == 'narrow':
            H[width] += 72
        else:
            H[48] += D(width * 72) / 48
        assert abs(hmass(H) - hmass(BASE)) < 1e-6
        vals.append(float((root(H, M, W0, start=b649 * D('0.9')) / b649 - 1) * 100))
    return S.mean(vals), len(pool)
TABLE = {9: (0.070, 0.140), 8: (0.051, 0.118), 7: (0.038, 0.101), 5: (0.031, 0.084), 4: (0.026, 0.072)}   # README P3 table (3 decimals)
for wd, (tn, tm) in TABLE.items():
    (n, cnt), (g, _) = price(wd, 'narrow'), price(wd, 'merge48')
    check('P3.rate-w%d' % wd, abs(n - tn) <= 0.0005 and abs(g - tm) <= 0.0005,
          'w%d helper (%d shapes): %.4f%% b narrow, %.4f%% merged into 48-bins (table %.4g / %.4g)' % (wd, cnt, n, g, tn, tm))
finish()
