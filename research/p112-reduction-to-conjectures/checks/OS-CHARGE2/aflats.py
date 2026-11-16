# all flats of the line arrangement (subspaces spanned by lines), by rank, as bitmasks; unit P112 or E8
import json, numpy as np, sys, pickle, time
D=json.load(open('data.json'))
unit=sys.argv[1]
FC=[list(map(int,r)) for r in D['FC']]
if unit=='E8':
    for i in range(8):
        e=[0]*8; e[i]=2; FC.append(e)
v=len(FC); X=np.array(FC,float)
def closure_mask(idx):
    B=X[idx]; Q,R=np.linalg.qr(B.T)
    r=int((np.abs(np.diag(R))>1e-9).sum()); Q=Q[:,:r] if r==len(idx) else np.linalg.svd(B)[2][:np.linalg.matrix_rank(B)].T
    res=X-(X@Q)@Q.T
    ok=np.nonzero((res*res).sum(1)<1e-9)[0]
    return sum(1<<int(t) for t in ok)
def basis_of(m):
    ts=[t for t in range(v) if m>>t&1]; B=[]
    for t in ts:
        if np.linalg.matrix_rank(X[B+[t]])>len(B): B.append(t)
    return B
levels={0:{0:[]}}
t0=time.time()
for r in range(1,8):
    nxt={}
    for m,B in levels[r-1].items():
        for t in range(v):
            if m>>t&1: continue
            nb=B+[t]; cm=closure_mask(nb)
            if cm not in nxt: nxt[cm]=nb
    levels[r]=nxt
    print(unit,'rank',r,'flats',len(nxt),'max lines',max(bin(x).count('1') for x in nxt),round(time.time()-t0),'s',flush=True)
pickle.dump({r:list(levels[r].keys()) for r in levels},open(f'aflats_{unit}.pkl','wb'))
