# enumerate leftover sets E (|E|<=2, minimal) with Off_E(r0) subset Lambda(Va) u Lambda(Vb) u E
from e8cov import *
from e8cov import _bits
from cov import remove_cover
import itertools
r0i=0   # line index 0 is the root r0
ol=np.uint64(om&((1<<64)-1)); oh=np.uint64(om>>64)
rl=ol&~lo; rh=oh&~hi
cnt=popcnt(rl)+popcnt(rh)
idx=np.nonzero(cnt<=36+2)[0]
print('candidate Va',len(idx),flush=True)
found=set()
for k in idx:
    R=(int(rh[k])<<64)|int(rl[k])
    L=list(_bits(R))
    labs=[labE[i] for i in L]
    for sz in (0,1,2):
        for E in itertools.combinations(range(len(L)),sz):
            rest=[labs[i] for i in range(len(L)) if i not in E]
            if len(rref_basis(rest))<=7:
                found.add(tuple(sorted(L[i] for i in E)))
# minimal elements
fs=sorted(found,key=len)
mins=[]
for e in fs:
    if not any(set(m)<=set(e) for m in mins): mins.append(e)
print('minimal leftover sets:',len(mins))
from collections import Counter
print(Counter(len(m) for m in mins))
print('all contain r0 (index 0)?',all(0 in m for m in mins))
print('those without r0:',[m for m in mins if 0 not in m][:10])
print('E sets size1:',[m for m in mins if len(m)==1][:10])
