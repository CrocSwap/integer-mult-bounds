"""UPHASE asc56adj.py: the transposed asc56 U run; is the original also in class P (= F on the adjoint)?"""
import pickle
from fattr import *
from adjoint import adjoint
d = pickle.load(open('../halvpay/f56run_nomix.pkl', 'rb'))
P = d['P']
ap, ai = adjoint(d['prog'], d['init'], 9)
out = analyze(ap, ai, {}, P)
print('adjoint legality', len(out['bad']), out['bad'][:3], ' identity fails', out['identity_fail'])
print('invariants W/alpha', out['viol_W'], out['viol_alpha'], ' W on X at end', out['W_X_nonzero'], ' Y-final odd', out['Yfinal_odd_terms'], ' helper fin y', out['helper_final_y'])
for k, lf in enumerate(out['L']):
    print(' adj life', k, lf['reg'], 'cost', lf['cost'], 'GTD', lf['gtd'], 'cold', lf['cold'], 'nox', lf['nox'], 'bound', chart_bound(lf))
rows = decoder_rows(out, P)
# adjoint X_s receipts should be M^T: on odd cells equal to the original receipts transposed (= -I there)
nb, nc = odd_check(out, rows, P, range(104))
print('adjoint decoder identity on odd cells fails', nb, 'of', nc, ' prices', [price(set(w), set(v), P) for w, v in rows])
# compare adjoint receipts with original receipts transposed (all cells)
o2 = analyze(d['prog'], d['init'], d['targets'], P, check_identity=False)
mis = 0
for t in range(104):
    for s in range(104):
        orig = o2['fin'][('X', t)].get(('y', s), 0) - o2['start'][('X', t)].get(('y', s), 0)
        adj = out['fin'][('X', s)].get(('y', t), 0)
        if orig != adj: mis += 1
print('adjoint X receipts == original M^T on all 104^2 cells: mismatches', mis)
