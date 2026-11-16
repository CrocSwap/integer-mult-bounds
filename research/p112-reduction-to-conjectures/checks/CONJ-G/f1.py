# F1: for every line v and every direction h in {c_t (t != v), f_j}: |Off(h) ∩ O_{l_v}| >= 5;
# also Off(c_v) ∩ O_{l_v} = {v} and N(v) := complement of O_{l_v} = Off(c_v) \ {v}.
import sys; sys.path.insert(0,'../K1-T2')
from base import *
dirs=[('c',t,C[t]) for t in range(n)]+[('f',j,[1 if i==j else 0 for i in range(8)]) for j in range(8)]
def Off(h): return {s for s in range(n) if sum(C[s][i]*h[i] for i in range(8))!=0}
offs=[(nm,i,Off(h)) for nm,i,h in dirs]
mn=99; arg=None
for v in range(n):
    Ov=set(O(L[v])); assert len(Ov)==60
    ocv=Off(C[v]); assert ocv & Ov == {v}, v
    assert set(range(n))-Ov == ocv-{v}
    for nm,i,S in offs:
        if nm=='c' and i==v: continue
        k=len(S & Ov)
        if k<mn: mn,arg=k,(v,nm,i)
print('F1 min |Off(h) ∩ O_{l_v}| over h != c_v:',mn,'at',arg)
assert mn>=5; print('F1 OK')
