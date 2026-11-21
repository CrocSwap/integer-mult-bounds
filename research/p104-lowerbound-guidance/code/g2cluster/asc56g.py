"""G2CLUSTER asc56g.py: global FA (owned weights + flush, effective coldness) on asc56 U runs (no-mix and mixed)."""
import pickle, sys
sys.path.insert(0, '.'); sys.path.insert(0, '../uphase')
from gfa_test import *
for f in ('../halvpay/f56run_nomix.pkl', '../halvpay/f56run.pkl'):
    d = pickle.load(open(f, 'rb')); prog, init, targets, P = d['prog'], d['init'], d['targets'], d['P']
    res = gfa(prog, init, P)
    miss = sum(1 for r, (fc, c) in targets.items() if res['fin'].get(r) != c)
    nb, _ = odd_check(res, P, 104)
    rep = lifetime_report(res, P)
    print(f, '| legality', len(res['bad']), 'misses', miss, 'identity', res['identity_fail'], 'odd fails', nb, 'inv', res['viol_pub'], res['viol_row'],
          '| lives', [(r['cost'], r['price'], r['nri'], r['cold'], r['bound']) for r in rep], 'sum price', sum(r['price'] for r in rep), 'R', sum(r['cost'] for r in rep))
