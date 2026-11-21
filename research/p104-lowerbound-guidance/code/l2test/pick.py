from e8net import *
import random,pickle
A=np.array(list(itertools.product(range(-2,3),repeat=8)))
A=A[(A!=0).any(1)]; first=(A!=0).argmax(1); A=A[A[np.arange(len(A)),first]>0]
V=Ah@A.T; cand=[]
for i in range(A.shape[0]):
    D=np.nonzero(V[:,i])[0]
    if len(D)<8: continue
    bs=span([L[t] for t in D])
    if len(bs)==8:
        v=[x for x in range(1,512) if all(dot(x,y)==0 for y in bs)][0]; cand.append((tuple(A[i]),v))
print(len(cand)); pickle.dump(cand,open('cand.pkl','wb'))
rng=random.Random(1); best=None; seen=0
import math
idx=list(range(len(cand)))
for it in range(200000):
    S=rng.sample(idx,8); M=np.array([cand[i][0] for i in S])
    d=np.linalg.det(M)
    if abs(d)<0.5: continue
    B=np.linalg.inv(M).T      # rows beta_h with alpha_i . beta_j = delta
    dims=[]
    for h in range(8):
        sup=np.nonzero(np.abs(Ah@B[h])>1e-9)[0]
        dims.append(len(span([L[t] for t in sup])))
    seen+=1
    sc=sum(dims)
    if best is None or sc<best[0]: best=(sc,S,dims); print(best,flush=True)
    if sc==64: break
pickle.dump(best,open('best_pick.pkl','wb'))
