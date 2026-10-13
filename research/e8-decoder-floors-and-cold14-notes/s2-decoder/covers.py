import pickle, numpy as np, sys
from collections import Counter
from geo import *
H = pickle.load(open('hyper.pkl', 'rb'))
HYP = [(sz, n, m) for sz in H for (n, m) in H[sz]]
LIVE = list(range(8, 120)); LIVEMASK = sum(1 << i for i in LIVE)
Lf = L.astype(float)
def covers_for(t):
    out = []
    for w in range(1, 512):
        if w == uint[t] or not lab_dot(w, uint[t]): continue
        Z = Rmask[w] & LIVEMASK & ~(1 << t)
        for sz, n, m in HYP:
            rest = Z & ~m
            ri = members(rest)
            if len(ri) == 0: continue
            if np.linalg.matrix_rank(Lf[ri]) <= 7:
                out.append((w, n, sz, bin(Z & m).count('1'), len(ri)))
    return out
if __name__ == '__main__':
    t = int(sys.argv[1])
    cv = covers_for(t)
    print('target', t, 'covers', len(cv), 'distinct w', len({c[0] for c in cv}))
    print(Counter((c[2], c[3], c[4]) for c in cv).most_common(20))
    pickle.dump(cv, open('covers_%d.pkl' % t, 'wb'))
