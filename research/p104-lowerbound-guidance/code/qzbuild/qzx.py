# exactify a design: python qzx.py <spec.json> <out.json> ; spec = {n,k,masks,pieces,order,place,seed,tries}
import sys, json
from qzdrive import *
sp = json.load(open(sys.argv[1]))
d = make_design(sp['n'], sp['k'], sp['masks'], [frozenset(p) for p in sp['pieces']], tuple(sp['order']), {int(a): b for a, b in sp['place'].items()})
print('design val %.4f' % chat(d), flush=True)
for attempt in range(sp.get('attempts', 4)):
    ok, z, S, nr = try_design(d, tries=sp.get('tries', 12), seed=sp.get('seed', 0) + attempt)
    print('numeric', ok, '%.2e' % nr, flush=True)
    if not ok: continue
    n, m = d.n, d.m
    order = list(range(2*n*m, d.nv)) + list(range(0, n*m)) + list(range(n*m, 2*n*m))
    z2, fixed, vals = (fix_batch if sp.get("batch", 1) else fix_all)(S, z, order=order)
    print('fixed', int(fixed.sum()), 'of', d.nv, flush=True)
    for md in (10**4, 10**6, 10**9):
        ok2, wf, C, data = exact_word(d, z2, fixed, vals, maxden=md, path=sys.argv[2])
        print('exact maxden', md, 'LEGAL', ok2, 'WF', wf, flush=True)
        if ok2 and wf:
            ab = data[2]; print('ab', [str(a*b) for a, b in ab]); sys.exit(0)
print('FAILED'); sys.exit(1)
