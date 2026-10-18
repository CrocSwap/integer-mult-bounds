# MASK9 case (b), d0 = D in {7, 8}: Z_0 is the annihilator of the label span U of term 0's live rows (dim U = 9 - D in {1, 2}), so U is
# spanned by the labels of 1 or 2 lines. Enumerate exactly: Z_0 = {c : O_c ∩ T = ∅} for every set T of 1 (D = 8) or 2 (D = 7) lines with
# dim = D. Writes cnt6_UNIT_D.pkl in cnt6's format (list of subspaces) for cnt7/cnt8.   usage: cnt10.py UNIT D
import sys
DD = int(sys.argv[2]); sys.argv = sys.argv[:2]
from m9lib import *
perms = pickle.load(open(f'orbits_{unit}.pkl', 'rb'))['perms']
seenT = set(); reps = []
for T in itertools.combinations(range(v), 9 - DD):
    if T in seenT: continue
    reps.append(T); seenT.add(T); st = [T]
    while st:
        x = st.pop()
        for p in perms:
            y = tuple(sorted(p[t] for t in x))
            if y not in seenT: seenT.add(y); st.append(y)
print('line-set orbit reps', len(reps), flush=True)
out = set()
for T in reps:
    Tm = sum(1 << t for t in T)
    Z = tuple(sorted(c for c in ks if not cls[c] & Tm))
    if len(Z) == (1 << DD) - 1: out.add(Z)
print('D', DD, 'subspaces', len(out), flush=True)
pickle.dump(sorted(out), open(f'cnt6_{unit}_{DD}.pkl', 'wb'))
