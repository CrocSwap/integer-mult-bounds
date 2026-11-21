import numpy as np, collections, pickle
from ds_lib import *; from ds_rank import *; from s2_flats import e8_vectors
L=e8_lines(); P=halfspin(L); n=64; Q=Qmat(P); lab=Labels(Q)
X=e8_vectors()
D=(X@P.T)==0; packed=np.packbits(D,axis=1); _,ui=np.unique(packed,axis=0,return_index=True)
rec=[]
for i in ui:
    idx=np.nonzero(D[i])[0]
    if len(idx)<7 or np.linalg.matrix_rank(P[idx].astype(float))!=7: continue
    A=[j for j in range(n) if j not in set(idx.tolist())]
    s=lab.span(A)
    x=X[i]; g=np.gcd.reduce(np.abs(x)); 
    rec.append((len(idx),len(s),s,tuple(x)))
c=collections.Counter((a,b) for a,b,_,_ in rec)
print('flat size, complement span dim : count',sorted(c.items()))
good=[r for r in rec if r[1]==7]
pickle.dump({'good':good,'all_n':len(rec)},open('hs_good.pkl','wb'))
spans=collections.Counter(r[2] for r in good)
print('dim-7 spans:',len(spans),'flats per span',sorted(collections.Counter(spans.values()).items()))
# rank-6 pairs structure
S=list(spans); pr=collections.Counter()
for a in S:
    k=sum(1 for b in S if lab.pair_rank(a,b)==6); pr[k]+=1
print('per span: #partner spans with rank 6:',sorted(pr.items()))
