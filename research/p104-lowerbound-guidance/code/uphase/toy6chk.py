"""UPHASE toy6chk.py: future attribution on RELAYTREE toy6 (seed 1, 945 ops, 108 public relays, 0 owned, +-1/2 and 1/8 scalars).
Expect: identity exact, invariants 0, W on X 0, Y-final odd terms 0, and receipts vanish on every odd cell (no rows)."""
import pickle
from fattr import *
d = pickle.load(open('toy6_word.pkl', 'rb')); W = d['W']; P = d['ports']; n = len(P)
def nm(s): return ('X', int(s[1:])) if s[0] == 'X' else ('Y', int(s[1:])) if s[0] == 'Y' else ('H', s)
init = {}
for s, r in W['regs'].items():
    k = nm(s); f = span(r['f0'])
    c = {('x', k[1]): Fr(1)} if k[0] == 'X' else {('y', k[1]): Fr(1)} if k[0] == 'Y' else {('h', s): Fr(1)}
    init[k] = (f, c)
prog = [('ADD', nm(o[1]), o[2], nm(o[3])) if o[0] == 'ADD' else ('MOVE', nm(o[1]), span(o[2])) for o in W['program']]
out = analyze(prog, init, {}, P)
print('legality', len(out['bad']), out['bad'][:3], '| owned lifetimes', len(out['L']), '| identity fails', out['identity_fail'])
print('invariants W/alpha', out['viol_W'], out['viol_alpha'], '| W on X at end', out['W_X_nonzero'], '| Y-final odd terms', out['Yfinal_odd_terms'], '| helper finals with y', out['helper_final_y'])
nb, nc = odd_check(out, [], P, range(n))
print('odd cells with nonzero receipts', nb, 'of', nc)
hot = sum(1 for i, o in enumerate(prog) if o[0] == 'ADD' and o[1][0] == 'X' and o[3][0] == 'H')
print('public relay deliveries into X', hot, '| relays', sum(1 for k in init if k[0] == 'H'))
Z = d['Z']; zmis = 0
for t in range(n):
    for s in range(n):
        if s == t: continue
        if out['fin'][('X', t)].get(('y', s), 0) != Z.get((t, s), 0): zmis += 1
print('X = x + Zy check mismatches', zmis, '| Z on odd cells?', sum(1 for (t, s) in Z if dot(P[t], P[s])))
