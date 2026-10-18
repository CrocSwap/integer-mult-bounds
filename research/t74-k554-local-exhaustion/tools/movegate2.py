import sys, json, time
import _paths
import harness as H
"""Exact pricing of single-gate commuting moves. usage: movegate2.py WORD JOBS.json PART NPARTS OUT.json"""
word, jobsf, part, nparts, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
P = H.Pricer(word); B = P.base['B']
jobs = json.load(open(jobsf))[part::nparts]
res = []
for dgain, i, lo, hi, pos in jobs:
    for p in pos:
        ed = dict(delete=[i], insert=[(p, list(B[i][:-1]) + [[]])], tail=[], prepend=[])
        t0 = time.time(); r = P.price(ed, timeout=120)
        res.append(dict(i=i, p=p, gain=dgain, status=r.get('status'), delta=r.get('delta')))
        if r.get('delta') is not None and r['delta'] < 0:
            print('GAIN', i, B[i][:5], 'to', p, r['delta'], r.get('profile'), flush=True)
    if len(res) % 50 < len(pos): print('...', len(res), 'priced; last gate', i, flush=True)
    json.dump(res, open(out, 'w'))
print('done', len(res))
