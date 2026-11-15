"""HELPERLB relay.py: who uses the zero-need frames (B_G=0) - hop patterns, fixed-register presence."""
import pickle, collections
D = pickle.load(open('needs.pkl', 'rb')); out = D['out']; dimk = D['dimk']; chain = D['chain']
zero = {G for G, o in out.items() if o['B'] == 0}
pat = collections.Counter(); patz = collections.Counter()
for h, ch in chain.items():
    p = tuple(dimk[ch[i + 1]] - dimk[ch[i]] for i in range(len(ch) - 1))
    nz = sum(1 for x in ch[1:-1] if x in zero); pat[p] += 1; patz[p] += nz
print('zero-need stops by hop pattern (top):', [(p, patz[p], pat[p]) for p, _ in patz.most_common(8)])
fx = sum(1 for G in zero if out[G]['R'] > 0 or out[G]['n'] > 0 or out[G]['m'] > 0)
print('zero-need frames %d; with any fixed register/event %d; pure helper-only %d' % (len(zero), fx, len(zero) - fx))
byd = collections.Counter((dimk[G], out[G]['n'] > 0) for G in zero for _ in range(out[G]['P']))
print('zero-need stops by (dim, fixed arrivals>0):', sorted(byd.items()))
