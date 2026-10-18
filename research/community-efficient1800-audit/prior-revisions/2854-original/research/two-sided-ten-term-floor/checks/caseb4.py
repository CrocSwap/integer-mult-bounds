import sys, itertools, os
sys.dont_write_bytecode=True
from enum9 import FCl, nonorth, v
import numpy as np
F=np.array(FCl,dtype=float)
sup=[frozenset(np.nonzero(F[t])[0]) for t in range(v)]
blocks=set(sup); print('#blocks',len(blocks),'S(3,4,8):',all(sum(1 for b in blocks if set(T)<=b)==1 for T in itertools.combinations(range(8),3)),flush=True)
root={tuple(F[t].astype(int)):t for t in range(v)}; root.update({tuple((-F[t]).astype(int)):t for t in range(v)})
pairs=list(itertools.combinations(range(v),2))
P1=np.array([F[a] for a,b in pairs]); P2=np.array([F[b] for a,b in pairs])
G11=(P1*P1).sum(1);G12=(P1*P2).sum(1);G22=(P2*P2).sum(1);DET=G11*G22-G12*G12
CACHE={}
def decomp(w):
    kk=tuple(w)
    if kk in CACHE: return CACHE[kk]
    r1=P1@w; r2=P2@w; ok=np.abs(DET)>1e-9; d=np.where(ok,DET,1)
    x1=(G22*r1-G12*r2)/d; x2=(G11*r2-G12*r1)/d
    res=np.abs(x1[:,None]*P1+x2[:,None]*P2-w).max(1)
    idx=np.nonzero(ok&(np.abs(x1)>1e-9)&(np.abs(x2)>1e-9)&(res<1e-9))[0]
    CACHE[kk]=[pairs[k] for k in idx]; return CACHE[kk]
st=dict(rows_ok=0,lin=0,lin_s2=0,full=0,full_s2=0)
CH=int(sys.argv[1]) if len(sys.argv)>1 else 0; NCH=int(sys.argv[2]) if len(sys.argv)>2 else 1   # chunk CH of NCH over the 70 column sets J
for ji,J in enumerate(itertools.combinations(range(8),4)):
    if ji%NCH!=CH: continue
    I=[c for c in range(8) if c not in J]
    for js in J:
        singles=[j for j in J if j!=js]
        cand=[[t for t in range(v) if F[t][j]!=0 and sup[t]<=set(I)|{j}] for j in singles]
        if any(not c for c in cand): continue
        for prod in itertools.product(*cand):
            A=np.zeros((8,8))
            for j,t in zip(singles,prod): A[:,j]+=F[t]/F[t][j]
            for wI in itertools.product((0,1,-1),repeat=4):
                vs=[]
                for i,wi in zip(I,wI):
                    row=np.eye(8)[i]-A[i]; row[js]-=wi
                    t=root.get(tuple(np.rint(row).astype(int))) if np.allclose(row,np.rint(row)) else None
                    if t is None: break
                    vs.append(t)
                else:
                    st['rows_ok']+=1
                    w=np.zeros(8); w[js]=1
                    for i,wi in zip(I,wI): w[i]=wi
                    for (t1,t2) in decomp(w):
                        us=list(prod)+[t1,t2]; s2=F[t1][js]!=0 and F[t2][js]!=0
                        st['lin']+=1; st['lin_s2']+=s2
                        if len(set(us))==5 and len(set(vs))==4 and all(nonorth(a,b) for a,b in itertools.combinations(us,2)) and all(nonorth(a,b) for a,b in itertools.combinations(vs,2)):
                            st['full']+=1; st['full_s2']+=s2
st={k:int(v) for k,v in st.items()}
print('chunk',CH,'of',NCH,st,flush=True)
