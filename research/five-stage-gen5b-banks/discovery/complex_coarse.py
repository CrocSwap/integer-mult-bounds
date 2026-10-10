import sys, importlib.util, gzip, json, time
from fractions import Fraction as Q
from collections import Counter
from pathlib import Path
root = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location('mm', root / 'moment.py'); cost = importlib.util.module_from_spec(spec); spec.loader.exec_module(cost)
spec = importlib.util.spec_from_file_location('pc', root / 'portable_complex.py'); pc = importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)
labels = pc.module(root, 'complex_labels')
for cert in sys.argv[2:]:
    c = json.loads(gzip.decompress(open(cert, 'rb').read()))
    inv = Counter()
    # compute histogram without the pinned-literal checks: blocks give it directly
    for rr, hh in c['blocks'].items():
        for k, n in hh.items(): inv[int(k)] += n
    H = Counter({k: 5 * n for k, n in inv.items()}); v, h = c['v'], c['h']
    for rank in [2*h-2, h-1, 2*h+2, 4]: H[rank] += 2 * v
    t = time.time(); r = cost.certify(dict(H), 110, 14692, False)
    b = Q(int(Q(r['lower']) * 10**18), 10**18)
    lo, hi = cost.moment(dict(H), 110, 14692, b, False); lo2, hi2 = cost.moment(dict(H), 110, 14692, b + Q(1, 10**18), False)
    print(cert, 'calls', sum(H.values()), 'mass', sum(k*n for k, n in H.items()), 'coarse b =', b.numerator, '/10^18 =', float(b), 'moment(b) <1:', hi < 1, 'moment(b+1e-18) >1:', lo2 > 1, '%.0fs' % (time.time() - t), flush=True)
