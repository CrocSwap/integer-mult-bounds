"""LINEAR56 lcore.py (own code). P104 in E8/2E8 coordinates."""
import json, numpy as np, itertools
D='<research-tree>/cards/WILD/LUNCH/exchange/d56dir/mod4/'
E=json.load(open(D+'e8base.json'))
C120=np.array(E['C'],dtype=np.int64); G=np.array(E['Gb'],dtype=np.int64)
LAB=[int(x) for x in open(D+'labels.txt').read().split()]
dot=lambda a,b: bin(a&b).count('1')&1
Q=np.array([[dot(a,b) for b in LAB] for a in LAB],dtype=np.int64)
X120=C120%2; Bm=G%2
def qf(x):  # E8 norm/2 mod 2 on F2^8 (well defined: x^T G x /2 with 0/1 lift)
    x=np.asarray(x,dtype=np.int64); return int((x@G@x)//2 %2)
def Bf(x,y): return int(np.asarray(x)@Bm@np.asarray(y)%2)
ALL=np.array(list(itertools.product([0,1],repeat=8)),dtype=np.int64)
def rref(M):
    M=(np.array(M)%2).astype(np.uint8); r=0; piv=[]
    for c in range(M.shape[1]):
        if r==M.shape[0]: break
        p=np.nonzero(M[r:,c])[0]
        if len(p)==0: continue
        p=p[0]+r; M[[r,p]]=M[[p,r]]
        nz=np.nonzero(M[:,c])[0]; nz=nz[nz!=r]; M[nz]^=M[r]
        piv.append(c); r+=1
    return M[:r],piv
def f2rank(M):
    M=np.array(M)
    if M.size==0: return 0
    return len(rref(M)[1])
def kernel(M):
    R,piv=rref(M); n=M.shape[1]; free=[c for c in range(n) if c not in piv]; out=[]
    for f in free:
        v=np.zeros(n,np.uint8); v[f]=1
        for i,c in enumerate(piv): v[c]=R[i,f]
        out.append(v)
    return np.array(out,dtype=np.int64).reshape(-1,n)
_R,_p=rref(np.concatenate([Bm,np.eye(8,dtype=np.int64)],1)); Binv=_R[:,8:].astype(np.int64)
C104=C120[:104]; Xb=X120[:104]; Z16=X120[104:]
def f_val(Ub,Vb):
    """f = dimU + dimV - rank <U,V> for row-bases over the 104 ports (F2 arrays)."""
    dU=f2rank(Ub); dV=f2rank(Vb)
    if dU==0 or dV==0: return dU+dV,dU,dV,0
    r=f2rank((np.array(Ub)@np.array(Vb).T)%2)
    return dU+dV-r,dU,dV,r
def UV(W,V):
    """U = span{a_k o Q_s : s in S_k}, V = span{b_k o Q_t : t in D_k}, supports mod 4 (as in ARF/TAU)."""
    W=W%4; V=V%4; a=W%2; b=V%2; Ug=[]; Vg=[]
    for k in range(W.shape[1]):
        S=np.nonzero(V[:,k])[0]; D=np.nonzero(W[:,k])[0]
        if a[:,k].any() and len(S): Ug.append((a[:,k][None,:]*Q[S])%2)
        if b[:,k].any() and len(D): Vg.append((b[:,k][None,:]*Q[D])%2)
    Ub=rref(np.concatenate(Ug))[0] if Ug else np.zeros((0,104),np.uint8)
    Vb=rref(np.concatenate(Vg))[0] if Vg else np.zeros((0,104),np.uint8)
    return Ub.astype(np.int64),Vb.astype(np.int64)
def check_decoder(W,V):
    return not ((((W%4)@(V%4).T-2*np.eye(104,dtype=np.int64))%4)*Q).any()
def cost(W,V):
    W=W%4; V=V%4; c=0
    for k in range(W.shape[1]):
        D=np.nonzero(W[:,k])[0]; S=np.nonzero(V[:,k])[0]
        if len(D) and len(S): c+=f2rank(Q[np.ix_(D,S)])
    return c
def solve2(A,b):
    """one solution of A x = b mod 2 or None"""
    M=np.concatenate([A%2,(b%2)[:,None]],1); R,piv=rref(M)
    if A.shape[1] in piv: return None
    x=np.zeros(A.shape[1],np.int64)
    for i,c in enumerate(piv): x[c]=R[i,-1]
    return x
