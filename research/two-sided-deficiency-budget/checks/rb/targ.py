import os
# targets Off(h) for the 1200 directions (E8 roots incl frame + norm-4 vectors), P112 lines
import json, numpy as np, itertools
D=json.load(open(os.environ.get('BX_DATA','../data/data.json'))); LAB=D['LAB']; L2=np.rint(np.array(D['L'])*2).astype(int)
E8=np.rint(np.array(D['E8'])*2).astype(int)
def n4():
    out=set()
    # norm-4 E8 vectors (x2 coords => norm 16): types (±2 at 4 coords... ) generate as sums of two orthogonal roots
    R=E8
    for i in range(len(R)):
        for j in range(len(R)):
            if R[i]@R[j]==0:
                for s in (1,-1):
                    v=R[i]+s*R[j]
                    v=tuple(v if next(c for c in v if c)>0 else -v)
                    out.add(v)
    return sorted(out)
H=[tuple(r) for r in E8]+n4()
def off(h): return frozenset(np.nonzero(L2@np.array(h))[0].tolist())
if __name__=='__main__':
    print(len(H)); from collections import Counter
    print(Counter(len(off(h)) for h in H))
