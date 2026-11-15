"""positive control: shear-transport a few NOT-pinned F-ops (and the movable SCALEs) and check final rows equal base (fastx k=4)."""
import sys, pickle, time
sys.path.insert(0, '../../NETCAUX'); import fastx
from mover import *
W = load(); NP, mains, fixed, dim = setup(W); P = W['program']
X = pickle.load(open('explore.pkl', 'rb')); PN = pickle.load(open('pin.pkl', 'rb'))['nopath']
base = [(float(i), e) for i, e in enumerate(P)]; tl = timeline(base, NP, W['owned_fields'], W['initial'])
R = fastx.proj_matrix(NP, 4, 1); a = fastx.FastReplay(W, R, 4)
done = 0; tried = 0
for F in X['relay'][:120]:
    for t, e in enumerate(P):
        if done >= 4 or tried > 60: break
        if evframe(e) != F or e[0] != 'ADD' or (e[1], e[2]) in PN.get(F, ()): continue
        tried += 1
        j = t   # base ops: index == key
        for d in (-1, 1):
            r = try_move(base, j, F, tl, d)
            if r is None: continue
            W2 = dict(W); W2['program'] = [x for k, x in r[0]]; b = fastx.FastReplay(W2, R, 4)
            print('F', F, e, 'dir', d, '->', r[1], 'replay ok', b.ok, b.bad[:2], 'rows equal', a.proj == b.proj); done += 1; break
print('tried', tried, 'moved', done)
