# symmetry check: number of 7-flat pairs covering N(r) is the same for other roots r; and E-lemma holds for them
from e8cov import masks, lo, hi, popcnt, labE, _bits, rref_basis
import numpy as np, itertools
from lib import *
import sys
for r in (17,77,119):
    Nl=[t for t in range(n) if t!=r and ip(lines[r],lines[t])!=0]
    Nm=sum(1<<t for t in Nl)
    nl=np.uint64(Nm&((1<<64)-1)); nh=np.uint64(Nm>>64)
    rl=nl&~lo; rh=nh&~hi
    cnt=popcnt(rl)+popcnt(rh)
    idx=np.nonzero(cnt<=36)[0]
    pairs=set()
    for k in idx:
        R=(int(rh[k])<<64)|int(rl[k])
        rlo=np.uint64(R&((1<<64)-1)); rhi=np.uint64(R>>64)
        ok=np.nonzero(((lo&rlo)==rlo)&((hi&rhi)==rhi))[0]
        for j in ok: pairs.add((min(masks[k],masks[j]),max(masks[k],masks[j])))
    # E-lemma for this root: all (Va, E) with |E|<=2 leftover rank<=7 of Off\Va\E contains r
    Off=Nm|(1<<r)
    ol=np.uint64(Off&((1<<64)-1)); oh=np.uint64(Off>>64)
    rl=ol&~lo; rh=oh&~hi
    cnt=popcnt(rl)+popcnt(rh)
    bad=0
    for k in np.nonzero(cnt<=38)[0]:
        R=(int(rh[k])<<64)|int(rl[k]); L=list(_bits(R)); labs=[labE[i] for i in L]
        for sz in (0,1,2):
            for E in itertools.combinations(range(len(L)),sz):
                if r in [L[i] for i in E]: continue
                rest=[labs[i] for i in range(len(L)) if i not in E]
                if len(rref_basis(rest))<=7: bad+=1
    print('root',r,'pairs',len(pairs),'E-lemma violations',bad,flush=True)
