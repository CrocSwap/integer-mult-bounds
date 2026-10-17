from e8cov import *
from e8cov import _bits
from cov import rref_basis, inspan
import itertools, pickle
# pairs of 7-flat masks (Va,Vb) covering N(r0)=Off\{r0} ; use index sets
Noff=om & ~1   # remove line 0
nl=np.uint64(Noff&((1<<64)-1)); nh=np.uint64(Noff>>64)
rl=nl&~lo; rh=nh&~hi
cnt=popcnt(rl)+popcnt(rh)
idx=np.nonzero(cnt<=36)[0]
print('Va candidates',len(idx))
pairs=set()
mk=[masks[k] for k in range(len(masks))]
# for each Va, find all Vb with N \ Va subset Vb : Vb mask must contain R
for k in idx:
    R=(int(rh[k])<<64)|int(rl[k])
    # all 7-flat masks containing R
    rlo=np.uint64(R&((1<<64)-1)); rhi=np.uint64(R>>64)
    ok=np.nonzero(((lo&rlo)==rlo)&((hi&rhi)==rhi))[0]
    for j in ok:
        a,b=masks[k],masks[j]
        pairs.add((min(a,b),max(a,b)))
print('covering pairs',len(pairs))
pickle.dump(sorted(pairs),open('pairs771.pkl','wb'))
# overlap sizes
from collections import Counter
print(Counter(bin(a&b).count('1') for a,b in pairs))
print(Counter((bin(a).count('1'),bin(b).count('1')) for a,b in pairs))
