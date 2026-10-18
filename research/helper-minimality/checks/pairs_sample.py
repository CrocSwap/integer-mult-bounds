"""Pre-read table (inputs/derived/pairs.json.gz): statistics of the stored table, a recompute of all 271 singles and 150 seeded pairs
with the exact oracle, and the no-op legality / kappa of the oracle on the #799 X4 word."""
import os, sys, random
HM = os.environ['HM_ROOT']; os.chdir(HM + '/cards/B159'); sys.path.insert(0, '.')
from pairsio import load_pairs
import mdl
from collections import Counter
M, sg, pv = load_pairs(HM + '/inputs/derived/pairs.json.gz')
assert M == mdl.M
kinds = Counter(m[0] for m in M)
st = (len(M), kinds['h2r'], kinds['r2h'], kinds['def'], sum(1 for v in sg if not v), min(len(v) for v in sg), len(pv), sum(1 for v in pv.values() if not v), min(len(v) for v in pv.values()))
print('stored table: moves %d (h2r %d, r2h %d, deferrals %d); singles legal %d, min |V| %d; pairs %d, legal %d, min |V| %d' % st)
print('%s preread.stats' % ('PASS' if st == (271, 84, 92, 95, 0, 2, 36501, 0, 2) else 'FAIL'))
bad = 0
for i, m in enumerate(M):
    if mdl.V([m])[0] != sg[i]: bad += 1
print('%s preread.singles  recomputed 271 singles, %d differ' % ('PASS' if not bad else 'FAIL', bad))
rnd = random.Random(717); keys = sorted(pv); samp = rnd.sample(keys, 150); bad2 = 0
for ab in samp:
    if mdl._p(ab) != pv[ab]: bad2 += 1
print('%s preread.pairs-sample  recomputed 150 seeded pairs, %d differ' % ('PASS' if not bad2 else 'FAIL', bad2))
from decimal import Decimal
r = mdl.O.evaluate(mdl.s)
k = str(r['kappa'])
print('no-op legal %s kappa %s' % (r['legal'], k[:24]))
print('%s oracle.noop  legal and kappa starts 0.001661634653669567 (the kappa published by #799)' % ('PASS' if r['legal'] and k.startswith('0.001661634653669567') else 'FAIL'))
sys.exit(1 if (st != (271, 84, 92, 95, 0, 2, 36501, 0, 2) or bad or bad2 or not r['legal']) else 0)
