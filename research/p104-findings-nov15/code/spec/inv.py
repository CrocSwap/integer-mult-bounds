import sys
sys.path.insert(0, '../PRICEKIT')
import pricekit as pk
from collections import Counter
W = pk.load('../ATTACK/STACK7616/best7616.json.gz')
C = pk.load('../MONOCALLER/7113_CALLER.json')
nat = pk.native_from_word(W); ci = pk.caller_invoice(C)
inv = pk.invoice(ci, nat); pr = pk.price(inv, 30)
print('kappa', pk.kstr(pr['kappa']), 'S', pr['S'], 'D0', float(pr['D0']))
mass = lambda h: sum(r*v for r, v in h.items())
T, P = nat['T'], nat['P']
print('native per call: T mass', mass(T), 'P mass', mass(P), 'helpers', sum(T.values()), 'S_nat', mass(T)-mass(P))
print('main moves mass', {k: mass(v) for k, v in nat['main_moves'].items()})
n = W['public']; dim = [len(b) for b in W['frames']]
om = Counter()
for e in W['program']:
    if e[0] == 'MOVE' and e[1] >= n: om[abs(dim[e[3]] - dim[e[2]])] += 1
print('owned move hist', dict(om), 'mass', mass(om))
print('calls', ci['nJ'], 'caller T mass', mass(ci['T']), 'caller P mass', mass(ci['P']))
print('caller P', dict(ci['P'])); print('caller T', dict(ci['T']))
