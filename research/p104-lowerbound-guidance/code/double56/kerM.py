import sys,json,numpy as np, itertools; sys.path.insert(0,'../orbitlp')
from geo import Q, D56
E=json.load(open(D56+'e8base.json')); R=np.array(E['C'])[:104]; Gb=np.array(E['Gb'])
print('Gb',Gb.tolist()); print('Gb sym',(Gb==Gb.T).all())
# constraint rows: for each Q-cell (t,s): sum_{ij} R_ti R_sj K_ij = 0 mod 4
cells=[(t,s) for t in range(104) for s in range(104) if Q[t,s]]
A=np.array([np.outer(R[t],R[s]).ravel()%4 for t,s in cells],dtype=np.int64)
# solve A k = 0 mod 4: enumerate via mod2 kernel then lift
def kernel2(A):
    A=A.copy()%2; r=0; piv=[]; n=A.shape[1]
    for c in range(n):
        p=next((i for i in range(r,len(A)) if A[i,c]),None)
        if p is None: continue
        A[[r,p]]=A[[p,r]]
        for i in range(len(A)):
            if i!=r and A[i,c]: A[i]^=A[r]
        piv.append(c); r+=1
    free=[c for c in range(n) if c not in piv]; out=[]
    for f in free:
        v=np.zeros(n,np.int64); v[f]=1
        for i,c in enumerate(piv): v[c]=A[i,f]
        out.append(v)
    return np.array(out)
K2=kernel2(A); print('mod2 kernel dim',len(K2))
# Z4 solutions: k = k0 + 2 k1 where k0 in K2-span, need A k0 /2 + A k1 = 0 mod 2 -> A k1 = A k0/2 mod 2 solvable?
# module structure: 2*(F2^64) solutions = 2*kernel2 ; lifts of K2 basis vectors
ok=[]
B=A%2
for v in K2:
    rhs=((A@v)%4)//2
    # solve B k1 = rhs mod 2
    M=np.concatenate([B,rhs[:,None]],1)%2
    M2=M.copy(); r=0; piv=[]
    for c in range(64):
        p=next((i for i in range(r,len(M2)) if M2[i,c]),None)
        if p is None: continue
        M2[[r,p]]=M2[[p,r]]
        for i in range(len(M2)):
            if i!=r and M2[i,c]: M2[i]^=M2[r]
        piv.append(c); r+=1
    cons=not M2[r:,64].any()
    ok.append(cons)
print('liftable basis vectors',sum(ok),'of',len(K2))
np.save('K2.npy',K2)
