"""UPHASE asc56.py: future attribution on the MIXED (x/y-mixing, den 2^-5) asc56 U-phase run (halvpay/f56run.pkl, data from our own
FANOUT56 build).  Prints: legality, identity, invariants, lifetime classes, decoder rows, prices, master-form numbers."""
import pickle, sys, time
from fattr import *
t0 = time.time()
d = pickle.load(open('../halvpay/f56run.pkl', 'rb'))
prog, init, targets, P = d['prog'], d['init'], d['targets'], d['P']
out = analyze(prog, init, targets, P)
print('legality problems', len(out['bad']), out['bad'][:3])
miss = sum(1 for r, (f, c) in targets.items() if out['fin'].get(r) != c)
print('target misses (replay)', miss)
print('IDENTITY failures (X targets)', out['identity_fail'])
print('chart invariant violations: W', out['viol_W'], ' alpha', out['viol_alpha'])
print('x-balance: nonzero W on X publics at end', out['W_X_nonzero'], ' Y-final odd terms', out['Yfinal_odd_terms'], ' helper finals with y', out['helper_final_y'])
print('output events', len(out['ev']))
for k, lf in enumerate(out['L']):
    print(' life', k, lf['reg'], 'cost', lf['cost'], 'GTD', lf['gtd'], 'cold-intake', lf['cold'], 'no-x', lf['nox'],
          '#intakes', len(lf['intakes']), '#outs', len(lf['outs']), 'chart bound', chart_bound(lf))
for name, ports in [('P104', range(104)), ('Q96', range(96))]:
    ports = list(ports); ps = set(ports)
    rows = decoder_rows(out, P, ps)
    nb, nc = odd_check(out, rows, P, ports)
    pr = [price(set(w), set(v), P) for (w, v) in rows]
    print(name, 'decoder identity on odd cells: fails', nb, 'of', nc, '| row prices', pr, 'sum', sum(pr),
          '| |D|,|S|', [(len(w), len(v)) for w, v in rows])
    print(name, 'master form', master(rows, P, ports))
print('%.1fs' % (time.time() - t0))
